import os
from zipfile import ZipFile
from html_utils import check_stopword, extract_words_from_html, extract_links_from_html, TITLE_RE
from indexer import LinkedList, DOC_LENGTHS, HYPERLINKS, DOCUMENTS, compute_doc_freqs, compute_norm_tf_idf

#Extracts all of the information from a folder, file by file
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

if __name__ == "__main__":
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
