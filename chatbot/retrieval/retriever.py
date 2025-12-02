"""
Retrieval module for similarity search using Qdrant.
Performs vector similarity search to find relevant documents.
"""

from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue
from typing import List, Dict, Any, Optional
from ingestion.embeddings import EmbeddingGenerator
from retrieval.query_processor import QueryProcessor

class Retriever:
    """Handles similarity search and document retrieval using Qdrant."""
    
    def __init__(self, 
                 url: str = "http://localhost:6333",
                 api_key: str = None,
                 collection_name: str = "internship_education_db",
                 embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2",
                 top_k: int = 5):
        """
        Initialize the retriever.
        
        Args:
            url: Qdrant server URL
            api_key: API key for Qdrant Cloud (None for local)
            collection_name: Name of the collection to query
            embedding_model: Model name for generating query embeddings
            top_k: Number of top results to retrieve
        """
        self.url = url
        self.api_key = api_key
        self.collection_name = collection_name
        self.top_k = top_k
        self.client = None
        self.embedding_generator = EmbeddingGenerator(embedding_model)
        self.query_processor = QueryProcessor()  # Add query processor
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Qdrant client."""
        try:
            self.client = QdrantClient(
                url=self.url,
                api_key=self.api_key,
                timeout=60
            )
            print(f"Retriever initialized with collection: {self.collection_name}")
            
        except Exception as e:
            print(f"Error initializing retriever: {e}")
            raise
    
    def retrieve(self, 
                 query: str, 
                 top_k: Optional[int] = None,
                 filter_by: Optional[Dict[str, str]] = None) -> List[Dict[str, Any]]:
        """
        Retrieve relevant documents for a query.
        
        Args:
            query: User query text
            top_k: Number of results to retrieve (overrides default)
            filter_by: Optional metadata filters (e.g., {"company": "Google"})
            
        Returns:
            List of retrieved documents with metadata and scores
        """
        if not query:
            return []
        
        k = top_k if top_k is not None else self.top_k
        
        try:
            # Preprocess query
            processed = self.query_processor.process_query(query)
            normalized_query = processed['normalized']
            keyword_query = processed['keyword_query']
            
            # Log preprocessing for debugging
            print(f"Original query: {query}")
            print(f"Normalized: {normalized_query}")
            print(f"Keywords: {keyword_query}")
            
            # Use keyword query if it has content, otherwise use normalized
            search_query = keyword_query if keyword_query else normalized_query
            
            # Generate query embedding
            query_embedding = self.embedding_generator.generate_embedding(search_query)
            
            # Prepare filter if provided
            query_filter = None
            if filter_by:
                conditions = []
                for key, value in filter_by.items():
                    conditions.append(
                        FieldCondition(
                            key=key,
                            match=MatchValue(value=value)
                        )
                    )
                query_filter = Filter(must=conditions)
            
            # Perform similarity search
            search_results = self.client.query_points(
                collection_name=self.collection_name,
                query=query_embedding.tolist(),
                limit=k,
                query_filter=query_filter,
                with_payload=True,
                with_vectors=False
            ).points
            
            # Format results
            retrieved_docs = []
            
            for result in search_results:
                # Extract payload
                payload = result.payload
                content = payload.pop('content', '')
                
                # Similarity score (Qdrant returns score directly for cosine)
                similarity_score = result.score
                
                retrieved_docs.append({
                    'content': content,
                    'metadata': payload,  # All remaining fields are metadata
                    'similarity_score': similarity_score
                })
            
            print(f"Retrieved {len(retrieved_docs)} documents")
            return retrieved_docs
            
        except Exception as e:
            print(f"Error during retrieval: {e}")
            return []
    
    def format_retrieved_context(self, retrieved_docs: List[Dict[str, Any]]) -> str:
        """
        Format retrieved documents into a context string.
        
        Args:
            retrieved_docs: List of retrieved documents
            
        Returns:
            Formatted context string
        """
        if not retrieved_docs:
            return ""
        
        context_parts = []
        
        for idx, doc in enumerate(retrieved_docs, 1):
            metadata = doc.get('metadata', {})
            content = doc.get('content', '')
            
            company = metadata.get('company', 'Unknown')
            doc_type = metadata.get('document_type', 'Unknown')
            source = metadata.get('source', 'Unknown')
            
            formatted_chunk = f"""[Company]: {company}
[Document Type]: {doc_type}
[Source]: {source}

Content:
{content}
"""
            context_parts.append(formatted_chunk)
        
        return "\n---\n".join(context_parts)
    
    def ingest_qa_pair(self, question: str, answer: str) -> bool:
        """
        Ingest a single Q&A pair into Qdrant for future retrieval.
        
        Args:
            question: The user's question
            answer: The generated answer
            
        Returns:
            True if successful, False otherwise
        """
        if not question or not answer:
            return False
        
        try:
            from qdrant_client.models import PointStruct
            import uuid
            
            # Create content combining question and answer
            content = f"Question: {question}\n\nAnswer: {answer}"
            
            # Generate embedding for the question (for retrieval)
            embedding = self.embedding_generator.generate_embedding(question)
            
            # Create metadata
            metadata = {
                "document_type": "Generated Q&A",
                "company": "General Knowledge",
                "source": "Gemini LLM",
                "question": question,
                "answer": answer
            }
            
            # Create point
            point = PointStruct(
                id=str(uuid.uuid4()),
                vector=embedding.tolist(),
                payload={
                    "content": content,
                    **metadata
                }
            )
            
            # Upsert to Qdrant
            self.client.upsert(
                collection_name=self.collection_name,
                points=[point]
            )
            
            print(f"✓ Ingested Q&A pair into Qdrant")
            return True
            
        except Exception as e:
            print(f"Error ingesting Q&A pair: {e}")
            return False
