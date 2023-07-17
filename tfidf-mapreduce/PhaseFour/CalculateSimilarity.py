import math

# Write only documents with TF-IDF greather than:
SIMILARITY_THRESHOLD = 0.1

def calculate_cosine_similarity(tfidf_dict1, tfidf_dict2):
    # Find the intersection of keys in both tfidf dictionaries
    intersection = set(tfidf_dict1.keys()) & set(tfidf_dict2.keys())
    
    # Calculate the dot product of tfidf values for common words
    dot_product = sum(tfidf_dict1[word] * tfidf_dict2[word] for word in intersection)
    
    # Calculate the magnitude of tfidf_dict1
    magnitude1 = math.sqrt(sum(tfidf_dict1[word] ** 2 for word in tfidf_dict1))
    
    # Calculate the magnitude of tfidf_dict2
    magnitude2 = math.sqrt(sum(tfidf_dict2[word] ** 2 for word in tfidf_dict2))
    
    # Calculate the cosine similarity
    similarity = dot_product / (magnitude1 * magnitude2)
    
    return similarity

def read_tfidf_file(file_path):
    tfidf_dict = {}
    with open(file_path, 'r') as file:
        for line in file:
            # Input format: 
            # ((word, doc_id), tf-idf)
            word_doc, tfidf_value = line.strip().split('\t')
            word, doc_id = word_doc.split(',')

            # Create an inner dictionary for each document ID if it doesn't exist
            tfidf_dict.setdefault(doc_id, {})
            tfidf_dict[doc_id][word] = float(tfidf_value)

    return tfidf_dict

def write_similarity_file(similarity_dict, output_path):

    # Write document in format:
    # <Document i>-<Document j>: Similarity

    with open(output_path, 'w') as file:
        for doc_id1, doc_id2 in similarity_dict:
            similarity = similarity_dict[(doc_id1, doc_id2)]
            if similarity > SIMILARITY_THRESHOLD:
                file.write(f"{doc_id1}-{doc_id2}:{similarity}\n")

def calculate_document_similarity(input_path, output_path):
    tfidf_dict = read_tfidf_file(input_path)
    similarity_dict = {}
    doc_ids = list(tfidf_dict.keys())
    num_docs = len(doc_ids)

    for i in range(num_docs):
        for j in range(i + 1, num_docs):
            doc_id1 = doc_ids[i]
            doc_id2 = doc_ids[j]

            similarity = calculate_cosine_similarity(tfidf_dict[doc_id1], tfidf_dict[doc_id2])
            similarity_dict[(doc_id1, doc_id2)] = similarity

    write_similarity_file(similarity_dict, output_path)

# Start script
calculate_document_similarity("../PhaseThree/OutputPhaseThree.txt", "Similarity.txt")