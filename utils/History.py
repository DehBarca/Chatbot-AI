import logging
from typing import Dict, Any
from langchain.memory import ConversationBufferMemory
from langchain_core.messages import HumanMessage, AIMessage

# Configure logger
logger = logging.getLogger(__name__)

# Global memory instance - singleton pattern
_memory_instance = None

def get_memory_instance():
    """
    Get or create a singleton memory instance with optimized settings
    
    Returns:
        ConversationBufferMemory: Configured memory instance
    """
    global _memory_instance
    
    if _memory_instance is None:
        try:
            # Optimized memory configuration
            _memory_instance = ConversationBufferMemory(
                return_messages=True,
                memory_key="chat_history",
                max_token_limit=8000,  # Prevent memory overflow
                human_prefix="Usuario",
                ai_prefix="AI"
            )
            logger.info("Memory instance created successfully")
        except Exception as e:
            logger.error(f"Error creating memory instance: {e}")
            # Fallback to basic memory
            _memory_instance = ConversationBufferMemory(return_messages=True)
    
    return _memory_instance

def make_history(user_input: str = "", ai_output: str = "") -> str:
    """
    Manage conversation history with improved error handling and optimization
    
    Args:
        user_input (str): User's message (empty string for retrieval only)
        ai_output (str): AI's response (empty string for retrieval only)
    
    Returns:
        str: Formatted conversation history
    """
    try:
        memory = get_memory_instance()
        
        # Get current history first (before adding new messages)
        current_history = ""
        try:
            memory_vars = memory.load_memory_variables({})
            chat_history = memory_vars.get("chat_history", [])
            
            # Format history directly as readable string (optimized - no intermediate list)
            if chat_history:
                history_parts = []
                for msg in chat_history:
                    if hasattr(msg, 'content') and msg.content.strip():
                        prefix = "Usuario" if isinstance(msg, HumanMessage) else "AI"
                        history_parts.append(f"{prefix}: {msg.content}")
                
                current_history = "\n".join(history_parts)
            
        except Exception as e:
            logger.warning(f"Error loading memory variables: {e}")
            current_history = ""
        
        # Save new context only if both input and output are provided
        if user_input.strip() and ai_output.strip():
            try:
                memory.save_context(
                    {"input": user_input.strip()}, 
                    {"output": ai_output.strip()}
                )
                logger.debug("Successfully saved conversation context")
                
            except Exception as e:
                logger.error(f"Error saving context to memory: {e}")
        
        return current_history
        
    except Exception as e:
        logger.error(f"Critical error in make_history: {e}")
        return ""

def clear_history() -> bool:
    """
    Clear all conversation history
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        memory = get_memory_instance()
        memory.clear()
        logger.info("Conversation history cleared successfully")
        return True
        
    except Exception as e:
        logger.error(f"Error clearing history: {e}")
        return False

def get_history_length() -> int:
    """
    Get the number of messages in history
    
    Returns:
        int: Number of messages in conversation history
    """
    try:
        memory = get_memory_instance()
        memory_vars = memory.load_memory_variables({})
        chat_history = memory_vars.get("chat_history", [])
        return len(chat_history)
        
    except Exception as e:
        logger.error(f"Error getting history length: {e}")
        return 0

def get_memory_stats() -> Dict[str, Any]:
    """
    Get statistics about current memory usage
    
    Returns:
        Dict[str, Any]: Memory statistics
    """
    try:
        memory = get_memory_instance()
        memory_vars = memory.load_memory_variables({})
        chat_history = memory_vars.get("chat_history", [])
        
        stats = {
            "message_count": len(chat_history),
            "total_tokens": 0,
            "user_messages": 0,
            "ai_messages": 0
        }
        
        for msg in chat_history:
            if hasattr(msg, 'content'):
                # Rough token estimation (1 token ≈ 4 characters)
                stats["total_tokens"] += len(msg.content) // 4
                
                if isinstance(msg, HumanMessage):
                    stats["user_messages"] += 1
                elif isinstance(msg, AIMessage):
                    stats["ai_messages"] += 1
        
        return stats
        
    except Exception as e:
        logger.error(f"Error getting memory stats: {e}")
        return {"message_count": 0, "total_tokens": 0, "user_messages": 0, "ai_messages": 0}