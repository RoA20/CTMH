from flask import Flask, request, send_from_directory, jsonify
import os
import io
import cv2
from PIL import Image
import google.generativeai as genai
import re

app = Flask(__name__)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("Please set your GEMINI_API_KEY environment variable.")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

@app.route('/')
def home():
    return send_from_directory('.', 'index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    sport = request.form.get('sport', 'general')
    skill = request.form.get('skill', 'general')
    video = request.files.get('video')

    if not video:
        return jsonify({"error": "No video uploaded"}), 400

    temp_video_path = 'temp_chunk.webm'
    video.save(temp_video_path)

    cap = cv2.VideoCapture(temp_video_path)
    ret, frame = cap.read()
    cap.release()

    if not ret:
        return jsonify({"error": "Failed to read video frame"}), 400

    _, jpeg = cv2.imencode('.jpg', frame)
    image_bytes = jpeg.tobytes()

    prompt = (
        f"Evaluate the student's performance in {sport} "
        f"for the skill: {skill}. "
        "Provide a rating out of 10, detailed feedback, and next steps to improve."
    )

    try:
        response = model.generate_content([
            prompt,
            Image.open(io.BytesIO(image_bytes))
        ])
        feedback_text = response.text.strip()

        rating = "AI generated"
        match = re.search(r'(\d+(\.\d+)?)\s*(/|out of)?\s*10', feedback_text, re.IGNORECASE)
        if match:
            rating = match.group(1)
    except Exception as e:
        feedback_text = f"⚠️ Gemini Error: {e}"
        rating = "N/A"

    if os.path.exists(temp_video_path):
        os.remove(temp_video_path)

    return jsonify({
        "rating": rating,
        "feedback": feedback_text,
        "next_steps": "Included in feedback."
    })

if __name__ == '__main__':
    app.run(debug=True)
