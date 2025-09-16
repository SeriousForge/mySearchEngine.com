import os
#extracts all of the information from a folder, file by file
#returns it all in file_contents as a dictionary
#gives an error if the folder isn't found
def extract_words_from_files(directory_path):
    file_contents = {}
    try:
        for file_name in os.listdir(directory_path):
            full_path = os.path.join(directory_path, file_name)
            if os.path.isfile(full_path):
                try:
                    with open(full_path, 'r') as f:
                        file_contents[file_name] = f.read()
                except Exception as e:
                    print(f"Error reading file {file_name}")
    except FileNotFoundError:
        print("Directory not found")
    except Exception:
        print("Error occurred")
    return file_contents

file_path = 'Extract_List.txt'

contextWord = "null"
matchWord = "null"
searchWord = "null"

#looks for where the script is and changes to its directory before extracting from folder Jan
script_dir = os.path.dirname(os.path.realpath(__file__))
os.chdir(script_dir)
all_file_data = extract_words_from_files("Jan")
#shows the data extracted from the folder
for filename, content in all_file_data.items():
    print(f"File: {filename}\nContent:\n{content}\n---")



print("Web Searchers Part 1 \n\nTask 1:")
if matchWord == searchWord:
    print("\n The Words Match! \n")