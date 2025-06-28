import os
import json
from markdown import Markdown
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
from chatbotAPIs.OpenRouter import get_OpenRouter
from chatbotAPIs.Gemini import get_Gemini
from chatbotAPIs.Together import get_Together

load_dotenv()
Host = os.getenv("HOST", "0.0.0.0")
Port = os.getenv("PORT", 10000)

app = Flask(__name__)

with open('models/genText.json', 'r') as genTextFile:
    models = json.load(genTextFile)

dirpath = "./archivos"


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/modelos/", methods=["GET"])
def get_modelos():
    return jsonify(models)

@app.route("/archivos/", methods=["GET"])
def get_archivos():
    files = os.listdir(dirpath)
    return jsonify(files)
    
@app.route("/archivos", methods=['POST'])
def upload():
    
    filesUploaded = request.files.getlist('file')
    for file in filesUploaded:
        if file:
            file.save(f"./archivos/{file.filename}")
            
    files = os.listdir(dirpath)
    return jsonify({"message": "Archivo(s) subido(s) correctamente", "allFiles": [file for file in files]})

@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        message = data.get("message", "").strip()
        model_id = data.get("model", "gemini-2.0-flash") 
        provider = data.get("provider", "gemini").strip().lower()
        archivo = data.get("archivo", "").strip().lower()

        if not message:
            return jsonify({"error": "Empty message"}), 400
        
        if not provider:
            return jsonify({"error": "El proveedor no es válido"}), 400
        
        if not model_id:
            return jsonify({"error": "El modelo no es válido"}), 400
        
        # Verificar si el modelo pertenece a Openrouter o Gemini
        match provider:
            case "openrouter": 
                reply = get_OpenRouter(model_id, message) # Proceso para modelos de Openrouter
            case "gemini":
                reply = get_Gemini(model_id, message) # Proceso para modelos de Gemini
            case "together":
                reply = get_Together(model_id, message)
            case _:
                return jsonify({"error": "Model not found"}), 404
                
        return jsonify({"response": Markdown().convert(reply)})

    except Exception as e:
        print("Error:", str(e))
        return jsonify({"response": "Sorry, something went wrong."}), 500

if __name__ == "__main__":
    app.run(debug=True, host = Host, port = Port)