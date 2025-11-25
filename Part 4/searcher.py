import math
from html_utils import check_stopword, tokenize_query
from indexer import DOC_LENGTHS

# Task 3: Build a query searcher
def rank_documents(query_words, current_result, word_frequency, doc_id_to_file):
    scores = {}
    N = len(doc_id_to_file)

    query_vec = {}
    for word in query_words:
        if word in word_frequency:
            df = max(1, word_frequency[word].doc_freq())
            idf = math.log((N + 1) / (df + 1)) + 1  
            tf = query_words.count(word)
            query_vec[word] = (1 + math.log(tf)) * idf
            
    if not query_vec:
        return []
    
    # Calculates cosine similarity using node lookup
    for doc_id in current_result:
        dot_product = 0.0
        query_norm = math.sqrt(sum(v ** 2 for v in query_vec.values()))

        for word, q_weight in query_vec.items():
            postings = word_frequency.get(word)
            if postings is None:
                continue
            node = postings.nodes_by_doc.get(doc_id)
            if node is not None:
                dot_product += q_weight * node.norm_tf_idf

        scores[doc_id] = dot_product / query_norm

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
            ranked_docs = rank_documents(querie_words, all_docs, word_frequency, doc_id_to_file)
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
            ranked_docs = rank_documents(querie_words, lefthandside, word_frequency, doc_id_to_file)
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

#search_loop(all_file_data, doc_id_to_file)
def compute_keyword_correlation(term1, term2, index):
    """
    Computes corr(term1, term2) by walking down the postings lists
    and summing tf-idf products for documents that appear in both.
    """
    postings1 = index.get(term1)
    postings2 = index.get(term2)
    if postings1 is None or postings2 is None:
        return 0.0

    n1 = postings1.head
    n2 = postings2.head
    score = 0.0

    while n1 and n2:
        if n1.doc_id == n2.doc_id:
            score += n1.norm_tf_idf * n2.norm_tf_idf
            n1 = n1.next
            n2 = n2.next
        elif n1.doc_id < n2.doc_id:
            n1 = n1.next
        else:
            n2 = n2.next

    return score

def extract_keywords_from_docs(doc_ids, index):
    keyword_set = set()
    for term, postings in index.items():
        node = postings.head
        while node:
            if node.doc_id in doc_ids:
                keyword_set.add(term)
                break
            node = node.next
    return list(keyword_set)

def suggest_keywords(query_terms, index, top_k=5):
    scores = {}

    # Get list K
    for q in query_terms:
        if q not in index:
            continue
        for k in index.keys():
            if k == q:
                continue
            corr = compute_keyword_correlation(q, k, index)
            if corr > 0:
                scores[k] = scores.get(k, 0) + corr

    # return top_k strongest correlations
    sorted_terms = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return [term for term, _ in sorted_terms[:top_k]]

def search_core(query_words, word_frequency, doc_id_to_file):
    all_docs = list(doc_id_to_file.keys())
    ranked_docs = rank_documents(query_words, all_docs, word_frequency, doc_id_to_file)
    ranked_docs = [(doc_id, score) for doc_id, score in ranked_docs if score > 0.0]
    
    results = []
    for doc_id, score in ranked_docs:
        file_name = doc_id_to_file[doc_id]
        results.append({
            "doc_id": doc_id,
            "file": file_name,
            "score": round(score, 6)
        })
    return results


def search_loop_equiv(search_key, word_frequency, doc_id_to_file):
    search_key = search_key.strip().lower()
    or_mode = False
    and_mode = False
    but_mode = False
    lefthandside = []
    righthandside = []
    search_key = search_key.strip().lower()
    querie_words = tokenize_query(search_key)


    original_results = search_core(querie_words, word_frequency, doc_id_to_file)
    suggested_keywords = suggest_keywords(querie_words, word_frequency)
    querie_words = tokenize_query(search_key)
    results = original_results[:5]
    has_boolean = any(word in ["or", "and", "but"] for word in querie_words)
    top_doc_ids = [r['doc_id'] for r in results]

    # Suggest top 3 keywords correlated with query in top docs
    all_keywords = extract_keywords_from_docs(top_doc_ids, word_frequency)
    scores = {}
    for q in querie_words:
        for k in all_keywords:
            if k == q:
                continue
            corr = compute_keyword_correlation(q, k, word_frequency)
            if corr > 0:
                scores[k] = scores.get(k, 0) + corr

    top_keywords = [k for k, _ in sorted(scores.items(), key=lambda x: x[1], reverse=True)[:3]]

    # Phrasal search
    if search_key.startswith('"') and search_key.endswith('"'):
        lefthandside = phrasal_search(word_frequency, querie_words)
        
        # Rank phrasal search results
        results = []
        if lefthandside:
            ranked_docs = rank_documents(querie_words, lefthandside, word_frequency, doc_id_to_file)
            ranked_docs = [(doc_id, score) for doc_id, score in ranked_docs if score != 0.0]
            
            for doc_id, score in ranked_docs:
                file_name = doc_id_to_file[doc_id]
                results.append({
                    "doc_id": doc_id,
                    "file": file_name,
                    "score": round(score, 6)
                })
        suggested_keywords = top_keywords
        reformulated_query_words = querie_words + suggested_keywords
        reformulated_results = search_core(reformulated_query_words, word_frequency, doc_id_to_file)
        return {
            "results": results,
            "suggestions": suggested_keywords,
            "reformulated_results": reformulated_results
        }

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
            ranked_docs = rank_documents(querie_words, lefthandside, word_frequency, doc_id_to_file)
            ranked_docs = [(doc_id, score) for doc_id, score in ranked_docs if score != 0.0]

            for doc_id, score in ranked_docs:
                file_name = doc_id_to_file[doc_id]
                results.append({
                    "doc_id": doc_id,            
                    "file": file_name,
                    "score": round(score, 6)
                })
        suggested_keywords = top_keywords
        reformulated_query_words = querie_words + suggested_keywords
        reformulated_results = search_core(reformulated_query_words, word_frequency, doc_id_to_file)
        return {
            "results": results,
            "suggestions": suggested_keywords,
            "reformulated_results": reformulated_results
        }

    else:
        # Vector Space retrieval (no boolean operators)
        all_docs = list(doc_id_to_file.keys())
        ranked_docs = rank_documents(querie_words, all_docs, word_frequency, doc_id_to_file)
        ranked_docs = [(doc_id, score) for doc_id, score in ranked_docs if score != 0.0]
        
        results = []
        
        for doc_id, score in ranked_docs:
            file_name = doc_id_to_file[doc_id]
            results.append({
                "doc_id": doc_id,
                "file": file_name,
                "score": round(score, 6)
            })
        suggested_keywords = top_keywords    
        reformulated_query_words = querie_words + suggested_keywords
        reformulated_results = search_core(reformulated_query_words, word_frequency, doc_id_to_file)
        return {
            "results": results,
            "suggestions": suggested_keywords,
            "reformulated_results": reformulated_results
        }