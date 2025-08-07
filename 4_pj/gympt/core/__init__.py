import os
from pinecone import Pinecone
from langchain_pinecone import PineconeVectorStore
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv

load_dotenv()

PINECONE_PJ_KEY     = os.environ.get("PINECONE_PJ_KEY")
INDEX_NAME          = "food-index"
EMBED_MODEL         = "text-embedding-3-small"

pc                  = Pinecone(api_key=PINECONE_PJ_KEY)
index               = pc.Index(INDEX_NAME)

embeddings          = OpenAIEmbeddings(model=EMBED_MODEL)
vector_store        = PineconeVectorStore(index=index, embedding=embeddings)