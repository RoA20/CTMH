from flask import Flask, render_template, request, jsonify
import random

app = Flask(__name__)

skills = {
    "Throws": ["underhand_throw", "overhead_throw", "sidearm_throw"],
    "Volleyball": [
        "volleyball_overhead_serve",
        "volleyball_underhand_serve",
        "volleyball_forearm_pass",
        "volleyball_overhead_pass",
        "volleyball_block",
        "volleyball_pass"
    ]
}

# Predefined feedback dictionary
feedback_dict = {
    "underhand_throw": [
        {"stars":5,"feedback":"Excellent underhand throw!"},
        {"stars":4,"feedback":"Very good underhand throw!"},
        {"stars":3,"feedback":"Good effort! Practice your underhand throw technique."},
        {"stars":2,"feedback":"Needs improvement. Focus on stance and follow-through."},
        {"stars":1,"feedback":"Keep trying! Watch your form carefully."}
    ],
    "overhead_throw":[
        {"stars":5,"feedback":"Excellent overhead throw!"},
        {"stars":4,"feedback":"Very good overhead throw!"},
        {"stars":3,"feedback":"Good effort! Practice your overhead throw technique."},
        {"stars":2,"feedback":"Needs improvement. Focus on arm motion and follow-through."},
        {"stars":1,"feedback":"Keep trying! Watch your overhead form."}
    ],
    "sidearm_throw":[
        {"stars":5,"feedback":"Excellent sidearm throw!"},
        {"stars":4,"feedback":"Very good sidearm throw!"},
        {"stars":3,"feedback":"Good effort! Practice your sidearm throw technique."},
        {"stars":2,"feedback":"Needs improvement. Focus on stance and wrist action."},
        {"stars":1,"feedback":"Keep trying! Watch your sidearm form."}
    ],
    "volleyball_overhead_serve":[
        {"stars":5,"feedback":"Excellent overhead serve!"},
        {"stars":4,"feedback":"Very good overhead serve!"},
        {"stars":3,"feedback":"Good effort! Keep practicing your serve."},
        {"stars":2,"feedback":"Needs improvement. Focus on toss and follow-through."},
        {"stars":1,"feedback":"Keep trying! Watch your arm swing."}
    ],
    "volleyball_underhand_serve":[
        {"stars":5,"feedback":"Excellent underhand serve!"},
        {"stars":4,"feedback":"Very good underhand serve!"},
        {"stars":3,"feedback":"Good effort! Keep practicing your serve."},
        {"stars":2,"feedback":"Needs improvement. Focus on swing and aim."},
        {"stars":1,"feedback":"Keep trying! Watch your form."}
    ],
    "volleyball_forearm_pass":[
        {"stars":5,"feedback":"Excellent forearm pass!"},
        {"stars":4,"feedback":"Very good forearm pass!"},
        {"stars":3,"feedback":"Good effort! Keep practicing your technique."},
        {"stars":2,"feedback":"Needs improvement. Focus on stance and platform."},
        {"stars":1,"feedback":"Keep trying! Watch your positioning."}
    ],
    "volleyball_overhead_pass":[
        {"stars":5,"feedback":"Excellent overhead pass!"},
        {"stars":4,"feedback":"Very good overhead pass!"},
        {"stars":3,"feedback":"Good effort! Keep practicing your overhead pass."},
        {"stars":2,"feedback":"Needs improvement. Focus on hand position and follow-through."},
        {"stars":1,"feedback":"Keep trying! Watch your technique."}
    ],
    "volleyball_block":[
        {"stars":5,"feedback":"Excellent block!"},
        {"stars":4,"feedback":"Very good block!"},
        {"stars":3,"feedback":"Good effort! Keep practicing your timing."},
        {"stars":2,"feedback":"Needs improvement. Focus on jump and hand position."},
        {"stars":1,"feedback":"Keep trying! Watch your stance."}
    ],
    "volleyball_pass":[
        {"stars":5,"feedback":"Excellent pass!"},
        {"stars":4,"feedback":"Very good pass!"},
        {"stars":3,"feedback":"Good effort! Keep practicing your technique."},
        {"stars":2,"feedback":"Needs improvement. Focus on stance and direction."},
        {"stars":1,"feedback":"Keep trying! Watch your form."}
    ]
}

@app.route('/')
def index():
    return render_template('index.html', skills=skills)

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.json
    name = data.get('name', 'Student')
    skill = data.get('skill')
    frames = data.get('frames', [])

    # Simulate AI rating (replace with actual AI call later)
    rating = random.choices([1,2,3,4,5], weights=[1,1,2,4,7])[0]

    # Get feedback
    skill_feedback_list = feedback_dict.get(skill, [])
    feedback_entry = next((f for f in skill_feedback_list if f["stars"] == rating), None)
    feedback_text = feedback_entry["feedback"] if feedback_entry else "Keep practicing!"

    # Return name, skill, rating, feedback
    return jsonify({
        "name": name,
        "skill": skill.replace("_", " ").title(),
        "rating": rating,
        "feedback": feedback_text
    })

if __name__ == '__main__':
    app.run(debug=True)
