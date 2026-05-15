from embeddings import generate_embedding
from pinecone_service import index
import ollama

#relevant chunks retrieval
query="What is a retrieval augmented generation?"

query_embedding=generate_embedding(query)
results=index.query(
    vector=query_embedding,
    top_k=3,
    include_metadata=True
)
# for match in results["matches"]:
#     print("\nScore:", match["score"])
#     print(match["metadata"]["text"])

#just separation
context="\n\n".join(
    match["metadata"]["text"]
    for match in results["matches"]
)

# print(context)

prompt = f"""
            You are a helpful AI assistant.

            Answer the question ONLY using the provided context.

            If the answer is not found in the context,
            say "I don't know."

            Context:
            {context}

            Question:
            {query}

            Answer:
        """

response=ollama.chat(
    model="mistral",
    messages=[
        {
            "role": "user",
            "content": prompt
        }
    ]
)

print("\n* ANSWER *\n")
print(response["message"]["content"])