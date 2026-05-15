import os
from dotenv import load_dotenv
from pinecone import Pinecone

load_dotenv()

pc = Pinecone(
    api_key=os.getenv("PINECONE_API_KEY")
)

index_name = "rag-demo"
if index_name not in pc.list_indexes().names():
    pc.create_index(
        name=index_name,
        dimension=768, #nomic dimensions
        metric="cosine",
        spec={
            "serverless":{
                "cloud": "aws",
                "region": "us-east-1"
            }
        }
    )
index = pc.Index(index_name)
print("Pinecone index ready.")
