import streamlit.components.v1 as components

def render_focus_timer():
    timer_html = """
    <div id="focus-widget" style="font-family: sans-serif; text-align: center; padding: 20px; border-radius: 12px; background: #f0f2f6;">
        <div style="margin-bottom: 12px;">
            <button onclick="setMode(25,5)" style="margin:4px; padding:8px 14px; border-radius:8px; border:none; cursor:pointer; background:#ff4b4b; color:white;">🍅 Pomodoro (25 min)</button>
            <button onclick="setMode(50,10)" style="margin:4px; padding:8px 14px; border-radius:8px; border:none; cursor:pointer; background:#4b8bff; color:white;">📘 Long Focus (50 min)</button>
        </div>

        <div>
            <input type="number" id="customMinutes" placeholder="Custom minutes" min="1" style="padding:6px; width:120px; border-radius:6px; border:1px solid #ccc;">
            <button onclick="startCustom()" style="padding:8px 14px; border-radius:8px; border:none; cursor:pointer; background:#2ecc71; color:white;">Start Custom</button>
        </div>

        <h1 id="timer-display" style="font-size: 48px; margin: 16px 0; color:#333;">00:00</h1>
        <p id="timer-status" style="color:#666;">Choose a mode to begin focusing</p>

        <div>
            <button onclick="pauseTimer()" style="margin:4px; padding:8px 14px; border-radius:8px; border:none; cursor:pointer; background:#f39c12; color:white;">⏸ Pause</button>
            <button onclick="resumeTimer()" style="margin:4px; padding:8px 14px; border-radius:8px; border:none; cursor:pointer; background:#27ae60; color:white;">▶ Resume</button>
            <button onclick="resetTimer()" style="margin:4px; padding:8px 14px; border-radius:8px; border:none; cursor:pointer; background:#7f8c8d; color:white;">🔄 Reset</button>
        </div>
    </div>

    <script>
        let totalSeconds = 0;
        let remaining = 0;
        let interval = null;
        let isBreakNext = false;
        let breakMinutes = 0;

        function updateDisplay() {
            const m = Math.floor(remaining / 60).toString().padStart(2, '0');
            const s = (remaining % 60).toString().padStart(2, '0');
            document.getElementById('timer-display').innerText = m + ":" + s;
        }

        function tick() {
            if (remaining > 0) {
                remaining--;
                updateDisplay();
            } else {
                clearInterval(interval);
                document.getElementById('timer-status').innerText = "⏰ Time's up! Great work.";
                try {
                    const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
                    const o = audioCtx.createOscillator();
                    o.frequency.value = 880;
                    o.connect(audioCtx.destination);
                    o.start();
                    setTimeout(() => o.stop(), 400);
                } catch (e) {}
            }
        }

        function startTimer(minutes, statusText) {
            clearInterval(interval);
            totalSeconds = minutes * 60;
            remaining = totalSeconds;
            updateDisplay();
            document.getElementById('timer-status').innerText = statusText;
            interval = setInterval(tick, 1000);
        }

        function setMode(focusMin, breakMin) {
            breakMinutes = breakMin;
            startTimer(focusMin, "🎯 Focus session in progress...");
        }

        function startCustom() {
            const val = parseInt(document.getElementById('customMinutes').value);
            if (!val || val <= 0) {
                alert("Enter a valid number of minutes");
                return;
            }
            breakMinutes = 0;
            startTimer(val, "🎯 Custom focus session in progress...");
        }

        function pauseTimer() {
            clearInterval(interval);
            document.getElementById('timer-status').innerText = "⏸ Paused";
        }

        function resumeTimer() {
            if (remaining > 0) {
                clearInterval(interval);
                interval = setInterval(tick, 1000);
                document.getElementById('timer-status').innerText = "🎯 Focus session in progress...";
            }
        }

        function resetTimer() {
            clearInterval(interval);
            remaining = 0;
            updateDisplay();
            document.getElementById('timer-status').innerText = "Choose a mode to begin focusing";
        }
    </script>
    """
    components.html(timer_html, height=320)