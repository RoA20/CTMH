import os
import tempfile
import cv2
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import google.generativeai as genai
import subprocess
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

def extract_frames(video_path, num_frames=3):
    """Extract evenly spaced frames from a video."""
    frames = []
    cap = cv2.VideoCapture(video_path)
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    if total <= 0:
        return frames

    step = max(1, total // num_frames)
    for i in range(0, total, step):
        cap.set(cv2.CAP_PROP_POS_FRAMES, i)
        success, frame = cap.read()
        if success:
            tmp_file = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False)
            cv2.imwrite(tmp_file.name, frame)
            frames.append(tmp_file.name)
        if len(frames) >= num_frames:
            break
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

        # Save uploaded .webm file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as tmp:
            video.save(tmp.name)
            video_path = tmp.name

        # Convert WebM to MP4
        mp4_path = video_path.replace(".webm", ".mp4")
        subprocess.run(["ffmpeg", "-y", "-i", video_path, mp4_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        video_path = mp4_path

        # Extract frames
        frames = extract_frames(video_path, num_frames=3)
        if not frames:
            return jsonify({"error": "No frames extracted from video."})

        # Force JSON output from Gemini
        prompt = f"""
        You are a PE teacher giving encouraging feedback.
        The student is performing the skill: "{skill.replace('_',' ')}".
        Look at the provided video frames.
        Return your answer STRICTLY in JSON format with exactly these keys:
        {{
          "feedback": "short encouraging feedback (1-2 sentences)",
          "stars": 1-5
        }}
        """

        inputs = [prompt] + [genai.upload_file(frame) for frame in frames]
        response = model.generate_content(inputs)

        # Parse JSON response
        text = response.text.strip()
        try:
            result = json.loads(text)
        except Exception:
            result = {"feedback": text, "stars": 3}  # fallback

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
