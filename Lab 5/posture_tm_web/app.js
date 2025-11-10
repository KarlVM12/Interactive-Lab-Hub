const MODEL_DIR = "../posture_teachable_machine/";
const BAD_POSTURE = new Set(["slouching", "leaning"]);
const ALERT_AFTER_MS = 10_000;
const ALERT_COOLDOWN_MS = 20_000;
const SMOOTHING_WINDOW = 5;

let model;
let webcam;
let ctx;
let rafId;
let isRunning = false;
let lastBadStart = null;
let lastAlert = 0;
const labelHistory = [];

const statusLabel = document.getElementById("status-label");
const statusConfidence = document.getElementById("status-confidence");
const statusMessage = document.getElementById("status-message");
const progressFill = document.getElementById("progress-fill");
const predictionContainer = document.getElementById("predictions");
const startBtn = document.getElementById("start-btn");
const stopBtn = document.getElementById("stop-btn");
const audioEl = document.getElementById("coach-audio");

async function loadModel() {
  if (model) {
    return model;
  }
  const modelURL = MODEL_DIR + "model.json";
  const metadataURL = MODEL_DIR + "metadata.json";
  model = await tmPose.load(modelURL, metadataURL);
  return model;
}

async function setupWebcam() {
  const size = 320;
  const flip = true;
  webcam = new tmPose.Webcam(size, size, flip);
  await webcam.setup();
  await webcam.play();
  document.getElementById("canvas").width = size;
  document.getElementById("canvas").height = size;
  ctx = document.getElementById("canvas").getContext("2d");
}

function updateLabelHistory(label) {
  labelHistory.push(label);
  while (labelHistory.length > SMOOTHING_WINDOW) {
    labelHistory.shift();
  }
}

function smoothedLabel() {
  if (!labelHistory.length) {
    return null;
  }
  const counts = labelHistory.reduce((acc, lbl) => {
    acc[lbl] = (acc[lbl] || 0) + 1;
    return acc;
  }, {});
  return Object.entries(counts).sort((a, b) => b[1] - a[1])[0][0];
}

function updateUI(sortedPreds, pose) {
  const best = sortedPreds[0];
  updateLabelHistory(best.label);
  const label = smoothedLabel();
  const confidence = sortedPreds.find((p) => p.label === label)?.probability || 0;

  const friendly = label ? label.toUpperCase() : "UNKNOWN";
  statusLabel.textContent = friendly;
  statusConfidence.textContent = `${(confidence * 100).toFixed(1)}%`;

  const now = performance.now();
  if (label && BAD_POSTURE.has(label)) {
    if (!lastBadStart) {
      lastBadStart = now;
    }
    const elapsed = now - lastBadStart;
    const ratio = Math.min(1, elapsed / ALERT_AFTER_MS);
    progressFill.style.width = `${ratio * 100}%`;
    statusMessage.textContent = ratio >= 1 ? "Audio reminder playing" : "Sit taller";

    if (ratio >= 1 && now - lastAlert > ALERT_COOLDOWN_MS) {
      triggerAudio();
      lastAlert = now;
      lastBadStart = now; // restart timer after alert
    }
  } else {
    statusMessage.textContent = "Nice posture";
    progressFill.style.width = "0%";
    lastBadStart = null;
  }

  predictionContainer.innerHTML = sortedPreds
    .map(
      (p) => `
        <div class="prediction ${p.label === label ? "active" : ""}">
          <span>${p.label}</span>
          <span>${(p.probability * 100).toFixed(1)}%</span>
        </div>`
    )
    .join("");

  ctx.drawImage(webcam.canvas, 0, 0);
  if (pose) {
    const minConfidence = 0.5;
    tmPose.drawKeypoints(pose.keypoints, minConfidence, ctx);
    tmPose.drawSkeleton(pose.keypoints, minConfidence, ctx);
  }
}

function triggerAudio() {
  if (!audioEl) return;
  audioEl.currentTime = 0;
  audioEl.play().catch((err) => {
    console.warn("Audio play blocked", err);
  });
}

async function predictLoop() {
  const { pose, posenetOutput } = await model.estimatePose(webcam.canvas);
  const prediction = await model.predict(posenetOutput);
  const sortedPreds = prediction
    .map((p) => ({ label: p.className.toLowerCase(), probability: p.probability }))
    .sort((a, b) => b.probability - a.probability);

  updateUI(sortedPreds, pose);
  if (isRunning) {
    rafId = requestAnimationFrame(predictLoop);
  }
}

async function startSystem() {
  startBtn.disabled = true;
  stopBtn.disabled = false;
  statusMessage.textContent = "Loading model…";
  try {
    await loadModel();
    await setupWebcam();
    await warmAudio();
    isRunning = true;
    predictLoop();
  } catch (err) {
    console.error(err);
    statusMessage.textContent = "Failed to start (see console)";
    startBtn.disabled = false;
    stopBtn.disabled = true;
  }
}

async function warmAudio() {
  if (!audioEl) return;
  try {
    audioEl.muted = true;
    await audioEl.play();
  } catch (err) {
    // ignore autoplay rejections
  } finally {
    audioEl.pause();
    audioEl.currentTime = 0;
    audioEl.muted = false;
  }
}

async function stopSystem() {
  isRunning = false;
  startBtn.disabled = false;
  stopBtn.disabled = true;
  progressFill.style.width = "0%";
  statusLabel.textContent = "Paused";
  statusMessage.textContent = "Press Start";

  if (rafId) {
    cancelAnimationFrame(rafId);
  }
  if (webcam) {
    webcam.stop();
  }
}

startBtn.addEventListener("click", startSystem);
stopBtn.addEventListener("click", stopSystem);
