const video = document.getElementById("video");
const canvas = document.getElementById("canvas");
const recordBtn = document.getElementById("recordBtn");
const progress = document.getElementById("progress");
const feedbackDiv = document.getElementById("feedback");
const starsDiv = document.getElementById("stars");
const cheerSound = document.getElementById("cheerSound");

const chatbox = document.getElementById("chatbox");
const chatInput = document.getElementById("chatInput");
const chatSend = document.getElementById("chatSend");

// ✅ Use back-facing camera
navigator.mediaDevices.getUserMedia({ video: { facingMode: "environment" } })
  .then(stream => { video.srcObject = stream; })
  .catch(err => console.error("Camera error:", err));

// Convert rating to star emojis
function getStars(rating) {
  switch (rating) {
    case 1: return "⭐";
    case 2: return "⭐ ⭐";
    case 3: return "⭐ ⭐ ⭐";
    case 4: return "⭐ ⭐ ⭐ ⭐";
    case 5: return "🌈⭐ 🌈⭐ 🌈⭐ 🌈⭐ 🌈⭐";
    default: return "";
  }
}

// Handle recording & analysis
recordBtn.addEventListener("click", () => {
  progress.style.width = "0%";
  let width = 0;
  const interval = setInterval(() => {
    width += 100 / 30; // 3s → 30 steps
    progress.style.width = width + "%";
  }, 100);

  setTimeout(() => {
    clearInterval(interval);
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    canvas.getContext("2d").drawImage(video, 0, 0);

    const skill = document.getElementById("skill").value;
    fetch("/analyze", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ skill })
    })
      .then(res => res.json())
      .then(data => {
        feedbackDiv.textContent = data.feedback;
        starsDiv.textContent = getStars(data.stars);

        if (data.stars === 5) {
          cheerSound.play();
          confetti({ particleCount: 120, spread: 70, origin: { y: 0.6 } });
        }
      });
  }, 3000);
});

// ✅ PE Buddy Chat
chatSend.addEventListener("click", () => {
  const message = chatInput.value.trim();
  if (!message) return;

  const userMsg = document.createElement("div");
  userMsg.className = "user-msg";
  userMsg.textContent = "You: " + message;
  chatbox.appendChild(userMsg);

  fetch("/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message })
  })
    .then(res => res.json())
    .then(data => {
      const botMsg = document.createElement("div");
      botMsg.className = "bot-msg";
      botMsg.textContent = "PE Buddy: " + data.reply;
      chatbox.appendChild(botMsg);
      chatbox.scrollTop = chatbox.scrollHeight;
    });

  chatInput.value = "";
});
