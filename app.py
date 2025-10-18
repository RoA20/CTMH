import os
import tempfile
import cv2
from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
from dotenv import load_dotenv

# ----------------------------
# Load environment
# ----------------------------
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

app = Flask(__name__)

# ----------------------------
# Skills dropdown
# ----------------------------
SKILLS = [
    "underhand_throw", "overhead_throw", "sidearm_throw",
    "volleyball_underhand_serve", "volleyball_overhead_serve",
    "volleyball_forearm_pass", "volleyball_overhead_pass",
    "volleyball_block", "volleyball_pass"
]

# ----------------------------
# Gemini model
# ----------------------------
model = genai.GenerativeModel("gemini-2.0-flash")

# ----------------------------
# Temporary test route
# ----------------------------
@app.route("/test-render")
def test_render():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return "❌ GEMINI_API_KEY is NOT set on Render"
    sdk_version = getattr(genai, "__version__", "Unknown")
    return f"✅ GEMINI_API_KEY set (first 8 chars: {api_key[:8]})<br>✅ SDK version: {sdk_version}"

# ----------------------------
# Home page
# ----------------------------
@app.route("/")
def index():
    return render_template("index.html", skills=SKILLS)

# ----------------------------
# Extract a single frame from video
# ----------------------------
def extract_frame(video_path):
    cap = cv2.VideoCapture(video_path)
    success, frame = cap.read()
    cap.release()
    if not success:
        return None
    return frame

# ----------------------------
# Generate simple text description for frame
# ----------------------------
def describe_frame(frame, skill):
    """
    Placeholder description for Render-friendly deployment.
    """
    return f"Student performing {skill.replace('_',' ')}, arms and legs visible, standing on the floor."

# ----------------------------
# Analyze route
# ----------------------------
@app.route("/analyze", methods=["POST"])
def analyze():
    try:
        skill = request.form.get("skill")
        video = request.files["video"]

        # Save uploaded video
        with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as tmp:
            video.save(tmp.name)
            video_path = tmp.name

        # Extract first frame
        frame = extract_frame(video_path)
        if frame is None:
            return jsonify({"error": "No frame extracted from video."})

        # Generate placeholder description
        frame_description = describe_frame(frame, skill)

        # Prompt Gemini
        prompt = f"""
        You are a PE teacher giving encouraging feedback.
        The student is performing the skill: "{skill.replace('_',' ')}".
        Here is a description of the video frame: {frame_description}
        Respond with only 1–2 short sentences of feedback (no JSON, no formatting).
        Also give a star rating (1–5), like this example:
        Feedback: Great throw, keep your eyes on the target!
        Stars: 3
        """

        response = model.generate_content(prompt=prompt)
        text = response.text.strip()

        # Parse feedback and stars
        feedback = ""
        stars = 3
        for line in text.splitlines():
            if line.lower().startswith("feedback:"):
                feedback = line.split(":", 1)[1].strip()
            if line.lower().startswith("stars:"):
                try:
                    stars = int(line.split(":", 1)[1].strip())
                except:
                    stars = 3

        return jsonify({"feedback": feedback, "stars": stars})

    except Exception as e:
        return jsonify({"error": str(e)})

# ----------------------------
# Chat route
# ----------------------------
@app.route("/chat", methods=["POST"])
def chat():
    try:
        user_msg = request.json.get("message")
        prompt = f"""
        You are PE Buddy. A student asked: "{user_msg}".
        Reply with simple, encouraging feedback (max 2 sentences).
        """
        response = model.generate_content(prompt=prompt)
        return jsonify({"reply": response.text.strip()})
    except Exception as e:
        return jsonify({"reply": f"PE Buddy failed: {e}"})

# ----------------------------
if __name__ == "__main__":
    app.run(debug=True)
