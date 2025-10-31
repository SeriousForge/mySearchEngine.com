# Jose X. Moreno 20387773
# Andrea Garza 20581964
# Leonardo Pérez 0444297
# Misael Garay 20522356

import os
from zipfile import ZipFile
from io import BytesIO
import re
import math
from queue import Queue
from posixpath import normpath, join as posixjoin

# Task 1: Build an indexer
class Node:
    def __init__(self, doc_id, position, frequency=1):
        self.doc_id = doc_id
        self.frequency = frequency
        self.position = [position]
        self.norm_tf_idf = 0.0
        self.next = None

class LinkedList:
    def __init__(self):
        self.head = None

    def update_list(self, doc_id, position):
        if self.head is None:
            self.head = Node(doc_id, position)
        else:
            current = self.head
            while current:
                if current.doc_id == doc_id:
                    current.frequency += 1
                    current.position.append(position)
                    return
                if current.next == None:
                    current.next = Node(doc_id, position)
                    return
                current = current.next
            
    def display(self):
        current = self.head
        while current:
            print(f"doc: {current.doc_id} frequency: {current.frequency} positions: {current.position}")
            current = current.next

    def list_doc_ids(self):
        current = self.head
        doc_ids = []
        while current:
            doc_ids.append(current.doc_id)
            current = current.next
        return doc_ids
    def id_positions(self, id):
        current = self.head
        while current:
            if current.doc_id == id:
                return current.position
            current = current.next
        return []
    
    def doc_freq(self):
        c, count = self.head, 0
        while c:
            count += 1
            c = c.next
        return count
    
DOC_LENGTHS = {}
HYPERLINKS = []
DOCUMENTS = {}

# Regular expression to find href links in HTML
HREF_RE = re.compile(r'<(?:a|area)\s[^>]*?href\s*=\s*([\'"])(.*?)\1', re.IGNORECASE | re.DOTALL)
SCRIPT_STYLE_RE = re.compile(r"(?is)<(script|style)\b.*?>.*?</\1>")
TAG_RE = re.compile(r"(?s)<[^>]+>")
TITLE_RE = re.compile(r"(?is)<title>(.*?)</title>")

def check_stopword(word):
    stopwords = [
        "a", 'able', 'about', 'above', 'according', 'accordingly', 'across', 'actually', 'after','afterwards', 'again', 'against', "ain",
        'all', 'allow', 'allows', 'almost', 'alone', 'along','already', 'also', 'although', 'always', 'am', 'among', 'amongst', 'an', 'and',
        'another','any', 'anybody', 'anyhow', 'anyone', 'anything', 'anyway', 'anyways', 'anywhere', 'apart','appear', 'appreciate', 'appropriate',
        'are', "aren", 'around', 'as', 'aside', 'ask', 'asking','associated', 'at', 'available', 'away', 'awfully', 'be', 'became', 'because',
        'become', 'becomes','becoming', 'been', 'before', 'beforehand', 'behind', 'being', 'believe', 'below', 'beside', 'besides','best', 'better',
        'between', 'beyond', 'both', 'brief', 'but', 'by', "c", "mon", 'came', "can",'cannot', 'cant', 'cause', 'causes', 'certain', 'certainly', 'changes',
        'clearly', 'co', 'com', 'come','comes', 'concerning', 'consequently', 'consider', 'considering', 'contain', 'containing', 'contains','corresponding',
        'could', "couldn", 'course', 'currently', 'definitely', 'described', 'despite', 'did',"didn", 'different', 'do', 'does', "doesn", 'doing', "don",
        'done', 'down', 'downwards', 'during', 'each','edu', 'eg', 'eight', 'either', 'else', 'elsewhere', 'enough', 'entirely', 'especially', 'et', 'etc',
        'even', 'ever', 'every', 'everybody', 'everyone', 'everything', 'everywhere', 'ex', 'exactly','example', 'except', 'far', 'few', 'fifth', 'first',
        'five', 'followed', 'following', 'follows','for', 'former', 'formerly', 'forth', 'four', 'from', 'further', 'furthermore', 'get', 'gets','getting',
        'given', 'gives', 'go', 'goes', 'going', 'gone', 'got', 'gotten', 'greetings', 'had', "hadn",'happens', 'hardly', 'has', "hasn", 'have', "haven",
        'having', 'he', 'hello', 'help', 'hence', 'her','here', 'hereafter', 'hereby', 'herein', 'hereupon', 'hers', 'herself', 'hi', 'him', 'himself', 'his',
        'hither', 'hopefully', 'how', 'howbeit', 'however', "i", 'ie', 'if', 'ignored', 'immediate', 'in','inasmuch', 'inc', 'indeed', 'indicate', 'indicated',
        'indicates', 'inner', 'insofar', 'instead', 'into','inward', 'is', "isn", 'it', 'its', 'itself', 'just', 'keep', 'keeps', 'kept', 'know', 'known',
        'knows','last', 'lately', 'later', 'latter', 'latterly', 'least', 'less', 'lest', 'let', 'like', 'liked', 'likely','little', 'look', 'looking', 'looks',
        'ltd', 'mainly', 'many', 'may', 'maybe', 'me', 'mean', 'meanwhile','merely', 'might', 'more', 'moreover', 'most', 'mostly', 'much', 'must', 'my', 'myself',
        'name', 'namely','nd', 'near', 'nearly', 'necessary', 'need', 'needs', 'neither', 'never', 'nevertheless', 'new', 'next','nine', 'no', 'nobody', 'non',
        'none', 'noone', 'nor', 'normally', 'not', 'nothing', 'novel', 'now', 'nowhere','obviously', 'of', 'off', 'often', 'oh', 'ok', 'okay', 'old', 'on', 'once',
        'one', 'ones', 'only', 'onto', 'or','other', 'others', 'otherwise', 'ought', 'our', 'ours', 'ourselves', 'out', 'outside', 'over', 'overall', 'own','particular',
        'particularly', 'per', 'perhaps', 'placed', 'please', 'plus', 'possible', 'presumably', 'probably','provides', 'que', 'quite', 'qv', 'rather', 'rd', 're',
        'really', 'reasonably', 'regarding', 'regardless', 'regards','relatively', 'respectively', 'right', 'said', 'same', 'saw', 'say', 'saying', 'says', 'second',
        'secondly', 'see', 'seeing','seem', 'seemed', 'seeming', 'seems', 'seen', 'self', 'selves', 'sensible', 'sent', 'serious', 'seriously', 'seven', 'several',
        'shall', 'she', 'should', "shouldn", 'since', 'six', 'so', 'some', 'somebody', 'somehow', 'someone', 'something', 'sometime','sometimes', 'somewhat',
        'somewhere', 'soon', 'sorry', 'specified', 'specify', 'specifying', 'still', 'sub', 'such', 'sup','sure', "s", "t", 'take', 'taken', 'tell', 'tends', 'th',
        'than', 'thank', 'thanks', 'thanx', 'that', 'thats', 'the', 'their','theirs', 'them', 'themselves', 'then', 'thence', 'there', 'thereafter', 'thereby',
        'therefore', 'therein', 'theres', 'thereupon','these', 'they', "ll", "ve", 'think', 'third', 'this', 'thorough', 'thoroughly', 'those', 'though', 'three',
        'through', 'throughout','thru', 'thus', 'to', 'together', 'too', 'took', 'toward', 'towards', 'tried', 'tries', 'truly', 'try', 'trying', 'twice', 'two',
        'un', 'under', 'unfortunately', 'unless', 'unlikely', 'until', 'unto', 'up', 'upon', 'us', 'use', 'used', 'useful', 'uses','using', 'usually', 'value',
        'various', 'very', 'via', 'viz', 'vs', 'want', 'wants', 'was', 'way', 'we', "d", 'welcome', 'well','went', 'were', "weren", 'what', 'whatever', 'when',
        'whence', 'whenever', 'where', 'whereafter', 'whereas', 'whereby', 'wherein','whereupon', 'wherever', 'whether', 'which', 'while', 'whither', 'who',
        'whoever', 'whole', 'whom', 'whose', 'why', 'will','willing', 'wish', 'with', 'within', 'without', "won", 'wonder', 'would', "wouldn", 'yes', 'yet',
        'you', 'your', 'yours','yourself', 'yourselves', 'zero']
    
    if word in stopwords:
        return True
    return False

def extract_words_from_html(text):
    text = SCRIPT_STYLE_RE.sub(" ", text)
    text = TAG_RE.sub(" ", text)

    words = []
    current_word = []

    for char in text:
        if char.isalpha():
            current_word.append(char)
        else:
            if current_word:
                words.append(''.join(current_word))
                current_word = []
    
    if current_word:
        words.append(''.join(current_word))

    return [w.lower() for w in words if not check_stopword(w.lower())]

def extract_links_from_html(text):
    return [m[1].strip() for m in HREF_RE.findall(text)]

# Tokenizes a query string into lowercase words, ignoring non-alphabetic characters
QUERY_RE = re.compile(r"[A-Za-z]+")
def tokenize_query(text: str):
    tokens = [w.lower() for w in QUERY_RE.findall(text)]
    return tokens

# Given an index dictionary, returns a dictionary w/ the doc frequencies for each term
def compute_doc_freqs(index_dict):
    return {term: postings.doc_freq() for term, postings in index_dict.items()}

# Computes the normalized tf-idf weights for each term/doc
def compute_norm_tf_idf(index_dict, doc_lengths, doc_freqs, num_docs):

    # Compute raw tf-idf
    doc_norm_squares = {}
    for term, postings in index_dict.items():
        # idf = log((N + 1) / df) + 1
        df = max(1, doc_freqs.get(term, 1))
        idf = math.log((num_docs + 1) / df) + 1.0

        current = postings.head
        while current:
            tf = (current.frequency / max(1, doc_lengths.get(current.doc_id, 1)))
            weight = tf * idf

            doc_norm_squares[current.doc_id] = doc_norm_squares.get(current.doc_id, 0.0) + (weight * weight)
            current._raw_w = weight

            current = current.next

    # Normalize tf-idf
    for term, postings in index_dict.items():
        current = postings.head
        while current:
            denominator = math.sqrt(doc_norm_squares.get(current.doc_id, 1.0))
            
            if denominator > 0:
                current.norm_tf_idf = (current._raw_w / denominator)
            else:
                current.norm_tf_idf = 0.0

            del current._raw_w
            current = current.next

# Extracts all of the information from a folder, file by file
# Separates the info into tokens, removes any tokens that include non alphabet chars, returns all valid tokens
# Gives an error if the folder isn't found
def extract_words_from_files(directory_path):
    word_frequency = {}
    doc_id_to_file = {}
    i = 0
    pos = 0
    try:
        for file_name in os.listdir(directory_path):
            full_path = os.path.join(directory_path, file_name)
            if os.path.isfile(full_path):
                doc_id_to_file[i] = file_name
                try:
                    with open(full_path, 'r') as f:
                        
                        file_info = f.read()
                        title_match = TITLE_RE.search(file_info)
                        title = title_match.group(1).strip() if title_match else None

                        links = extract_links_from_html(file_info)
                        pos = 0
        
                        for term in extract_words_from_html(file_info):
                            word = term.lower()
                            if not check_stopword(word):
                                if word not in word_frequency:
                                    word_frequency[word] = LinkedList()
                                word_frequency[word].update_list(i, pos)
                                pos += 1
                        DOC_LENGTHS[i] = pos
                        DOCUMENTS[i] = {"file": file_name, "length": pos, "title" : title}
                        HYPERLINKS.append({"doc_id": i, "file": file_name, "links": links, "status": "unvisited"})
                        i += 1
                except Exception as e:
                    print(f"Error reading file {file_name}")
    except FileNotFoundError:
        print("Directory not found")
    except Exception:
        print("Error occurred")
    return word_frequency, doc_id_to_file

def extract_from_zip(zip_path):
    word_frequency = {}
    doc_id_to_file = {}
    i = 0
    pos = 0
    try:
        with ZipFile(zip_path, 'r') as zip_archive:
            files = zip_archive.namelist()
            for file_name in files:
                with zip_archive.open(file_name) as file_in_zip:
                    doc_id_to_file[i] = file_name
                    
                    file_info_undecoded = file_in_zip.read()
                    file_info = file_info_undecoded.decode('utf-8')

                    title_match = TITLE_RE.search(file_info)
                    title = title_match.group(1).strip() if title_match else None

                    links = extract_links_from_html(file_info)
                    pos = 0

                    for term in extract_words_from_html(file_info):
                        word = term.lower()
                        if not check_stopword(word):
                            if word not in word_frequency:
                                word_frequency[word] = LinkedList()
                            word_frequency[word].update_list(i, pos)
                            pos += 1
                    DOC_LENGTHS[i] = pos
                    DOCUMENTS[i] = {"file": file_name, "length": pos, "title" : title}
                    HYPERLINKS.append({"doc_id": i, "file": file_name, "links": links, "status": "unvisited"})
                    i += 1
    except FileNotFoundError:
        print("Directory not found")
    except Exception:
        print("Error occurred")
    return word_frequency, doc_id_to_file



#helper function for spidering
#Resolves a link relative to the current file's directory.
#It makes sure that the correct file path is used to open it
#posixjoin handles knowing how to combine the link
#normpath removes stuff like // and anything that would make it not work as intended
def resolve_path(current_file, link):
    
    current_dir = os.path.dirname(current_file)
    if current_dir:
        resolved = posixjoin(current_dir, link)
    else:
        resolved = link
    normalized = normpath(resolved)
    return normalized

# this will handle spidering
# the links are the anchors
###########
############
#############
##############
def spiderIndex(zip_path, start_file):
    word_frequency = {}
    doc_id_to_file = {}
    i = 0
    pos = 0
    visit = Queue()
    visited = []
    #pathhelp will help when opening the start_file, it gives it the zip_path/
    pathhelp = ""
    for char in zip_path:
        if char != ".":
            pathhelp += char
        else:
            pathhelp += "/"
            break
    z = 0 #counts how many total files it looked at
    try:
        with ZipFile(zip_path, 'r') as zip_archive: #opens the zip_path
            
            start_path = pathhelp + start_file
            visit.put(start_path)
            #as long as visit isn't empty, keep on looping
            while(not visit.empty()):

                fname = visit.get()
                print(f"{i}  and file: {fname}")
                z += 1
                if fname in visited:
                    continue
                if not fname.endswith(('.html', '.htm')): #ignore non html, htm, add to visited to prevent adding again
                    print(f"skipping non-HTML file: {fname}")
                    visited.append(fname)
                    continue
                print(f"visited: {fname}")
                visited.append(fname)
                
                
                #mostly the same as in extract from zip, except at the end it adds unvisited links to visit
                try:
                    with zip_archive.open(fname) as fiz:
                    
                        file_info_undecoded = fiz.read()
                        try:
                            file_info = file_info_undecoded.decode('utf-8')
                        except UnicodeDecodeError:
                            file_info = file_info_undecoded.decode('latin-1')
                        
                        doc_id_to_file[i] = fname
                        tmatch = TITLE_RE.search(file_info)
                        title2 = tmatch.group(1).strip() if tmatch else None
                        links = extract_links_from_html(file_info)
                        pos = 0
                        for term in extract_words_from_html(file_info):
                            word = term.lower()
                            if not check_stopword(word):
                                if word not in word_frequency:
                                    word_frequency[word] = LinkedList()
                                word_frequency[word].update_list(i, pos)
                                pos += 1
                        DOC_LENGTHS[i] = pos
                        DOCUMENTS[i] = {"file": fname, "length": pos, "title" : title2}
                        HYPERLINKS.append({"doc_id": i, "file": fname, "links": links, "status": "unvisited"})
                        for link in links:
                            resolved_link = resolve_path(fname, link)
                            if resolved_link not in visited:
                                visit.put(resolved_link)
                            
                                
                        i+=1
                except Exception:
                    print(f"skipped: {fname}")    
            print(f"z: {z}")
            
    except FileNotFoundError:
        print("Directory not found")
    except Exception as e:
        print(f"Error occurred: {e}")
    return word_frequency, doc_id_to_file


# Looks for where the script is and changes to its directory before extracting from folder Jan
script_dir = os.path.dirname(os.path.realpath(__file__))
os.chdir(script_dir)
all_file_data, doc_id_to_file = extract_from_zip("Jan.zip")

# Computes the doc frequencies and normalized tf-idf weights
DOC_FREQS = compute_doc_freqs(all_file_data)
compute_norm_tf_idf(
    index_dict = all_file_data,
    doc_lengths = DOC_LENGTHS,
    doc_freqs = DOC_FREQS,
    num_docs = len(doc_id_to_file)
)

# Extracts data into its appropriate files

file_path = 'Extract_List.txt'
with open(file_path, 'w') as output_file:
    for word, linked_list in all_file_data.items():
        output_file.write(f"{word}:\n")
        current = linked_list.head
        while current:
            output_file.write(f"doc: {current.doc_id} frequency: {current.frequency}\n")
            current = current.next
        output_file.write("\n")

tf_idf_path = "TFIDF_List.txt"
with open(tf_idf_path, "w") as output_file:
    for term in sorted(all_file_data.keys()):
        postings = all_file_data[term]
        output_file.write(f"{term} (df={DOC_FREQS.get(term, 0)}):\n")
        current = postings.head
        while current:
            output_file.write(
                f"doc:{current.doc_id}  tf:{current.frequency}  "
                f"len:{DOC_LENGTHS.get(current.doc_id, 0)}  "
                f"norm_tf_idf:{current.norm_tf_idf:.6f}  "
                f"positions:{current.position}\n"
            )
            current = current.next
        output_file.write("\n")

hyperlinks_path = "Hyperlinks_Report.txt"
with open(hyperlinks_path, "w", encoding="utf-8") as output_file:
    if not HYPERLINKS:
        output_file.write("(no hyperlinks found)\n")
    else:
        for entry in HYPERLINKS:
            seen = set()
            links = []
            for u in entry["links"]:
                if u not in seen:
                    seen.add(u)
                    links.append(u)

            output_file.write(f"Doc {entry['doc_id']} — {entry['file']}  (status: {entry['status']})\n")
            if not links:
                output_file.write("  (no links)\n\n")
            else:
                for u in links:
                    output_file.write(f"  - {u}\n")
                output_file.write("\n")

# Task 3: Build a query searcher
def rank_documents(query_words, current_result, word_frequency):
    scores = {}
    N = len(doc_id_to_file)

    query_vec = {}
    for word in query_words:
        if word in word_frequency:
            df = len(word_frequency[word].list_doc_ids())
            idf = math.log((N + 1) / (df + 1)) + 1  
            tf = query_words.count(word)
            query_vec[word] = (1 + math.log(tf)) * idf

    for doc_id in current_result:
        dot_product = 0.0
        query_norm = math.sqrt(sum(v ** 2 for v in query_vec.values()))

        for word, q_weight in query_vec.items():
            node = word_frequency[word].head
            while node:
                if node.doc_id == doc_id:
                    dot_product += q_weight * node.norm_tf_idf
                    break
                node = node.next

        scores[doc_id] = dot_product / max(query_norm, 1e-9)  

    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return ranked

# Creates a loop that allows the user to search for words
# If the word is found, it prints the names of the files containing that word
# If not found, it displays a "No match" message to the user

# It keeps track of 3 modes: or, and, and but. These modes help with boolean queries
# If it finds either word in the search, it turns on the respective mode
# If a mode is on, it will perform the boolean query with the current list and the next word that follows
# For and, it only keeps doc_ids that match both sides. for but, it removes from the left any doc_ids that appear in the right

def search_loop(word_frequency, doc_id_to_file):
    while True:
        search_key = input("Enter a word to search: ").strip().lower()
        or_mode = False
        and_mode = False
        but_mode = False
        lefthandside = []
        righthandside = []

        if search_key == '':
            print("Exiting the search...")
            break
        
        querie_words = tokenize_query(search_key)
        has_boolean = any(word in ["or", "and", "but"] for word in querie_words)

        if search_key[0] == '"' and search_key.endswith('"'):
            lefthandside = phrasal_search(word_frequency, querie_words)

        # Boolean retrieval
        elif has_boolean:
            for search_word in querie_words:
                if or_mode:
                    or_mode = False
                    if search_word in word_frequency:
                        for id in word_frequency[search_word].list_doc_ids():
                            if id not in lefthandside:
                                lefthandside.append(id)

                elif and_mode:
                    and_mode = False
                    leftandright = []
                    if search_word in word_frequency:
                        for id in word_frequency[search_word].list_doc_ids():
                            if id not in righthandside:
                                righthandside.append(id)
                        for left_doc_id in lefthandside:
                            for right_doc_id in righthandside:
                                if left_doc_id == right_doc_id and left_doc_id not in leftandright:
                                    leftandright.append(left_doc_id)
                        lefthandside = []
                        righthandside = []
                        for accepted_ids in leftandright:
                            lefthandside.append(accepted_ids)
                    else:
                        lefthandside = []

                elif but_mode:
                    but_mode = False
                    if search_word in word_frequency:
                        for id in word_frequency[search_word].list_doc_ids():
                            if id not in righthandside:
                                righthandside.append(id)
                    to_remove = set(righthandside)
                    lefthandside = [id for id in lefthandside if id not in to_remove]
                    righthandside = []
                                
                elif search_word == "or":
                    or_mode = True
                elif search_word == "and":
                    and_mode = True
                elif search_word == "but":
                    but_mode = True
            
                elif search_word in word_frequency:
                    for id in word_frequency[search_word].list_doc_ids():
                        if id not in lefthandside:
                            lefthandside.append(id)

        else:
            # Vector Space retrieval
            all_docs = list(doc_id_to_file.keys())
            ranked_docs = rank_documents(querie_words, all_docs, word_frequency)
            ranked_docs = [(doc_id, score) for doc_id, score in ranked_docs if score > 0.0]

            if ranked_docs:
                print("Vector space results (cosine):")
                for doc_id, score in ranked_docs:
                    print(f"  {doc_id_to_file[doc_id]}  (score: {score:.6f})")
            else:
                print("No match found")
            continue
        
        if lefthandside:
            # Boolean and phrasal ranking results 
            ranked_docs = rank_documents(querie_words, lefthandside, word_frequency)
            ranked_docs = [(doc_id, score) for doc_id, score in ranked_docs if score > 0.0]

            print("Found a match! Ranked results:")
            if ranked_docs:
                for doc_id, score in ranked_docs:
                    file_name = doc_id_to_file[doc_id]
                    print(f"  {file_name}  (score: {score:.6f})")
            else:
                print("No match found")
        else:
            print("No match found")

# Task 4: Phrasal Search
def phrasal_search(word_frequency, query_words):
    indexes = {}
    lefthandside = []
    righthandside = []

    # Go through the words in the query, it ignores stop words
    # If the word is missing from word_frequency return [] since phrase doesn't match
    # It first adds all of the ids from the first word, then it filters out ids by removing any doc_ids that don't have all the words
    # If at any point it removes all ids, it returns []
    for search_word in query_words:
        if not check_stopword(search_word):
            if search_word not in word_frequency:
                return []
            elif not lefthandside:
                for id in word_frequency[search_word].list_doc_ids():
                    if id not in lefthandside:
                        lefthandside.append(id)
                        indexes[id] = word_frequency[search_word].id_positions(id)[:]
            else:
                leftandright = []
                for id in word_frequency[search_word].list_doc_ids():
                    if id not in righthandside:
                        righthandside.append(id)
                for left_doc_id in lefthandside:
                    for right_doc_id in righthandside:
                        if left_doc_id == right_doc_id and left_doc_id not in leftandright:
                            leftandright.append(left_doc_id)
                lefthandside = []
                righthandside = []
                if leftandright:
                    for accepted_ids in leftandright:
                        lefthandside.append(accepted_ids)
                else:
                    return []
                
    # 'i' helps keep track of the positions of the words in the phrase
    # Goes through query words and checks to see if it matches the position in the phrase (position in indexes[id]+i)
    # If it isn't in position, it removes the position in indexes
    # Ignores stop words
    i = 0
    for search_word in query_words:
        if not check_stopword(search_word):
            for id in lefthandside:
                    positions = set(word_frequency[search_word].id_positions(id))
                    indexes[id] = [p for p in indexes[id] if (p + i) in positions]
            i += 1

    # If indexes[id] is empty it removes the id from lefthandside since that means it didn't match the phrase
    lefthandside = [id for id in lefthandside if indexes.get(id)]
    return lefthandside
def build_index(zip_path):
    """
    Build the search index from a zip file.
    Returns word_frequency and doc_id_to_file dictionaries.
    """
    # Clear global containers in case this is called multiple times
    global DOC_LENGTHS, HYPERLINKS, DOCUMENTS, DOC_FREQS
    DOC_LENGTHS = {}
    HYPERLINKS = []
    DOCUMENTS = {}
    
    # Extract data from zip file
    word_frequency, doc_id_to_file = spiderIndex(zip_path, "index.html")
    
    # Compute document frequencies and tf-idf weights
    doc_freqs = compute_doc_freqs(word_frequency)
    compute_norm_tf_idf(
        index_dict=word_frequency,
        doc_lengths=DOC_LENGTHS,
        doc_freqs=doc_freqs,
        num_docs=len(doc_id_to_file)
    )
    
    # Store doc_freqs globally for use in ranking
    DOC_FREQS = doc_freqs
    
    return word_frequency, doc_id_to_file


#search_loop(all_file_data, doc_id_to_file)

def search_loop_equiv(search_key, word_frequency, doc_id_to_file):
    search_key = search_key.strip().lower()
    or_mode = False
    and_mode = False
    but_mode = False
    lefthandside = []
    righthandside = []

    querie_words = tokenize_query(search_key)
    has_boolean = any(word in ["or", "and", "but"] for word in querie_words)

    # Phrasal search
    if search_key.startswith('"') and search_key.endswith('"'):
        lefthandside = phrasal_search(word_frequency, querie_words)
        
        # Rank phrasal search results
        results = []
        if lefthandside:
            ranked_docs = rank_documents(querie_words, lefthandside, word_frequency)
            ranked_docs = [(doc_id, score) for doc_id, score in ranked_docs if score > 0.0]
            
            for doc_id, score in ranked_docs:
                file_name = doc_id_to_file[doc_id]
                results.append({
                    "file": file_name,
                    "score": round(score, 6)
                })
        return results

    # Boolean retrieval
    elif has_boolean:
        for search_word in querie_words:
            if or_mode:
                or_mode = False
                if search_word in word_frequency:
                    for id in word_frequency[search_word].list_doc_ids():
                        if id not in lefthandside:
                            lefthandside.append(id)

            elif and_mode:
                and_mode = False
                leftandright = []
                if search_word in word_frequency:
                    for id in word_frequency[search_word].list_doc_ids():
                        if id not in righthandside:
                            righthandside.append(id)
                    for left_doc_id in lefthandside:
                        for right_doc_id in righthandside:
                            if left_doc_id == right_doc_id and left_doc_id not in leftandright:
                                leftandright.append(left_doc_id)
                    lefthandside = leftandright
                    righthandside = []
                else:
                    lefthandside = []

            elif but_mode:
                but_mode = False
                if search_word in word_frequency:
                    for id in word_frequency[search_word].list_doc_ids():
                        if id not in righthandside:
                            righthandside.append(id)
                to_remove = set(righthandside)
                lefthandside = [id for id in lefthandside if id not in to_remove]
                righthandside = []
                        
            elif search_word == "or":
                or_mode = True
            elif search_word == "and":
                and_mode = True
            elif search_word == "but":
                but_mode = True
        
            elif search_word in word_frequency:
                for id in word_frequency[search_word].list_doc_ids():
                    if id not in lefthandside:
                        lefthandside.append(id)

        # Rank boolean search results
        results = []
        if lefthandside:
            ranked_docs = rank_documents(querie_words, lefthandside, word_frequency)
            ranked_docs = [(doc_id, score) for doc_id, score in ranked_docs if score > 0.0]
            
            for doc_id, score in ranked_docs:
                file_name = doc_id_to_file[doc_id]
                results.append({
                    "file": file_name,
                    "score": round(score, 6)
                })
        return results

    else:
        # Vector Space retrieval (no boolean operators)
        all_docs = list(doc_id_to_file.keys())
        ranked_docs = rank_documents(querie_words, all_docs, word_frequency)
        ranked_docs = [(doc_id, score) for doc_id, score in ranked_docs if score > 0.0]

        results = []
        for doc_id, score in ranked_docs:
            file_name = doc_id_to_file[doc_id]
            results.append({
                "file": file_name,
                "score": round(score, 6)
            })
        return results
