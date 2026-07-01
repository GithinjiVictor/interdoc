import chromadb         # is our vector database 
from chromadb.utils import embedding_functions

#PersistentClient - means Chroma writes everything on the disk, in this folder 
# even if you stop server , later on your uploaded documents are still there 
client = chromadb.PersistentClient(path="./data/chroma_db")

# creating an embedding function- something Chroma can call automatically, every time 
# we add or search to turn text into vector 
embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")

# collection - in ChromaDB is like a table in database 
# get_or_create_collection - if a collection named "documents" already exists , reuse it  else create a new one 
collection = client.get_or_create_collection(name="documents", embedding_function=embedding_fn)

# add_chunks () - saving chunks into the vector store
def add_chunks(doc_id: str, chunks: list[str]):
    # create a unique ID for every chunk 
    # ChromaDB require every stored item to have a unique id 
    ids = [f"{doc_id}_{i}" for i in range(len(chunks))]
    # create metadata dictionary for each chunk 
    # "source" - whch file this chunk came from
    # chunk_index - position of this chunk within the file 
    metadatas = [{"source": doc_id, "chunk_index": i} for i in range(len(chunks))]
    # Actually inserts data into ChromaDB 
    # documents=chunks  - the raw text (gets embedded automatically using embedding_fn )
    collection.add(documents=chunks, metadatas=metadatas, ids=ids)
    # return the count of chunks that were added 
    return len(chunks)


# search_chunks() - finding the closes chunks to a question 
# query - is the question text. top_k - how many of the closest chunks to return 
def search_chunks(query: str, top_k: int = 4):
    return collection.query(query_texts=[query], n_results=top_k)