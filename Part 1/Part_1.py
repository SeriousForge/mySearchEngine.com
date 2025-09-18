import os


class Node:
    def __init__(self, doc_id, frequency=1):
        self.doc_id = doc_id
        self.frequency = frequency
        self.next = None
class LinkedList:
    def __init__(self):
        self.head = None

    def update_list(self, doc_id):
        
        if self.head is None:
            self.head = Node(doc_id)
        else:
            current = self.head
            while current:
                if current.doc_id == doc_id:
                    current.frequency += 1
                    return
                if current.next == None:
                    current.next = Node(doc_id)
                    return
                current = current.next
            
    
    def display(self):
        current = self.head
        while current:
            print(f"doc: {current.doc_id} frequency: {current.frequency}")
            current = current.next
            



#extracts all of the information from a folder, file by file
#separates the info into tokens, removes any tokens that include non alphabet chars, returns all valid tokens
#gives an error if the folder isn't found
def extract_words_from_files(directory_path):
    word_frequency = {}
    i = 0
    try:
        for file_name in os.listdir(directory_path):
            full_path = os.path.join(directory_path, file_name)
            if os.path.isfile(full_path):
                try:
                    with open(full_path, 'r') as f:
                        
                        file_info = f.read()
                        split_info = file_info.split()
                        for term in split_info:
                            if term.isalpha():
                                word = term.lower()
                                if word not in word_frequency:
                                    word_frequency[word] = LinkedList()
                                word_frequency[word].update_list(i)
                        i += 1
                except Exception as e:
                    print(f"Error reading file {file_name}")
    except FileNotFoundError:
        print("Directory not found")
    except Exception:
        print("Error occurred")
    return word_frequency

file_path = 'Extract_List.txt'

contextWord = "null"
matchWord = "null"
searchWord = "null"

#looks for where the script is and changes to its directory before extracting from folder Jan
script_dir = os.path.dirname(os.path.realpath(__file__))
os.chdir(script_dir)
all_file_data = extract_words_from_files("Jan")
#shows the data extracted from the folder
for word, linked_list in all_file_data.items():
    print(f"Word: {word}")
    linked_list.display()
    print("---")



print("Web Searchers Part 1 \n\nTask 1:")
if matchWord == searchWord:
    print("\n The Words Match! \n")