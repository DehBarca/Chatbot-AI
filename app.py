import os
import json
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError("GEMINI_API_KEY not found in .env file.")

genai.configure(api_key=API_KEY)

app = Flask(__name__)

with open('modelos/gemini_models.json', 'r') as file:
    models = json.load(file)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/modelos/", methods=["GET"])
def get_modelos():
    return jsonify(models)

@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        message = data.get("message", "").strip()
        model_id = data.get("model", "gemini-2.0-flash-lite") 

        print("model_id:", model_id)

        if not message:
            return jsonify({"error": "Empty message"}), 400

        model = genai.GenerativeModel(model_id)
        response = model.generate_content(message)
        reply = response.text

        # print("response:", response)

        return jsonify({"response": reply})

    except Exception as e:
        print("Error:", str(e))
        return jsonify({"response": "Sorry, something went wrong."}), 500

if __name__ == "__main__":
    app.run(debug=True)