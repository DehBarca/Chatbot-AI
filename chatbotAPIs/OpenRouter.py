import os
import logging
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from utils.Files import read_file

# Configure logger
logger = logging.getLogger(__name__)

load_dotenv()
OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY")

if not OPENROUTER_KEY:
    raise ValueError("OPENROUTER_API_KEY not found in .env file.")


def get_OpenRouter(model_id, message, history, archivo=""):
    """
    Get response from OpenRouter AI model with comprehensive error handling
    
    Args:
        model_id (str): OpenRouter model identifier
        message (str): User message
        history (str): Conversation history
        archivo (str): Optional PDF file name
    
    Returns:
        str: AI response or error message
    """
    try:
        logger.info(f"Initializing OpenRouter model: {model_id}")
        
        # Validate inputs
        if not message or not message.strip():
            logger.warning("Empty message provided to OpenRouter")
            return "Error: Message cannot be empty"
        
        if len(message) > 15000:
            logger.warning(f"Message too long for OpenRouter: {len(message)} characters")
            return "Error: Message is too long (max 15,000 characters)"
        
        # Initialize model with timeout
        llm = ChatOpenAI(
            model=model_id,
            openai_api_key=OPENROUTER_KEY,
            openai_api_base="https://openrouter.ai/api/v1",
            timeout=60,
            max_retries=2
        )
        
        # Handle file processing
        if archivo and archivo.strip():
            logger.info(f"Processing file with OpenRouter: {archivo}")
            try:
                # Check if file exists
                file_path = f'./archivos/{archivo}'
                if not os.path.exists(file_path):
                    logger.error(f"File not found: {archivo}")
                    return f"Error: File '{archivo}' not found"
                
                # Process file
                reply = read_file(archivo, llm, message)
                logger.info(f"Successfully processed file {archivo} with OpenRouter")
                return reply
                
            except FileNotFoundError:
                logger.error(f"File not found during processing: {archivo}")
                return f"Error: Could not find file '{archivo}'"
            except Exception as e:
                logger.error(f"Error processing file {archivo} with OpenRouter: {e}")
                return f"Error: Could not process file '{archivo}'. Please try again."
        
        # Handle regular chat
        else:
            logger.info("Processing regular chat message with OpenRouter")
            try:
                prompt = f"Context: el siguiente contenido es el historial de la conversación:{history} puedes usarlo para responder al usuario\nUser: {message}"
                reply = llm.invoke(prompt)
                
                if not reply or not reply.content:
                    logger.warning("Empty response from OpenRouter")
                    return "Error: Received empty response from AI"
                
                logger.info("Successfully received response from OpenRouter")
                return reply.content
                
            except Exception as e:
                logger.error(f"Error during OpenRouter chat: {e}")
                return "Error: Could not get response from OpenRouter. Please try again."
    
    except ValueError as e:
        logger.error(f"Invalid model or parameters for OpenRouter: {e}")
        return f"Error: Invalid model '{model_id}' or configuration"
    
    except ConnectionError as e:
        logger.error(f"Connection error with OpenRouter API: {e}")
        return "Error: Could not connect to OpenRouter. Please check your internet connection."
    
    except TimeoutError as e:
        logger.error(f"Timeout error with OpenRouter API: {e}")
        return "Error: OpenRouter request timed out. Please try again."
    
    except Exception as e:
        logger.error(f"Unexpected error in OpenRouter: {e}")
        return "Error: Something went wrong with OpenRouter. Please try again."