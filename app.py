import os
import json
from markdown import Markdown
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
import google.generativeai as genai
from chatbotAPIs.OpenRouter import obtenerMensaje

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
Host = os.getenv("HOST", "0.0.0.0")
Port = os.getenv("PORT", 10000)

if not API_KEY:
    raise ValueError("GEMINI_API_KEY not found in .env file.")

genai.configure(api_key=API_KEY)

app = Flask(__name__)

with open('models/genText.json', 'r') as genTextFile:
    models = json.load(genTextFile)

dirpath = "./archivos"
files = os.listdir(dirpath)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/modelos/", methods=["GET"])
def get_modelos():
    return jsonify(models)

@app.route("/archivos/", methods=["GET"])
def get_archivos():
    return jsonify(files)
    
@app.route("/archivos", methods=['POST'])
def upload():
    files = request.files.getlist('file')
    for file in files:
        if file:
            file.save(f"./archivos/{file.filename}")
    return jsonify({"message": "Archivo(s) subido(s) correctamente"})

@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        message = data.get("message", "").strip()
        model_id = data.get("model", "gemini-2.0-flash") 
        provider = data.get("provider", "gemini").strip().lower()
        archivo = data.get("archivo", "").strip().lower()

        print("Archivo enviado: ", archivo)
        if not message:
            return jsonify({"error": "Empty message"}), 400
        
        if not provider:
            return jsonify({"error": "El proveedor no es válido"}), 400

        # Verificar si el modelo pertenece a DeepSeek o Gemini
        if provider == "openrouter":
            reply = obtenerMensaje(model_id, message, archivo)
            
        elif provider == "gemini":
            # Proceso para modelos de Gemini
            model = genai.GenerativeModel(model_id)
            response = model.generate_content(message)
            reply = response.text
            
        else:
            return jsonify({"error": "Model not found"}), 404
        
        return jsonify({"response": Markdown().convert(reply)})

    except Exception as e:
        print("Error:", str(e))
        return jsonify({"response": "Sorry, something went wrong."}), 500

if __name__ == "__main__":
    app.run(debug=True, host = Host, port = Port)