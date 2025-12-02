"""
Routing rules module for directing queries to appropriate pipelines.
Determines whether to use RAG or external knowledge based on intent.
"""

from typing import Dict, Any
from routing.intent_router import IntentRouter

class RouteRules:
    """Manages routing logic based on intent classification."""
    
    def __init__(self):
        """Initialize routing rules."""
        self.intent_router = IntentRouter()
        
        # Define which intents use RAG
        self.rag_intents = [
            IntentRouter.COMPANY_INTERNSHIP
        ]
        
        # Define which intents use external knowledge
        self.external_intents = [
            IntentRouter.EDUCATION_CODING,
            IntentRouter.INTERVIEW_PREPARATION,
            IntentRouter.GENERAL_EDUCATION
        ]
    
    def should_use_rag(self, intent: str) -> bool:
        """
        Determine if RAG pipeline should be used for this intent.
        
        Args:
            intent: Intent category
            
        Returns:
            True if RAG should be used, False otherwise
        """
        return intent in self.rag_intents
    
    def should_use_external(self, intent: str) -> bool:
        """
        Determine if external knowledge pipeline should be used.
        
        Args:
            intent: Intent category
            
        Returns:
            True if external knowledge should be used, False otherwise
        """
        return intent in self.external_intents
    
    def route_query(self, query: str) -> Dict[str, Any]:
        """
        Route a query to the appropriate pipeline.
        
        Args:
            query: User query text
            
        Returns:
            Dictionary with routing information
        """
        # Classify intent
        intent = self.intent_router.classify_intent(query)
        
        # Determine pipeline
        use_rag = self.should_use_rag(intent)
        use_external = self.should_use_external(intent)
        
        # Get intent info
        intent_info = self.intent_router.get_intent_info(intent)
        
        return {
            "intent": intent,
            "intent_name": intent_info.get("name", "Unknown"),
            "use_rag": use_rag,
            "use_external": use_external,
            "pipeline": "RAG" if use_rag else "EXTERNAL"
        }
    
    def get_pipeline_for_intent(self, intent: str) -> str:
        """
        Get the pipeline name for a given intent.
        
        Args:
            intent: Intent category
            
        Returns:
            Pipeline name ("RAG" or "EXTERNAL")
        """
        if self.should_use_rag(intent):
            return "RAG"
        elif self.should_use_external(intent):
            return "EXTERNAL"
        else:
            return "UNKNOWN"
