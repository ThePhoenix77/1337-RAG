def chunk_text(text, chunk_size=300, overlap=50):
    start=0
    chunks=[]
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        start+=chunk_size - overlap
    return chunks

# with open("data/notes.txt", "r") as file:
#     text = file.read()

# chunks = chunk_text(text)

# for i, chunk in enumerate(chunks):
#     print(f"\n--- Chunk {i} ---\n")
#     print(chunk)