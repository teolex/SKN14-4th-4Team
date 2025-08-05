from django.conf import settings
from pinecone import Pinecone
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore

from typing import Final

class VStore:
    pc           : Final[Pinecone]            = Pinecone(api_key=settings.PINECONE_PJ_KEY)
    index        : Final[Pinecone.Index]      = pc.Index(settings.INDEX_NAME)
    embeddings   : Final[OpenAIEmbeddings]    = OpenAIEmbeddings(model=settings.EMBED_MODEL)
    vector_store : Final[PineconeVectorStore] = PineconeVectorStore(index=index, embedding=embeddings)

    @classmethod
    def get_vec_store(cls):
        return VStore.vector_store