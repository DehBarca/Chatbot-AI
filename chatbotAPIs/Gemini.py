import os
import logging
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from utils.Files import read_file

# Configure logger
logger = logging.getLogger(__name__)

load_dotenv()
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
os.environ["GOOGLE_API_KEY"] = GEMINI_KEY

if not GEMINI_KEY:
    raise ValueError("GEMINI_API_KEY not found in .env file.")


def get_Gemini(model_id, message, history, archivo=""):
    """
    Get response from Gemini AI model with comprehensive error handling
    
    Args:
        model_id (str): Gemini model identifier
        message (str): User message
        history (str): Conversation history
        archivo (str): Optional PDF file name
    
    Returns:
        str: AI response or error message
    """
    try:
        logger.info(f"Initializing Gemini model: {model_id}")
        
        # Validate inputs
        if not message or not message.strip():
            logger.warning("Empty message provided to Gemini")
            return "Error: Message cannot be empty"
        
        if len(message) > 10000:
            logger.warning(f"Message too long for Gemini: {len(message)} characters")
            return "Error: Message is too long (max 10,000 characters)"
        
        # Initialize model with timeout
        llm = ChatGoogleGenerativeAI(
            model=model_id,
            timeout=60,
            max_retries=2
        )
        
        # Handle file processing
        if archivo and archivo.strip():
            logger.info(f"Processing file with Gemini: {archivo}")
            try:
                # Check if file exists
                file_path = f'./archivos/{archivo}'
                if not os.path.exists(file_path):
                    logger.error(f"File not found: {archivo}")
                    return f"Error: File '{archivo}' not found"
                
                # Process file
                reply = read_file(archivo, llm, message)
                logger.info(f"Successfully processed file {archivo} with Gemini")
                return reply
                
            except FileNotFoundError:
                logger.error(f"File not found during processing: {archivo}")
                return f"Error: Could not find file '{archivo}'"
            except Exception as e:
                logger.error(f"Error processing file {archivo} with Gemini: {e}")
                return f"Error: Could not process file '{archivo}'. Please try again."
        
        # Handle regular chat
        else:
            logger.info("Processing regular chat message with Gemini")
            try:
                prompt = f"Context: el siguiente contenido es el historial de la conversación:{history} puedes usarlo para responder al usuario\nUser: {message}"
                reply = llm.invoke(prompt)
                
                if not reply or not reply.content:
                    logger.warning("Empty response from Gemini")
                    return "Error: Received empty response from AI"
                
                logger.info("Successfully received response from Gemini")
                return reply.content
                
            except Exception as e:
                logger.error(f"Error during Gemini chat: {e}")
                return "Error: Could not get response from Gemini. Please try again."
    
    except ValueError as e:
        logger.error(f"Invalid model or parameters for Gemini: {e}")
        return f"Error: Invalid model '{model_id}' or configuration"
    
    except ConnectionError as e:
        logger.error(f"Connection error with Gemini API: {e}")
        return "Error: Could not connect to Gemini. Please check your internet connection."
    
    except TimeoutError as e:
        logger.error(f"Timeout error with Gemini API: {e}")
        return "Error: Gemini request timed out. Please try again."
    
    except Exception as e:
        logger.error(f"Unexpected error in Gemini: {e}")
        return "Error: Something went wrong with Gemini. Please try again."


