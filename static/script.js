// Populate skill dropdown dynamically
const dropdown = document.getElementById('skill-dropdown');
for (let category in skills) {
    let optgroup = document.createElement('optgroup');
    optgroup.label = category;
    skills[category].forEach(skill => {
        let option = document.createElement('option');
        option.value = skill;
        option.text = skill.replace(/_/g, " ").toUpperCase();
        optgroup.appendChild(option);
    });
    dropdown.appendChild(optgroup);
}

// Video setup
const video = document.getElementById('video');
navigator.mediaDevices.getUserMedia({ video: true, audio: false })
    .then(stream => video.srcObject = stream);

const recordBtn = document.getElementById('record-btn');
const progress = document.querySelector('.progress');

recordBtn.addEventListener('click', () => {
    if (!dropdown.value) return alert('Select a skill first!');

    const frames = [];
    progress.style.width = '0%';

    const canvas = document.createElement('canvas');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const ctx = canvas.getContext('2d');

    let count = 0;
    const interval = setInterval(() => {
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
        frames.push(canvas.toDataURL('image/png'));
        count++;
        progress.style.width = `${(count / 30) * 100}%`; // 3s / 100ms = 30 frames
        if (count >= 30) {
            clearInterval(interval);
            sendFrames(frames);
        }
    }, 100);
});

// Send frames to backend
async function sendFrames(frames) {
    const skill = dropdown.value;
    const response = await fetch('/analyze', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ skill: skill, frames: frames })
    });
    const data = await response.json();
    displayFeedback(data);
    showConfetti();
}

// Display PE Buddy feedback with colored stars
function displayFeedback(data) {
    const feedbackDiv = document.getElementById('feedback');
    feedbackDiv.innerHTML = ''; // clear previous

    const skillName = data.skill;
    const rating = data.rating;

    // Create feedback message
    const message = document.createElement('div');
    message.textContent = `${skillName} - Rating: `;
    feedbackDiv.appendChild(message);

    // Add colored stars inline
    const starColors = {
        5: ['red','orange','yellow','green','blue','indigo','violet'], // rainbow
        4: ['violet','blue','green','yellow'],
        3: ['green','yellow','orange'],
        2: ['orange','red'],
        1: ['red']
    };

    for (let i = 0; i < 5; i++) {
        let star = document.createElement('span');
        star.textContent = '⭐';
        if (i < rating) {
            if (rating === 5) {
                star.style.background = `linear-gradient(to right, ${starColors[5].join(',')})`;
                star.style.webkitBackgroundClip = 'text';
                star.style.color = 'transparent';
            } else {
                star.style.color = starColors[rating][i] || starColors[rating][0];
            }
        } else {
            star.style.color = '#ccc';
        }
        message.appendChild(star);
    }

    // Add textual feedback below
    const text = document.createElement('div');
    text.textContent = data.feedback;
    text.style.marginTop = '5px';
    feedbackDiv.appendChild(text);
}

// Confetti animation
function showConfetti() {
    const container = document.createElement('div');
    container.style.position = 'fixed';
    container.style.top = '0';
    container.style.left = '0';
    container.style.width = '100%';
    container.style.height = '100%';
    container.style.pointerEvents = 'none';
    document.body.appendChild(container);

    for (let i=0; i<100; i++) {
        const confetti = document.createElement('div');
        confetti.textContent = '🎉';
        confetti.style.position = 'absolute';
        confetti.style.fontSize = `${Math.random()*20 + 10}px`;
        confetti.style.left = `${Math.random()*100}vw`;
        confetti.style.top = `${Math.random()*-100}vh`;
        confetti.style.animation = `fall ${2+Math.random()*3}s linear forwards`;
        container.appendChild(confetti);
    }
    setTimeout(() => container.remove(), 4000);
}

// Chat functionality
const chatBtn = document.getElementById('chat-btn');
const chatInput = document.getElementById('chat-input');
const chatBox = document.getElementById('chat-box');

chatBtn.addEventListener('click', () => {
    const msg = chatInput.value.trim();
    if (!msg) return;
    const userMsg = document.createElement('div');
    userMsg.textContent = `You: ${msg}`;
    chatBox.appendChild(userMsg);

    setTimeout(() => {
        const buddyMsg = document.createElement('div');
        buddyMsg.textContent = `PE Buddy: Great question! Keep practicing your form.`;
        chatBox.appendChild(buddyMsg);
        chatBox.scrollTop = chatBox.scrollHeight;
    }, 1000);

    chatInput.value = '';
});

// Confetti keyframes
const styleSheet = document.createElement("style")
styleSheet.type = "text/css"
styleSheet.innerText = `
@keyframes fall {
    to { transform: translateY(100vh) rotate(360deg);}
}`;
document.head.appendChild(styleSheet);
