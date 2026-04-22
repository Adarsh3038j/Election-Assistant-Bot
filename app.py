import os
from flask import Flask, request, jsonify, render_template
import google.generativeai as genai
from dotenv import load_dotenv

# 1. Environment variables load karna
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("API Key nahi mili! Kripya .env file check karein.")

genai.configure(api_key=api_key)

app = Flask(__name__)

# 2. Sabse stable aur globally available model use karna
# Dhyan rahe: Agar aapne check_models.py se koi specific naam nikala tha (jaise gemini-1.5-flash), toh yahan wahi use karein
model = genai.GenerativeModel("gemini-2.5-flash-lite")

# 3. Frontend UI dikhane ka route
@app.route('/')
def home():
    return render_template('index.html')

# 4. Chatbot ka API endpoint jahan Multilingual aur RAG logic hai
@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        user_message = data.get("message")
        
        # UI se aayi hui bhasha (language) ko receive karna, by default English rakhna
        user_language = data.get("language", "English")

        if not user_message:
            return jsonify({"error": "Message is required"}), 400

        # --- CUSTOM KNOWLEDGE (RAG) LOGIC SHURU ---
        try:
            # election_data.txt file ko padhne ki koshish karna
            with open("election_data.txt", "r", encoding="utf-8") as file:
                election_knowledge = file.read()
        except FileNotFoundError:
            election_knowledge = "Abhi koi naya official data available nahi hai."

        # AI ko Guardrails, Custom Knowledge, aur Language instruction ek sath dena
        secret_prompt = f"""
        Aap ek neutral, non-partisan election guide hain. 
        Aapka kaam sirf voting process, registration deadlines, aur election mechanics explain karna hai. 
        Kisi party ko endorse nahi karna hai.
        
        IMPORTANT INSTRUCTION: User wants the reply in {user_language} language. 
        You MUST completely translate your final answer and reply ONLY in {user_language}.
        
        Niche kuch strictly official ELECTION RULES AUR DATES di gayi hain. 
        Agar user ka sawaal in rules se juda hai, toh sirf isi data ke aadhar par jawab dein:
        
        --- OFFICIAL DATA SHURU ---
        {election_knowledge}
        --- OFFICIAL DATA KHATAM ---
        
        User ka sawaal: {user_message}
        """
        # --- CUSTOM KNOWLEDGE (RAG) LOGIC KHATAM ---

        # AI ko ab humara secret prompt jayega
        response = model.generate_content(secret_prompt)

        return jsonify({"response": response.text})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("🚀 Server start ho raha hai... UI ke liye http://127.0.0.1:5000 par jayen")
    app.run(debug=True, port=5000)