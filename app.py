import os
import json
import logging
from datetime import datetime
from markdown import Markdown
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
from chatbotAPIs.OpenRouter import get_OpenRouter
from chatbotAPIs.Gemini import get_Gemini
from chatbotAPIs.Together import get_Together
from utils.History import make_history

# Clear log file at startup
try:
    open('app.log', 'w').close()
except:
    pass  # If file doesn't exist or can't be cleared, continue anyway

# Configure logging first
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables with basic error handling
try:
    load_dotenv()
    logger.info("Environment file (.env) loaded successfully")
except:
    logger.warning("Could not load .env file")

try:
    Host = os.getenv("HOST", "0.0.0.0")
    Port = int(os.getenv("PORT", "10000"))
    logger.info("Environment variables loaded correctly")
except:
    logger.error("Error with environment variables, using defaults")
    Host = "0.0.0.0"
    Port = 10000

app = Flask(__name__)

# Log startup
logger.info(f"Starting Chatbot AI application on {Host}:{Port}")

# Load models with comprehensive error handling
try:
    logger.info("Loading models from genText.json")
    with open('models/genText.json', 'r') as genTextFile:
        models = json.load(genTextFile)
    logger.info(f"Successfully loaded {len(models)} models")
except FileNotFoundError:
    logger.error("genText.json file not found, using default model")
    models = [{"id": "gemini-2.0-flash", "nombre": "Gemini 2.0 Flash", "provider": "gemini"}]
except json.JSONDecodeError as e:
    logger.error(f"Invalid JSON in genText.json: {e}")
    models = [{"id": "gemini-2.0-flash", "nombre": "Gemini 2.0 Flash", "provider": "gemini"}]
except Exception as e:
    logger.error(f"Unexpected error loading models: {e}")
    models = [{"id": "gemini-2.0-flash", "nombre": "Gemini 2.0 Flash", "provider": "gemini"}]

dirpath = "./archivos"

# Create directory if it doesn't exist
if not os.path.exists(dirpath):
    logger.info(f"Creating directory: {dirpath}")
    os.makedirs(dirpath)

@app.route("/")
def index():
    try:
        logger.info("Serving index page")
        return render_template("index.html")
    except Exception as e:
        logger.error(f"Error rendering index page: {e}")
        return jsonify({"error": "Could not load page"}), 500

@app.route("/modelos/", methods=["GET"])
def get_modelos():
    try:
        logger.info("Getting models list")
        return jsonify(models)
    except Exception as e:
        logger.error(f"Error getting models: {e}")
        return jsonify({"error": "Could not get models"}), 500

@app.route("/archivos/", methods=["GET"])
def get_archivos():
    try:
        logger.info("Getting files list")
        files = os.listdir(dirpath)
        logger.info(f"Found {len(files)} files in {dirpath}")
        return jsonify(files)
    except Exception as e:
        logger.error(f"Error getting files: {e}")
        return jsonify([]), 200
    
@app.route("/archivos", methods=['POST'])
def upload():
    try:
        logger.info("Processing file upload request")
        
        if 'file' not in request.files:
            logger.warning("No files provided in upload request")
            return jsonify({"error": "No files provided"}), 400
        
        filesUploaded = request.files.getlist('file')
        uploaded_files = []
        
        logger.info(f"Processing {len(filesUploaded)} files")
        
        for file in filesUploaded:
            if file and file.filename:
                original_filename = file.filename
                # Basic filename sanitization
                filename = file.filename.replace("..", "").replace("/", "").replace("\\", "")
                
                try:
                    file_path = f"./archivos/{filename}"
                    file.save(file_path)
                    uploaded_files.append(filename)
                    logger.info(f"Successfully uploaded file: {original_filename} -> {filename}")
                except Exception as e:
                    logger.error(f"Failed to save file {original_filename}: {e}")
                    continue
        
        if not uploaded_files:
            logger.warning("No valid files were uploaded")
            return jsonify({"error": "No valid files uploaded"}), 400
        
        files = os.listdir(dirpath)
        logger.info(f"Upload complete. {len(uploaded_files)} files uploaded successfully")
        return jsonify({"message": "Archivo(s) subido(s) correctamente", "allFiles": files})
    
    except Exception as e:
        logger.error(f"Error in upload process: {e}")
        return jsonify({"error": "Could not upload files"}), 500

@app.route("/chat", methods=["POST"])
def chat():
    start_time = datetime.now()
    try:
        logger.info("Processing chat request")
        
        # Basic request validation
        if not request.is_json:
            logger.warning("Received non-JSON request")
            return jsonify({"error": "Request must be JSON"}), 400
        
        data = request.get_json()
        if not data:
            logger.warning("Received empty JSON request")
            return jsonify({"error": "Empty request"}), 400
        
        message = data.get("message", "").strip()
        model_id = data.get("model", "gemini-2.0-flash") 
        provider = data.get("provider", "gemini").strip().lower()
        archivo = data.get("archivo", "").strip()

        logger.info(f"Chat request - Provider: {provider}, Model: {model_id}, Message length: {len(message)}, File: {archivo}")

        # Simple validations
        if not message:
            logger.warning("Empty message received")
            return jsonify({"error": "Message is required"}), 400
        
        if len(message) > 4000:
            logger.warning(f"Message too long: {len(message)} characters")
            return jsonify({"error": "Message too long"}), 400
        
        if not provider:
            logger.warning("No provider specified")
            return jsonify({"error": "Provider is required"}), 400
        
        if not model_id:
            logger.warning("No model specified")
            return jsonify({"error": "Model is required"}), 400
        
        # Get history
        try:
            logger.debug("Retrieving conversation history")
            history = make_history("","")
            logger.debug("Successfully retrieved history")
        except Exception as e:
            logger.error(f"Could not get history: {e}")
            history = ""
        
        # Call the appropriate model
        reply = None
        try:
            logger.info(f"Calling {provider} model: {model_id}")
            match provider:
                case "openrouter": 
                    reply = get_OpenRouter(model_id, message, history, archivo)
                case "gemini":
                    reply = get_Gemini(model_id, message, history, archivo)
                case "together":
                    reply = get_Together(model_id, message, history, archivo)
                case _:
                    logger.error(f"Unsupported provider: {provider}")
                    return jsonify({"error": "Unsupported provider"}), 400
            
            if not reply:
                logger.error(f"No response from {provider} model {model_id}")
                return jsonify({"error": "No response from model"}), 503
            
            logger.info(f"Received response from {provider} - Length: {len(str(reply))}")
                
        except Exception as e:
            logger.error(f"Model error ({provider}/{model_id}): {e}")
            return jsonify({"error": f"Model unavailable: {provider}"}), 503
        
        # Save to history
        try:
            logger.debug("Saving conversation to history")
            make_history(message, reply)
            logger.debug("Successfully saved to history")
        except Exception as e:
            logger.error(f"Could not save history: {e}")
        
        # Convert to markdown
        try:
            logger.debug("Converting response to markdown")
            markdown_reply = Markdown().convert(reply)
            
            # Log successful completion
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            logger.info(f"Chat request completed successfully in {duration:.2f} seconds")
            
            return jsonify({"response": markdown_reply})
        except Exception as e:
            logger.error(f"Markdown conversion failed: {e}")
            return jsonify({"response": str(reply)})

    except Exception as e:
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        logger.error(f"Chat request failed after {duration:.2f} seconds: {e}")
        return jsonify({"error": "Something went wrong"}), 500

# Comprehensive error handlers
@app.errorhandler(404)
def not_found(error):
    logger.warning(f"404 error: {request.url}")
    return jsonify({"error": "Not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"500 error: {error}")
    return jsonify({"error": "Internal server error"}), 500

@app.errorhandler(400)
def bad_request(error):
    logger.warning(f"400 error: {error}")
    return jsonify({"error": "Bad request"}), 400

@app.errorhandler(413)
def payload_too_large(error):
    logger.warning(f"413 error: Payload too large")
    return jsonify({"error": "File too large"}), 413

if __name__ == "__main__":
    logger.info("Starting Flask application in debug mode")
    app.run(debug=True, host = Host, port = Port)