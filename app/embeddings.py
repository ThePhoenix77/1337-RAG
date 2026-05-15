import ollama

def generate_embedding(text):
    response = ollama.embeddings(
        model="nomic-embed-text",
        prompt=text
    )
    return response["embedding"]

# embedding = generate_embedding("ta to ti taha")
# print(f"length: {len(embedding)}")
# print(embedding)