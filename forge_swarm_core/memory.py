"""Forge Swarm — Memory Manager (ChromaDB-based lesson storage)."""

from __future__ import annotations

import json
from datetime import datetime
from typing import Any, Dict, List, Optional

import streamlit as st

from forge_swarm_core.core import Config
from forge_swarm_core.llm import OllamaEmbeddings


class MemoryManager:
    """Manage long-term memory with ChromaDB"""

    def __init__(self, config: Dict[str, Any], embedder: OllamaEmbeddings):
        self.config = config["memory"]
        self.embedder = embedder
        self.client = None
        self.collection = None
        self._initialize_db()

    def _initialize_db(self):
        """Initialize ChromaDB (lazy-imported on first call)."""
        try:
            db_path = self.config["db_path"]
            Path(db_path).mkdir(parents=True, exist_ok=True)

            _chroma_module, _Settings = _chromadb()
            self.client = _chroma_module.PersistentClient(
                path=db_path, settings=_Settings(anonymized_telemetry=False)
            )
            self.collection = self.client.get_or_create_collection(
                name=self.config["collection_name"]
            )
        except Exception as e:
            st.error(f"Failed to initialize memory database: {e}")
            raise

    def save_lesson(
        self, task_desc: str, output: str, critic_feedback: str, score: float
    ):
        """Save a lesson to memory"""
        try:
            text = f"Task: {task_desc}\nFeedback: {critic_feedback}"
            embedding = self.embedder.embed_documents([text])[0]

            lesson_id = f"lesson_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{self.collection.count()}"

            self.collection.add(
                documents=[critic_feedback],
                metadatas=[
                    {
                        "task": task_desc[:200],
                        "output_summary": output[:200],
                        "score": score,
                        "timestamp": datetime.now().isoformat(),
                    }
                ],
                ids=[lesson_id],
                embeddings=[embedding],
            )

            # Prune old lessons if needed
            self._prune_old_lessons()

        except Exception as e:
            st.warning(f"Could not save lesson: {e}")

    def get_relevant_lessons(self, task_desc: str, n: int = 3) -> List[str]:
        """Retrieve similar past lessons"""
        try:
            if self.collection.count() == 0:
                return []

            query_emb = self.embedder.embed_documents([task_desc])[0]
            results = self.collection.query(
                query_embeddings=[query_emb], n_results=min(n, self.collection.count())
            )

            if not results["metadatas"] or not results["metadatas"][0]:
                return []

            lessons = []
            for metadata, doc in zip(results["metadatas"][0], results["documents"][0]):
                score = metadata.get("score", "N/A")
                task = metadata.get("task", "Unknown task")
                lessons.append(f"[Score: {score}] {task}: {doc}")

            return lessons

        except Exception as e:
            st.warning(f"Could not retrieve lessons: {e}")
            return []

    def _prune_old_lessons(self):
        """Remove old lessons to stay within max_lessons limit"""
        try:
            max_lessons = self.config["max_lessons"]
            current_count = self.collection.count()

            if current_count > max_lessons:
                # Get all items sorted by timestamp
                all_items = self.collection.get()
                if all_items["metadatas"]:
                    # Sort by timestamp and remove oldest
                    items_with_time = [
                        (id_, meta.get("timestamp", ""))
                        for id_, meta in zip(all_items["ids"], all_items["metadatas"])
                    ]
                    items_with_time.sort(key=lambda x: x[1])

                    # Remove oldest items
                    to_remove = items_with_time[: current_count - max_lessons]
                    ids_to_remove = [item[0] for item in to_remove]

                    if ids_to_remove:
                        self.collection.delete(ids=ids_to_remove)

        except Exception as e:
            st.warning(f"Could not prune old lessons: {e}")

    def export_memory(self) -> str:
        """Export all stored lessons as JSON string for download."""
        try:
            results = self.collection.get(include=["documents", "metadatas"])
            export = {
                "exported_at": datetime.now().isoformat(),
                "collection": self.collection.name,
                "count": len(results["documents"]),
                "lessons": [
                    {"document": doc, "metadata": meta}
                    for doc, meta in zip(results["documents"], results["metadatas"])
                ],
            }
            return json.dumps(export, indent=2)
        except Exception as e:
            print(f"❌ Export failed: {e}")
            return json.dumps({"error": str(e)})

    def search_memory(self, query: str, n_results: int = 10) -> List[Dict]:
        """Search memory with text query, return ranked results."""
        try:
            count = self.collection.count()
            if count == 0:
                return []
            results = self.collection.query(
                query_texts=[query],
                n_results=min(n_results, count),
                include=["documents", "metadatas", "distances"],
            )
            return [
                {
                    "task": meta.get("task_description", "Unknown"),
                    "result": doc,
                    "score": meta.get("quality_score", 0),
                    "distance": round(dist, 4),
                    "stored_at": meta.get("stored_at", "Unknown"),
                }
                for doc, meta, dist in zip(
                    results["documents"][0],
                    results["metadatas"][0],
                    results["distances"][0],
                )
            ]
        except Exception as e:
            print(f"❌ Memory search failed: {e}")
            return []

    def get_stats(self) -> Dict[str, Any]:
        """Get memory statistics"""
        try:
            return {
                "total_lessons": self.collection.count(),
                "collection_name": self.config["collection_name"],
                "max_lessons": self.config["max_lessons"],
            }
        except Exception:
            return {"total_lessons": 0}

    def clear_memory(self) -> bool:
        """Delete all stored memories. Returns True on success."""
        try:
            self.collection.delete(where={})
            return True
        except Exception as e:
            st.error(f"Could not clear memory: {e}")
            return False

    def store_result(
        self,
        task_id: str,
        task_description: str,
        result: str,
        quality_score: int = 0,
        iterations: int = 1,
    ) -> None:
        """Store a completed task result - only if score meets threshold."""
        min_score = self.config.get("min_score_to_store", 7)
        if quality_score < min_score:
            print(
                f"⚠️ Score {quality_score} below threshold {min_score}. Skipping storage."
            )
            return
        try:
            text = f"Task: {task_description}\nResult: {result}"
            embedding = self.embedder.embed_documents([text])[0]

            self.collection.add(
                documents=[result],
                metadatas=[
                    {
                        "task_id": task_id,
                        "task_description": task_description[:500],
                        "quality_score": quality_score,
                        "iterations": iterations,
                        "stored_at": datetime.now().isoformat(),
                    }
                ],
                ids=[task_id],
                embeddings=[embedding],
            )
            print(f"💾 Stored lesson (score: {quality_score}/10)")
        except Exception as e:
            print(f"❌ Failed to store result: {e}")

    def query_similar(self, query: str, n_results: int = 3) -> List[Dict]:
        """Return top-n similar past results as dicts (alias for get_relevant_lessons)."""
        lessons = self.get_relevant_lessons(query, n_results)
        return [{"lesson": lesson} for lesson in lessons]

    def get_memory_stats(self) -> Dict[str, int]:
        """Return count of stored items and collection size."""
        stats = self.get_stats()
        return {
            "items_stored": stats.get("total_lessons", 0),
            "collection_size": stats.get("total_lessons", 0),
        }