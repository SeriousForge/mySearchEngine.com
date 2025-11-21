import os
import math
from zipfile import ZipFile
from queue import Queue
from posixpath import normpath, join as posixjoin
from html_utils import check_stopword, extract_words_from_html, extract_links_from_html, TITLE_RE

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
        self.tail = None
        self.nodes_by_doc = {}

    def update_list(self, doc_id, position):
        # If doc already has a node
        node = self.nodes_by_doc.get(doc_id)
        if node is not None:
            node.frequency += 1
            node.position.append(position)
            return
        
        # Otherwise, create a new node and adds it to the end of the list
        new_node = Node(doc_id, position)
        if self.head is None:
            self.head = self.tail = new_node
        else:
            self.tail.next = new_node
            self.tail = new_node
        self.nodes_by_doc[doc_id] = new_node
            
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
        node = self.nodes_by_doc.get(id)
        return node.position if node else []
    
    def doc_freq(self):
        return len(self.nodes_by_doc)
    
DOC_LENGTHS = {}
HYPERLINKS = []
DOCUMENTS = {}
DOC_FREQS = {}

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


#helper function for spidering
#Resolves a link relative to the current file's directory.
#It makes sure that the correct file path is used to open it
#posixjoin handles knowing how to combine the link
#normpath removes stuff like // and anything that would make it not work as intended
#added the top 2 if to deal with links that we can get from the rhf.zip
def resolve_path(current_file, link):
    
    if link.startswith('http://') or link.startswith('https://') or link.startswith('//'):
        return None
    
    # Handle absolute paths (starting with /) - strip the leading slash
    if link.startswith('/'):
        normalized = normpath(link.lstrip('/'))
        return normalized
    
    # Handle relative paths
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
    visited = set()
    enqueued = set()
    
    #pathhelp will help when opening the start_file, it gives it the zip_path/
    pathhelp = ""
    for char in zip_path:
        if char != ".":
            pathhelp += char
        else:
            pathhelp += "/"
            break
    
    try:
        with ZipFile(zip_path, 'r') as zip_archive: #opens the zip_path
            
            start_path = pathhelp + start_file
            visit.put(start_path)
            enqueued.add(start_path)

            #as long as visit isn't empty, keep on looping
            while(not visit.empty()):
                fname = visit.get()
                
                if fname in visited:
                    continue

                if not fname.endswith(('.html', '.htm')): #ignore non html, htm, add to visited to prevent adding again
                    visited.add(fname)
                    continue
                
                visited.add(fname)
                
                
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
                            if resolved_link and resolved_link not in visited and resolved_link not in enqueued:
                                visit.put(resolved_link)
                                enqueued.add(resolved_link)
                            
                        i+=1
                except Exception:
                    print(f"skipped: {fname}")    
            
            
    except FileNotFoundError:
        print("Directory not found")
    except Exception as e:
        print(f"Error occurred: {e}")
    return word_frequency, doc_id_to_file

def build_index(zip_path):
    """
    Build the search index from a zip file.
    Returns word_frequency and doc_id_to_file dictionaries.
    """

    script_dir = os.path.dirname(os.path.realpath(__file__))
    os.chdir(script_dir)

    # Clear global containers in case this is called multiple times
    global DOC_LENGTHS, HYPERLINKS, DOCUMENTS, DOC_FREQS
    DOC_LENGTHS = {}
    HYPERLINKS = []
    DOCUMENTS = {}
    DOC_FREQS = {}
    
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
    word_frequency = dict(word_frequency)  # if it was a defaultdict
    doc_id_to_file = dict(doc_id_to_file)
    
    return word_frequency, doc_id_to_file