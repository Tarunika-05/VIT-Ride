import os
import re
from typing import List, Dict, Any, Optional
from ..config import settings
from ..models.route import RouteInfo
from .rag_indexer import generate_route_documents

class RouteVectorStore:
    def __init__(self, persist_dir: Optional[str] = None):
        self.persist_dir = persist_dir or settings.CHROMA_PERSIST_DIR
        self.collection_name = "vit_campus_routes"
        self._client = None
        self._collection = None
        self._in_memory_docs: List[Dict[str, Any]] = []
        self._init_store()

    def _init_store(self):
        """Initialize ChromaDB client or fallback to in-memory store."""
        try:
            import chromadb
            os.makedirs(self.persist_dir, exist_ok=True)
            self._client = chromadb.PersistentClient(path=self.persist_dir)
            self._collection = self._client.get_or_create_collection(
                name=self.collection_name,
                metadata={"description": "VIT Chennai Bus Route Index"}
            )
        except Exception as e:
            # Fallback will use self._in_memory_docs
            self._collection = None

    def index_routes(self, routes: List[RouteInfo]) -> int:
        """
        Converts routes into RAG documents and stores them in ChromaDB and memory cache.
        """
        docs = generate_route_documents(routes)
        self._in_memory_docs = docs
        
        if self._collection is not None and docs:
            ids = [d["id"] for d in docs]
            documents = [d["text"] for d in docs]
            metadatas = [d["metadata"] for d in docs]
            
            # Upsert into ChromaDB
            try:
                self._collection.upsert(
                    ids=ids,
                    documents=documents,
                    metadatas=metadatas
                )
            except Exception as e:
                pass
                
        return len(docs)

    def search(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """
        Semantic search for relevant routes based on the user's natural language query.
        """
        query_cleaned = query.strip()
        if not query_cleaned:
            return []

        # 1. Try ChromaDB semantic search first
        if self._collection is not None:
            try:
                res = self._collection.query(
                    query_texts=[query_cleaned],
                    n_results=min(n_results, len(self._in_memory_docs) or n_results)
                )
                if res and res.get("documents") and res["documents"][0]:
                    results = []
                    docs = res["documents"][0]
                    metas = res["metadatas"][0] if res.get("metadatas") else [{}] * len(docs)
                    ids = res["ids"][0] if res.get("ids") else [""] * len(docs)
                    distances = res["distances"][0] if res.get("distances") else [0.0] * len(docs)
                    
                    for doc_id, doc_text, meta, dist in zip(ids, docs, metas, distances):
                        results.append({
                            "id": doc_id,
                            "text": doc_text,
                            "metadata": meta,
                            "distance": round(float(dist), 4) if dist is not None else 0.0
                        })
                    return results
            except Exception as e:
                pass

        # 2. Resilient keyword + token scoring fallback
        query_tokens = set(re.findall(r'\b[a-zA-Z0-9]+\b', query_cleaned.lower()))
        scored_docs = []
        
        for doc in self._in_memory_docs:
            text_lower = doc["text"].lower()
            score = 0
            for token in query_tokens:
                if token in text_lower:
                    score += 2 if len(token) > 3 else 1
            if score > 0:
                scored_docs.append((score, doc))
                
        scored_docs.sort(key=lambda x: x[0], reverse=True)
        return [
            {
                "id": doc["id"],
                "text": doc["text"],
                "metadata": doc["metadata"],
                "distance": round(1.0 / (score + 1), 4)
            }
            for score, doc in scored_docs[:n_results]
        ]

    def clear(self):
        """Clears all stored documents."""
        self._in_memory_docs = []
        if self._collection is not None and self._client is not None:
            try:
                self._client.delete_collection(self.collection_name)
                self._collection = self._client.get_or_create_collection(self.collection_name)
            except Exception:
                pass
