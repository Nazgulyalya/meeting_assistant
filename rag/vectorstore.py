import chromadb
from chromadb.utils import embedding_functions
from rag.chunker import chunk_text
from rag.pii_scrubber import scrub_pii
from typing import List, Dict
import uuid

# Используем локальные эмбеддинги — бесплатно
EMBEDDING_FN = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)

class MeetingVectorStore:
    def __init__(self, persist_path: str = "./chroma_db"):
        self.client = chromadb.PersistentClient(path=persist_path)
        self.collection = self.client.get_or_create_collection(
            name="meetings",
            embedding_function=EMBEDDING_FN
        )

    def add_meeting(self, meeting_id: str, transcript: str, metadata: dict = {}):
        """Chunk, scrub PII, embed and store a meeting transcript."""
        clean_text = scrub_pii(transcript)
        chunks = chunk_text(clean_text)

        ids = [f"{meeting_id}_chunk_{i}" for i in range(len(chunks))]
        metadatas = [{**metadata, "meeting_id": meeting_id, "chunk_index": i}
                     for i in range(len(chunks))]

        self.collection.add(documents=chunks, ids=ids, metadatas=metadatas)
        print(f"Stored {len(chunks)} chunks for meeting '{meeting_id}'")

    def query(self, query_text: str, n_results: int = 5) -> List[Dict]:
        """Retrieve most relevant chunks for a query."""
        results = self.collection.query(
            query_texts=[query_text],
            n_results=min(n_results, self.collection.count() or 1)
        )
        output = []
        for i, doc in enumerate(results["documents"][0]):
            output.append({
                "text": doc,
                "meeting_id": results["metadatas"][0][i].get("meeting_id"),
                "distance": results["distances"][0][i]
            })
        return output

    def count(self) -> int:
        return self.collection.count()