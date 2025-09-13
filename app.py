import os
import tempfile
import cv2
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import google.generativeai as genai
import json

# Load environment variables
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

app = Flask(__name__)

# Skills dropdown
SKILLS = [
    "underhand_throw", "overhead_throw", "sidearm_throw",
    "volleyball_underhand_serve", "volleyball_overhead_serve",
    "volleyball_forearm_pass", "volleyball_overhead_pass",
    "volleyball_block", "volleyball_pass"
]

# Gemini model
model = genai.GenerativeModel("gemini-1.5-flash")

def extract_single_frame(video_path):
    """Extract only the first frame to save memory."""
    frames = []
    cap = cv2.VideoCapture(video_path)
    success, frame = cap.read()
    if success:
        tmp_file = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False)
        cv2.imwrite(tmp_file.name, frame)
        frames.append(tmp_file.name)
    cap.release()
    return frames

@app.route("/")
def index():
    return render_template("index.html", skills=SKILLS)

@app.route("/analyze", methods=["POST"])
def analyze():
    try:
        skill = request.form.get("skill")
        video = request.files["video"]

        # Save video to disk
        with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as tmp:
            video.save(tmp.name)
            video_path = tmp.name

        # Extract only 1 frame (first frame)
        frames = extract_single_frame(video_path)
        if not frames:
            return jsonify({"error": "No frame extracted from video."})

        # Gemini prompt (force JSON)
        prompt = f"""
        You are a PE teacher giving encouraging feedback.
        The student is performing the skill: "{skill.replace('_',' ')}".
        Look at the provided video frame.
        Return your answer STRICTLY in JSON format with keys:
        {{
          "feedback": "short encouraging feedback (1-2 sentences)",
          "stars": 1-5
        }}
        """

        inputs = [prompt] + [genai.upload_file(frames[0])]
        response = model.generate_content(inputs)

        text = response.text.strip()
        try:
            result = json.loads(text)
        except Exception:
            result = {"feedback": text, "stars": 3}

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)})

@app.route("/chat", methods=["POST"])
def chat():
    try:
        user_msg = request.json.get("message")
        prompt = f"""
        You are PE Buddy. A student asked: "{user_msg}".
        Reply with simple, encouraging feedback (max 2 sentences).
        """
        response = model.generate_content(prompt)
        return jsonify({"reply": response.text.strip()})
    except Exception as e:
        return jsonify({"reply": f"PE Buddy failed: {e}"})

if __name__ == "__main__":
    app.run(debug=True)
