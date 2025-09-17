import os
import logging
from typing import Optional
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_openai import OpenAIEmbeddings

# Configure logger
logger = logging.getLogger(__name__)

# Load environment variables with error handling
try:
    load_dotenv()
    OPENAI_KEY = os.getenv("OPENAI_API_KEY")
    
    if not OPENAI_KEY:
        logger.error("OPENAI_API_KEY not found in .env file")
        raise ValueError("OPENAI_API_KEY not found in .env file.")
    
    os.environ["OPENAI_API_KEY"] = OPENAI_KEY
    logger.info("OpenAI API key loaded successfully")
    
except Exception as e:
    logger.error(f"Error loading OpenAI configuration: {e}")
    raise

# Optimized system prompt with better instructions
SYSTEM_PROMPT = (
    "Eres un asistente especializado en análisis de documentos PDF. "
    "Analiza el contexto proporcionado y responde la pregunta del usuario de manera precisa y útil. "
    "Instrucciones:\n"
    "1. Usa SOLO la información del contexto proporcionado\n"
    "2. Si no encuentras información relevante, indica claramente que no está en el documento\n"
    "3. Proporciona respuestas concisas pero completas\n"
    "4. Cita información específica cuando sea posible\n"
    "5. Responde en español\n\n"
    "Contexto del documento:\n{context}\n"
)

# Global prompt template (optimized for reuse)
PROMPT_TEMPLATE = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    ("human", "Pregunta: {input}")
])

# Cache for embeddings model (singleton pattern)
_embeddings_instance = None

def get_embeddings_instance() -> OpenAIEmbeddings:
    """
    Get or create a singleton embeddings instance for efficiency
    
    Returns:
        OpenAIEmbeddings: Configured embeddings instance
    """
    global _embeddings_instance
    
    if _embeddings_instance is None:
        try:
            _embeddings_instance = OpenAIEmbeddings(
                model="text-embedding-3-small",  # More efficient model
                chunk_size=1000,  # Optimize batch processing
                max_retries=3
            )
            logger.info("Embeddings instance created successfully")
        except Exception as e:
            logger.error(f"Error creating embeddings instance: {e}")
            # Fallback to default
            _embeddings_instance = OpenAIEmbeddings()
    
    return _embeddings_instance

def read_file(file: str, llm, user_input: str) -> str:
    """
    Process a PDF file and answer questions based on its content with comprehensive error handling
    
    Args:
        file (str): PDF filename in ./archivos/ directory
        llm: Language model instance
        user_input (str): User's question about the document
    
    Returns:
        str: Answer based on document content or error message
    """
    try:
        logger.info(f"Processing file: {file} with query: '{user_input[:50]}...'")
        
        # Validate user input only (file validation is done in validate_pdf_file)
        if not user_input or not user_input.strip():
            logger.warning("Empty user input provided")
            return "Error: No se proporcionó una pregunta"
        
        # Use the validation function - it handles all file validation logic
        if not validate_pdf_file(file):
            logger.error(f"PDF validation failed for: {file}")
            # Return appropriate error message - validation function logs specific issues
            return f"Error: El archivo '{file}' no es válido, no existe o no se puede procesar"
        
        # At this point, we know the file is valid - get the filepath
        filepath = f"./archivos/{file.strip()}"
        
        # Load PDF (we know it's valid from validation)
        try:
            logger.debug(f"Loading validated PDF: {filepath}")
            loader = PyPDFLoader(filepath)
            docs = loader.load()
            
            logger.info(f"Successfully loaded {len(docs)} pages from {file}")
            
        except Exception as e:
            logger.error(f"Error loading validated PDF {file}: {e}")
            return f"Error: No se pudo cargar el archivo '{file}' a pesar de pasar la validación"
        
        # Text splitting with optimized parameters
        try:
            logger.debug("Splitting document into chunks")
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1200,      # Slightly larger chunks for better context
                chunk_overlap=300,    # More overlap for better continuity
                length_function=len,
                separators=["\n\n", "\n", " ", ""]  # Better separation logic
            )
            
            splits = text_splitter.split_documents(docs)
            
            if not splits:
                logger.warning(f"No text chunks created from {file}")
                return f"Error: El archivo '{file}' parece estar vacío o no contiene texto extraíble"
            
            logger.info(f"Created {len(splits)} text chunks from {file}")
            
        except Exception as e:
            logger.error(f"Error splitting document {file}: {e}")
            return f"Error: No se pudo procesar el contenido del archivo '{file}'"
        
        # Create vector store with error handling
        try:
            logger.debug("Creating vector store and embeddings")
            embeddings = get_embeddings_instance()
            
            # Create vector store with optimized settings
            vectorstore = Chroma.from_documents(
                documents=splits,
                embedding=embeddings,
                collection_metadata={"hnsw:space": "cosine"}  # Better similarity metric
            )
            
            # Configure retriever with optimized parameters
            retriever = vectorstore.as_retriever(
                search_type="similarity",
                search_kwargs={
                    "k": 8  # Get more chunks to filter manually
                }
            )
            
            logger.info("Vector store created successfully")
            
        except Exception as e:
            logger.error(f"Error creating vector store for {file}: {e}")
            return f"Error: No se pudo crear el índice de búsqueda para '{file}'"
        
        # Create RAG chain and get answer
        try:
            logger.debug("Creating RAG chain and processing query")
            
            # Create optimized chains
            question_answer_chain = create_stuff_documents_chain(llm, PROMPT_TEMPLATE)
            rag_chain = create_retrieval_chain(retriever, question_answer_chain)
            
            # Process query
            results = rag_chain.invoke({"input": user_input.strip()})
            
            if not results or 'answer' not in results:
                logger.warning("No answer generated from RAG chain")
                return "Error: No se pudo generar una respuesta"
            
            answer = results['answer']
            
            if not answer or answer.strip() == "":
                logger.warning("Empty answer generated")
                return "No se encontró información relevante en el documento para responder tu pregunta"
            
            logger.info(f"Successfully generated answer for query about {file}")
            return answer.strip()
            
        except Exception as e:
            logger.error(f"Error in RAG processing for {file}: {e}")
            return f"Error: No se pudo procesar la consulta sobre '{file}'"
    
    except Exception as e:
        logger.error(f"Critical error in read_file function: {e}")
        return "Error: Ocurrió un error inesperado al procesar el archivo"

def validate_pdf_file(filename: str) -> bool:
    """
    Comprehensive validation of PDF file with detailed logging
    
    Args:
        filename (str): PDF filename to validate
    
    Returns:
        bool: True if file is valid and readable, False otherwise
    """
    try:
        # Check if filename is provided and not empty
        if not filename or not filename.strip():
            logger.warning("validate_pdf_file: Empty or None filename provided")
            return False
        
        # Construct file path
        filepath = f"./archivos/{filename.strip()}"
        logger.debug(f"validate_pdf_file: Checking file at: {filepath}")
        
        # Check if file exists
        if not os.path.exists(filepath):
            logger.warning(f"validate_pdf_file: File does not exist: {filepath}")
            return False
        
        # Check if it's a file (not a directory)
        if not os.path.isfile(filepath):
            logger.warning(f"validate_pdf_file: Path is not a file: {filepath}")
            return False
        
        # Check file extension
        if not filepath.lower().endswith('.pdf'):
            logger.warning(f"validate_pdf_file: File is not a PDF: {filename}")
            return False
        
        # Check file size (must be > 0)
        file_size = os.path.getsize(filepath)
        if file_size == 0:
            logger.warning(f"validate_pdf_file: PDF file is empty: {filename}")
            return False
        
        # Try to open and validate PDF structure
        try:
            with open(filepath, 'rb') as f:
                # Check PDF header
                header = f.read(4)
                if header != b'%PDF':
                    logger.warning(f"validate_pdf_file: Invalid PDF header in: {filename}")
                    return False
            
            # Try to load with PyPDFLoader as final validation
            loader = PyPDFLoader(filepath)
            docs = loader.load()
            
            if not docs or len(docs) == 0:
                logger.warning(f"validate_pdf_file: No content could be extracted from: {filename}")
                return False
            
            logger.debug(f"validate_pdf_file: Successfully validated PDF: {filename} ({len(docs)} pages, {file_size} bytes)")
            return True
            
        except Exception as pdf_error:
            logger.warning(f"validate_pdf_file: PDF structure validation failed for {filename}: {pdf_error}")
            return False
        
    except Exception as e:
        logger.error(f"validate_pdf_file: Unexpected error validating {filename}: {e}")
        return False

def get_file_info(filename: str) -> Optional[dict]:
    """
    Get information about a PDF file
    
    Args:
        filename (str): PDF filename
    
    Returns:
        dict: File information or None if error
    """
    try:
        if not validate_pdf_file(filename):
            return None
        
        filepath = f"./archivos/{filename.strip()}"
        stat = os.stat(filepath)
        
        # Try to load and get page count
        loader = PyPDFLoader(filepath)
        docs = loader.load()
        
        return {
            "filename": filename,
            "size_bytes": stat.st_size,
            "size_mb": round(stat.st_size / (1024 * 1024), 2),
            "page_count": len(docs),
            "last_modified": stat.st_mtime
        }
        
    except Exception as e:
        logger.error(f"Error getting file info for {filename}: {e}")
        return None