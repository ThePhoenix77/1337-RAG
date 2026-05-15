from chunking import chunk_text
from embeddings import generate_embedding
from pinecone_service import index

with open("data/notes.txt", "r") as file:
    text=file.read()

chunks=chunk_text(text)
# for c in chunks:
#     print(f"*** Chunk ***:  {c}")
vectors=[]
for i, chunk in enumerate(chunks):
    enumerate(chunks)
    embedding = generate_embedding(chunk)
    vector={
        "id": f"chunk-{i}",
        "values": embedding,
        "metadata": {
            "text": chunk
        }
    }
    vectors.append(vector)
index.upsert(vectors=vectors)
print("Document indexed successfully.")