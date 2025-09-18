# Jose X. Moreno 20387773
# Andrea Garza 20581964
# Leonardo Pérez 0444297
# Misael Garay 20522356

import os
from zipfile import ZipFile
from io import BytesIO
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


# Task 1 
#extracts all of the information from a folder, file by file
#separates the info into tokens, removes any tokens that include non alphabet chars, returns all valid tokens
#gives an error if the folder isn't found
def extract_words_from_files(directory_path):
    word_frequency = {}
    doc_id_to_file = {}
    i = 0
    try:
        for file_name in os.listdir(directory_path):
            full_path = os.path.join(directory_path, file_name)
            if os.path.isfile(full_path):
                doc_id_to_file[i] = file_name
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
    return word_frequency, doc_id_to_file

#same as above except for zip folder
def extract_from_zip(zip_path):
    word_frequency = {}
    doc_id_to_file = {}
    i = 0
    try:
        with ZipFile(zip_path, 'r') as zip_archive:
            files = zip_archive.namelist()
            for file_name in files:
                with zip_archive.open(file_name) as file_in_zip:
                    doc_id_to_file[i] = file_name
                    
                    file_info_undecoded = file_in_zip.read()
                    file_info = file_info_undecoded.decode('utf-8')
                    split_info = file_info.split()
                    for term in split_info:
                        if term.isalpha():
                            word = term.lower()
                            if word not in word_frequency:
                                word_frequency[word] = LinkedList()
                            word_frequency[word].update_list(i)
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