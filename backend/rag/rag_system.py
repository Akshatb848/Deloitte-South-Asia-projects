"""
RAG System - Retrieval-Augmented Generation
Handles vector embeddings, storage, and semantic search
"""

import os
import json
import numpy as np
import faiss
from typing import List, Dict, Any, Optional
from pathlib import Path
from sentence_transformers import SentenceTransformer


class RAGSystem:
    """RAG system for newsletter content retrieval"""

    def __init__(self):
        self.embedding_model_name = os.getenv(
            "EMBEDDING_MODEL",
            "sentence-transformers/all-MiniLM-L6-v2"
        )
        self.vector_db_path = os.getenv("VECTOR_DB_PATH", "./vector_db")
        self.embedding_model = None
        self.index = None
        self.documents = []
        self.newsletter_data = {}
        self.initialized = False

    async def initialize(self):
        """Initialize RAG system components"""
        try:
            # Load embedding model
            print(f"Loading embedding model: {self.embedding_model_name}")
            self.embedding_model = SentenceTransformer(self.embedding_model_name)

            # Load newsletter data
            self._load_newsletter_data()

            # Create or load vector index
            await self._initialize_vector_db()

            self.initialized = True
            print("RAG system initialized successfully")

        except Exception as e:
            print(f"Error initializing RAG system: {e}")
            raise

    def _load_newsletter_data(self):
        """Load newsletter data from JSON file"""
        data_path = Path(__file__).parent.parent.parent / "data" / "newsletter_data.json"

        if not data_path.exists():
            raise FileNotFoundError(f"Newsletter data not found at {data_path}")

        with open(data_path, 'r') as f:
            self.newsletter_data = json.load(f)

        print(f"Loaded newsletter data for {len(self.newsletter_data)} months")

    async def _initialize_vector_db(self):
        """Create or load FAISS vector database"""
        index_path = Path(self.vector_db_path) / "index.faiss"
        docs_path = Path(self.vector_db_path) / "documents.json"

        # Create directory if it doesn't exist
        Path(self.vector_db_path).mkdir(parents=True, exist_ok=True)

        if index_path.exists() and docs_path.exists():
            # Load existing index
            print("Loading existing vector index...")
            self.index = faiss.read_index(str(index_path))
            with open(docs_path, 'r') as f:
                self.documents = json.load(f)
            print(f"Loaded {len(self.documents)} documents from vector DB")
        else:
            # Create new index
            print("Creating new vector index...")
            await self._build_vector_db()

    async def _build_vector_db(self):
        """Build vector database from newsletter data"""
        print("Building vector database from newsletter data...")

        # Chunk the data
        chunks = self._create_chunks()
        print(f"Created {len(chunks)} chunks")

        # Generate embeddings
        texts = [chunk['text'] for chunk in chunks]
        embeddings = self.embedding_model.encode(
            texts,
            show_progress_bar=True,
            batch_size=32
        )

        # Create FAISS index
        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dimension)
        self.index.add(embeddings.astype('float32'))

        # Store documents
        self.documents = chunks

        # Save index and documents
        index_path = Path(self.vector_db_path) / "index.faiss"
        docs_path = Path(self.vector_db_path) / "documents.json"

        faiss.write_index(self.index, str(index_path))
        with open(docs_path, 'w') as f:
            json.dump(self.documents, f, indent=2)

        print(f"Vector DB built and saved with {len(chunks)} documents")

    def _create_chunks(self) -> List[Dict[str, Any]]:
        """
        Create document chunks from newsletter data

        Chunks by:
        - Monthly overview
        - Individual highlights
        - Events
        - State performance
        - Infrastructure data
        """
        chunks = []

        for month_key, month_data in self.newsletter_data.items():
            month_name = month_data['month']

            # Chunk 1: Monthly overview with key statistics
            overview_text = f"""
            Month: {month_name}

            Key Statistics:
            - Total Schools: {month_data['stats']['schools']:,}
            - Registered Teachers: {month_data['stats']['teachers']:,}
            - Enrolled Students: {month_data['stats']['students']:,}
            - APAAR IDs Issued: {month_data['stats']['apaar_ids']:,}
            - Attendance Rate: {month_data['stats']['attendance_rate']}%
            - Teacher Tracking: {month_data['stats']['teacher_tracking']}%
            """

            chunks.append({
                'text': overview_text.strip(),
                'month': month_key,
                'type': 'overview',
                'metadata': {
                    'month_name': month_name,
                    'stats': month_data['stats']
                }
            })

            # Chunk 2: Each highlight as separate chunk
            for idx, highlight in enumerate(month_data['highlights']):
                chunks.append({
                    'text': f"Month: {month_name}\n\nHighlight: {highlight}",
                    'month': month_key,
                    'type': 'highlight',
                    'metadata': {
                        'month_name': month_name,
                        'highlight_index': idx
                    }
                })

            # Chunk 3: Events
            for event in month_data['events']:
                event_text = f"""
                Month: {month_name}

                Event: {event['title']}
                Date: {event['date']}
                Description: {event['description']}
                """
                chunks.append({
                    'text': event_text.strip(),
                    'month': month_key,
                    'type': 'event',
                    'metadata': {
                        'month_name': month_name,
                        'event_title': event['title']
                    }
                })

            # Chunk 4: State performance
            state_perf_text = f"Month: {month_name}\n\nState Performance:\n"
            for state, metrics in month_data['state_performance'].items():
                state_perf_text += f"- {state}: Attendance {metrics['attendance']}%, APAAR Coverage {metrics['apaar_coverage']}%\n"

            chunks.append({
                'text': state_perf_text.strip(),
                'month': month_key,
                'type': 'state_performance',
                'metadata': {
                    'month_name': month_name,
                    'state_data': month_data['state_performance']
                }
            })

            # Chunk 5: Infrastructure
            infra_text = f"""
            Month: {month_name}

            Infrastructure Development:
            - Smart Classrooms: {month_data['infrastructure']['smart_classrooms']:,}
            - Computer Labs: {month_data['infrastructure']['computer_labs']:,}
            - Internet Enabled Schools: {month_data['infrastructure']['internet_enabled']:,}
            """

            chunks.append({
                'text': infra_text.strip(),
                'month': month_key,
                'type': 'infrastructure',
                'metadata': {
                    'month_name': month_name,
                    'infrastructure': month_data['infrastructure']
                }
            })

        return chunks

    async def search(
        self,
        query: str,
        top_k: int = 5,
        filter_month: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Perform semantic search on newsletter content

        Args:
            query: Search query
            top_k: Number of results to return
            filter_month: Optional month filter

        Returns:
            List of relevant documents with scores
        """
        if not self.initialized:
            raise RuntimeError("RAG system not initialized")

        # Generate query embedding
        query_embedding = self.embedding_model.encode([query])[0]

        # Search in FAISS index
        distances, indices = self.index.search(
            query_embedding.reshape(1, -1).astype('float32'),
            top_k * 2 if filter_month else top_k
        )

        # Retrieve documents
        results = []
        for idx, distance in zip(indices[0], distances[0]):
            if idx < len(self.documents):
                doc = self.documents[idx].copy()

                # Apply month filter if specified
                if filter_month and doc['month'] != filter_month:
                    continue

                doc['score'] = float(1 / (1 + distance))  # Convert distance to similarity score
                results.append(doc)

                if len(results) >= top_k:
                    break

        return results

    def get_context_for_query(
        self,
        query: str,
        current_month: Optional[str] = None,
        top_k: int = 3
    ) -> str:
        """
        Get formatted context for LLM based on query

        Args:
            query: User query
            current_month: Current month context
            top_k: Number of documents to retrieve

        Returns:
            Formatted context string
        """
        import asyncio

        # Perform search
        results = asyncio.run(self.search(query, top_k=top_k, filter_month=current_month))

        if not results:
            return "No relevant information found in the newsletter data."

        # Format context
        context_parts = []
        for idx, result in enumerate(results, 1):
            context_parts.append(f"[Source {idx} - {result['metadata']['month_name']} - {result['type']}]")
            context_parts.append(result['text'])
            context_parts.append("")  # Empty line

        return "\n".join(context_parts)

    def get_available_months(self) -> List[str]:
        """Get list of available months"""
        return list(self.newsletter_data.keys())

    def get_month_data(self, month: str) -> Optional[Dict[str, Any]]:
        """Get complete data for a specific month"""
        return self.newsletter_data.get(month)

    def is_initialized(self) -> bool:
        """Check if RAG system is initialized"""
        return self.initialized

    async def cleanup(self):
        """Cleanup resources"""
        self.embedding_model = None
        self.index = None
        self.documents = []
        self.initialized = False
        print("RAG system cleaned up")
