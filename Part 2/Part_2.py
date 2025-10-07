# Jose X. Moreno 20387773
# Andrea Garza 20581964
# Leonardo Pérez 0444297
# Misael Garay 20522356

import os
from zipfile import ZipFile
from io import BytesIO
class Node:
    def __init__(self, doc_id, position, frequency=1):
        self.doc_id = doc_id
        self.frequency = frequency
        self.position = [position]
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
    
#returns true if the word is a stopword, false otherwise
def check_stopword(word):
    stopwords = ["a", 'able', 'about', 'above', 'according', 'accordingly', 'across', 'actually', 'after', 'afterwards', 'again', 'against', "ain", 'all', 'allow', 'allows', 'almost', 'alone', 'along', 'already', 'also', 'although', 'always', 'am', 'among', 'amongst', 'an', 'and', 'another', 'any', 'anybody', 'anyhow', 'anyone', 'anything', 'anyway', 'anyways', 'anywhere', 'apart', 'appear', 'appreciate', 'appropriate', 'are', "aren", 'around', 'as', 'aside', 'ask', 'asking', 'associated', 'at', 'available', 'away', 'awfully', 'be', 'became', 'because', 'become', 'becomes', 'becoming', 'been', 'before', 'beforehand', 'behind', 'being', 'believe', 'below', 'beside', 'besides', 'best', 'better', 'between', 'beyond', 'both', 'brief', 'but', 'by', "c", "mon", 'came', "can", 'cannot', 'cant', 'cause', 'causes', 'certain', 'certainly', 'changes', 'clearly', 'co', 'com', 'come', 'comes', 'concerning', 'consequently', 'consider', 'considering', 'contain', 'containing', 'contains', 'corresponding', 'could', "couldn", 'course', 'currently', 'definitely', 'described', 'despite', 'did', "didn", 'different', 'do', 'does', "doesn", 'doing', "don", 'done', 'down', 'downwards', 'during', 'each', 'edu', 'eg', 'eight', 'either', 'else', 'elsewhere', 'enough', 'entirely', 'especially', 'et', 'etc', 'even', 'ever', 'every', 'everybody', 'everyone', 'everything', 'everywhere', 'ex', 'exactly', 'example', 'except', 'far', 'few', 'fifth', 'first', 'five', 'followed', 'following', 'follows', 'for', 'former', 'formerly', 'forth', 'four', 'from', 'further', 'furthermore', 'get', 'gets', 'getting', 'given', 'gives', 'go', 'goes', 'going', 'gone', 'got', 'gotten', 'greetings', 'had', "hadn", 'happens', 'hardly', 'has', "hasn", 'have', "haven", 'having', 'he', 'hello', 'help', 'hence', 'her', 'here', 'hereafter', 'hereby', 'herein', 'hereupon', 'hers', 'herself', 'hi', 'him', 'himself', 'his', 'hither', 'hopefully', 'how', 'howbeit', 'however', "i", 'ie', 'if', 'ignored', 'immediate', 'in', 'inasmuch', 'inc', 'indeed', 'indicate', 'indicated', 'indicates', 'inner', 'insofar', 'instead', 'into', 'inward', 'is', "isn", 'it', 'its', 'itself', 'just', 'keep', 'keeps', 'kept', 'know', 'known', 'knows', 'last', 'lately', 'later', 'latter', 'latterly', 'least', 'less', 'lest', 'let', 'like', 'liked', 'likely', 'little', 'look', 'looking', 'looks', 'ltd', 'mainly', 'many', 'may', 'maybe', 'me', 'mean', 'meanwhile', 'merely', 'might', 'more', 'moreover', 'most', 'mostly', 'much', 'must', 'my', 'myself', 'name', 'namely', 'nd', 'near', 'nearly', 'necessary', 'need', 'needs', 'neither', 'never', 'nevertheless', 'new', 'next', 'nine', 'no', 'nobody', 'non', 'none', 'noone', 'nor', 'normally', 'not', 'nothing', 'novel', 'now', 'nowhere', 'obviously', 'of', 'off', 'often', 'oh', 'ok', 'okay', 'old', 'on', 'once', 'one', 'ones', 'only', 'onto', 'or', 'other', 'others', 'otherwise', 'ought', 'our', 'ours', 'ourselves', 'out', 'outside', 'over', 'overall', 'own', 'particular', 'particularly', 'per', 'perhaps', 'placed', 'please', 'plus', 'possible', 'presumably', 'probably', 'provides', 'que', 'quite', 'qv', 'rather', 'rd', 're', 'really', 'reasonably', 'regarding', 'regardless', 'regards', 'relatively', 'respectively', 'right', 'said', 'same', 'saw', 'say', 'saying', 'says', 'second', 'secondly', 'see', 'seeing', 'seem', 'seemed', 'seeming', 'seems', 'seen', 'self', 'selves', 'sensible', 'sent', 'serious', 'seriously', 'seven', 'several', 'shall', 'she', 'should', "shouldn", 'since', 'six', 'so', 'some', 'somebody', 'somehow', 'someone', 'something', 'sometime', 'sometimes', 'somewhat', 'somewhere', 'soon', 'sorry', 'specified', 'specify', 'specifying', 'still', 'sub', 'such', 'sup', 'sure', "s", "t", 'take', 'taken', 'tell', 'tends', 'th', 'than', 'thank', 'thanks', 'thanx', 'that', 'thats', 'the', 'their', 'theirs', 'them', 'themselves', 'then', 'thence', 'there', 'thereafter', 'thereby', 'therefore', 'therein', 'theres', 'thereupon', 'these', 'they', "ll", "ve", 'think', 'third', 'this', 'thorough', 'thoroughly', 'those', 'though', 'three', 'through', 'throughout', 'thru', 'thus', 'to', 'together', 'too', 'took', 'toward', 'towards', 'tried', 'tries', 'truly', 'try', 'trying', 'twice', 'two', 'un', 'under', 'unfortunately', 'unless', 'unlikely', 'until', 'unto', 'up', 'upon', 'us', 'use', 'used', 'useful', 'uses', 'using', 'usually', 'value', 'various', 'very', 'via', 'viz', 'vs', 'want', 'wants', 'was', 'way', 'we', "d", 'welcome', 'well', 'went', 'were', "weren", 'what', 'whatever', 'when', 'whence', 'whenever', 'where', 'whereafter', 'whereas', 'whereby', 'wherein', 'whereupon', 'wherever', 'whether', 'which', 'while', 'whither', 'who', 'whoever', 'whole', 'whom', 'whose', 'why', 'will', 'willing', 'wish', 'with', 'within', 'without', "won", 'wonder', 'would', "wouldn", 'yes', 'yet', 'you', 'your', 'yours', 'yourself', 'yourselves', 'zero']
    if word in stopwords:
        return True
    return False
def extract_words_from_html(text):
    words = []
    current_word = []
    in_tag = False

    # Iterate through each character in the text
    for char in text:
        # Start of HTML tag
        if char == '<':
            in_tag = True
            if current_word:
                words.append(''.join(current_word))
                current_word = []
        # End of HTML tag
        elif char == '>':
            in_tag = False
        # Outside of HTML tags
        elif not in_tag:
            if char.isalpha():
                current_word.append(char)
            else:
                if current_word:
                    words.append(''.join(current_word))
                    current_word = []
    # Add the last word to the list if exists
    if current_word:
        words.append(''.join(current_word))

    return words

# Task 1 
#extracts all of the information from a folder, file by file
#separates the info into tokens, removes any tokens that include non alphabet chars, returns all valid tokens
#gives an error if the folder isn't found
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
                        pos = 0
        
                        for term in extract_words_from_html(file_info):
                            word = term.lower()
                            if not check_stopword(word):
                                if word not in word_frequency:
                                    word_frequency[word] = LinkedList()
                                word_frequency[word].update_list(i, pos)
                                pos += 1
                        i += 1
                except Exception as e:
                    print(f"Error reading file {file_name}")
    except FileNotFoundError:
        print("Directory not found")
    except Exception:
        print("Error occurred")
    return word_frequency, doc_id_to_file

#same as above except for zip folder
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
                    pos = 0

                    for term in extract_words_from_html(file_info):
                        word = term.lower()
                        if not check_stopword(word):
                            if word not in word_frequency:
                                word_frequency[word] = LinkedList()
                            word_frequency[word].update_list(i, pos)
                            pos += 1
                    i += 1
    except FileNotFoundError:
        print("Directory not found")
    except Exception:
        print("Error occurred")
    return word_frequency, doc_id_to_file

file_path = 'Extract_List.txt'


#looks for where the script is and changes to its directory before extracting from folder Jan
script_dir = os.path.dirname(os.path.realpath(__file__))
os.chdir(script_dir)
all_file_data, doc_id_to_file = extract_from_zip("Jan.zip")


# Writes extracted data into Extract_List.txt
with open(file_path, 'w') as output_file:
    for word, linked_list in all_file_data.items():
        output_file.write(f"{word}:\n")
        current = linked_list.head
        while current:
            output_file.write(f"doc: {current.doc_id} frequency: {current.frequency}\n")
            current = current.next
        output_file.write("\n")

print(f"Web Searchers Part 1 \n\nTask 1:\n{file_path} completed\n")


# Task 2
# Creates a loop that allows the user to search for words
# If the word is found, it prints the names of the files containing that word
# If not found, it displays a "No match" message to the user
def search_loop(word_frequency, doc_id_to_file):
    print("Task 2:")
    while True:
        search_key = input("Enter a word to search: ").strip().lower()
        if search_key == '':
            print("Exiting the search...")
            break

        if search_key in word_frequency:
            print(f"Found a match!:")

            # Gets the linked list for the searched word
            current = word_frequency[search_key].head

            # Iterate through the linked list and print file names
            while current:
                # doc ID to file name mapping
                file_name = doc_id_to_file[current.doc_id]
                print(f"  {file_name}")
                current = current.next
        else:
            print(f"No match.")

search_loop(all_file_data, doc_id_to_file)
