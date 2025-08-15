import os
import logging
from dotenv import load_dotenv
from langchain_together import ChatTogether
from utils.Files import read_file

# Configure logger
logger = logging.getLogger(__name__)

load_dotenv()
TOGETHER_KEY = os.getenv("TOGETHER_API_KEY")

if not TOGETHER_KEY:
    raise ValueError("TOGETHER_API_KEY not found in .env file.")


def get_Together(model_id, message, history, archivo=""):
    """
    Get response from Together AI model with comprehensive error handling
    
    Args:
        model_id (str): Together model identifier
        message (str): User message
        history (str): Conversation history
        archivo (str): Optional PDF file name
    
    Returns:
        str: AI response or error message
    """
    try:
        logger.info(f"Initializing Together model: {model_id}")
        
        # Validate inputs
        if not message or not message.strip():
            logger.warning("Empty message provided to Together")
            return "Error: Message cannot be empty"
        
        if len(message) > 12000:
            logger.warning(f"Message too long for Together: {len(message)} characters")
            return "Error: Message is too long (max 12,000 characters)"
        
        # Initialize model with timeout
        llm = ChatTogether(
            model=model_id,
            api_key=TOGETHER_KEY,
            timeout=60,
            max_retries=2
        )
        
        # Handle file processing
        if archivo and archivo.strip():
            logger.info(f"Processing file with Together: {archivo}")
            try:
                # Check if file exists
                file_path = f'./archivos/{archivo}'
                if not os.path.exists(file_path):
                    logger.error(f"File not found: {archivo}")
                    return f"Error: File '{archivo}' not found"
                
                # Process file
                reply = read_file(archivo, llm, message)
                logger.info(f"Successfully processed file {archivo} with Together")
                return reply
                
            except FileNotFoundError:
                logger.error(f"File not found during processing: {archivo}")
                return f"Error: Could not find file '{archivo}'"
            except Exception as e:
                logger.error(f"Error processing file {archivo} with Together: {e}")
                return f"Error: Could not process file '{archivo}'. Please try again."
        
        # Handle regular chat
        else:
            logger.info("Processing regular chat message with Together")
            try:
                prompt = f"Context: el siguiente contenido es el historial de la conversación:{history} puedes usarlo para responder al usuario\nUser: {message}"
                reply = llm.invoke(prompt)
                
                if not reply or not reply.content:
                    logger.warning("Empty response from Together")
                    return "Error: Received empty response from AI"
                
                logger.info("Successfully received response from Together")
                return reply.content
                
            except Exception as e:
                logger.error(f"Error during Together chat: {e}")
                return "Error: Could not get response from Together. Please try again."
    
    except ValueError as e:
        logger.error(f"Invalid model or parameters for Together: {e}")
        return f"Error: Invalid model '{model_id}' or configuration"
    
    except ConnectionError as e:
        logger.error(f"Connection error with Together API: {e}")
        return "Error: Could not connect to Together. Please check your internet connection."
    
    except TimeoutError as e:
        logger.error(f"Timeout error with Together API: {e}")
        return "Error: Together request timed out. Please try again."
    
    except Exception as e:
        logger.error(f"Unexpected error in Together: {e}")
        return "Error: Something went wrong with Together. Please try again."