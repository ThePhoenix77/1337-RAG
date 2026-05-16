from __future__ import annotations  #hadi to avoid name error(just in case)
from dotenv import load_dotenv
from pinecone import Pinecone
import os

INDEX_NAME = "rag-demo"


def get_index():
    load_dotenv()

    pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

    if INDEX_NAME not in pc.list_indexes().names():
        pc.create_index(
            name=INDEX_NAME,
            dimension=768,  # nomic dimensions
            metric="cosine",
            spec={
                "serverless": {
                    "cloud": "aws",
                    "region": "us-east-1",
                }
            },
        )

    return pc.Index(INDEX_NAME)
