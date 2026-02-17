from flask import Flask, render_template_string

app = Flask(__name__)

balance = 200
jackpot = 1000

HTML = """
<!DOCTYPE html>
<html>
<head>
<title>Vegas Casino Slot Machine</title>
<style>
body {
    margin: 0;
    padding: 0;
    background: black;
    font-family: 'Arial', sans-serif;
    color: #fff;
    text-align: center;
}
h1 {
    font-size: 50px;
    color: #ff0;
    text-shadow: 0 0 10px #fff200, 0 0 20px #ff0, 0 0 30px #ff0, 0 0 40px #ff0;
    margin-top: 20px;
}
h2 {
    font-size: 25px;
    text-shadow: 0 0 5px #fff, 0 0 10px #ff0, 0 0 20px #ff0;
}
.slot-container {
    margin: 30px auto;
    display: flex;
    justify-content: center;
    position: relative;
}
.reel-window {
    width: 90px;
    height: 90px;
    overflow: hidden;
    border: 4px solid #ff0;
    margin: 5px;
    background: #000;
    border-radius: 10px;
    box-shadow: 0 0 20px #ff0 inset, 0 0 30px #ff0;
}
.reel-strip {
    display: flex;
    flex-direction: column;
    align-items: center;
    font-size: 70px;
}
.reel-strip div {
    height: 90px;
    line-height: 90px;
    opacity: 1;
    will-change: transform, opacity;
    backface-visibility: hidden;
    transform: translateZ(0);
}
button {
    padding: 15px 30px;
    font-size: 20px;
    background: #ff0000;
    color: white;
    border: none;
    border-radius: 10px;
    cursor: pointer;
    box-shadow: 0 0 15px red;
    margin-top: 20px;
}
button:hover { background: #cc0000; }
.win { animation: flash 0.5s infinite alternate; }
@keyframes flash { from { color: yellow; } to { color: red; } }

/* bounce effect for reel stop */
.bounce {
    animation: bounce 0.2s ease-out;
}
@keyframes bounce {
    0%   { transform: translateY(var(--finalY)) }
    50%  { transform: translateY(calc(var(--finalY) - 15px)) }
    100% { transform: translateY(var(--finalY)) }
}

/* Flashing lights overlay */
.flash-overlay {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    pointer-events: none;
    background: rgba(255,255,0,0.2);
    mix-blend-mode: screen;
    animation: flashLights 0.3s infinite alternate;
    z-index: 1000;
    display: none; /* hidden by default */
}
@keyframes flashLights {
    from { background: rgba(255,255,0,0.3); }
    to { background: rgba(255,0,0,0.5); }
}

/* Glowing border for slot container on big win */
.slot-container.win-glow {
    box-shadow: 0 0 30px #ff0, 0 0 60px #ff0, 0 0 90px #ff0 inset;
}
</style>
</head>
<body>

<h1>🎰 VEGAS CASINO SLOT 🎰</h1>
<h2>Balance: $<span id="balance">{{balance}}</span></h2>
<h2>Jackpot: $<span id="jackpot">{{jackpot}}</span></h2>

<div class="slot-container">
    <div class="reel-window"><div class="reel-strip" id="reel1"></div></div>
    <div class="reel-window"><div class="reel-strip" id="reel2"></div></div>
    <div class="reel-window"><div class="reel-strip" id="reel3"></div></div>
    <div class="flash-overlay" id="flashOverlay"></div>
</div>

<input type="number" id="bet" placeholder="Bet amount">
<button onclick="spin()">SPIN</button>
<h2 id="result"></h2>

<audio id="spin-sound" src="/static/sounds/slot_reels.mp3" preload="auto"></audio>
<audio id="win-sound" src="/static/sounds/win-sound.mp3" preload="auto"></audio>
<audio id="jackpot-sound" src="/static/sounds/jackpot-sound.mp3" preload="auto"></audio>

<script>
const symbols = ["🍒","🍋","🍊","⭐","💎","7️⃣"];
const symbolHeight = 90;
const reels = [
    document.getElementById("reel1"),
    document.getElementById("reel2"),
    document.getElementById("reel3")
];

const spinSound = document.getElementById("spin-sound");
const winSound = document.getElementById("win-sound");
const jackpotSound = document.getElementById("jackpot-sound");

const flashOverlay = document.getElementById("flashOverlay");
const slotContainer = document.querySelector(".slot-container");

let spinning = false;

// Build reel strips
function buildStrip(reel) {
    reel.innerHTML = "";
    for (let i = 0; i < 30; i++) {
        const s = document.createElement("div");
        s.innerText = symbols[Math.floor(Math.random() * symbols.length)];
        reel.appendChild(s);
    }
}
reels.forEach(buildStrip);

// Spin function with 0.5s staggered start
function spin() {
    if (spinning) return;
    spinning = true;

    let bet = parseInt(document.getElementById("bet").value);
    let balance = parseInt(document.getElementById("balance").innerText);
    let jackpot = parseInt(document.getElementById("jackpot").innerText);

    if (!bet || bet <= 0 || bet > balance) {
        document.getElementById("result").innerText = "Invalid bet!";
        spinning = false;
        return;
    }

    spinSound.currentTime = 0;
    spinSound.play();

    balance -= bet;
    jackpot += Math.floor(bet * 0.2);
    document.getElementById("balance").innerText = balance;
    document.getElementById("jackpot").innerText = jackpot;
    document.getElementById("result").classList.remove("win");
    document.getElementById("result").innerText = "Spinning...";

    const finalSymbols = reels.map(() => symbols[Math.floor(Math.random() * symbols.length)]);
    
    reels.forEach((reel, i) => {
        setTimeout(() => {
            const targetIndex = symbols.indexOf(finalSymbols[i]);
            let steps = 0;
            const totalSteps = 30 + targetIndex;
            const intervalTime = 80; // base speed
            const interval = setInterval(() => {
                steps++;
                reel.style.transform = `translateY(-${(steps % 30) * symbolHeight}px)`;
                if (steps >= totalSteps) {
                    clearInterval(interval);

                    // Snap to final symbol
                    const finalY = -targetIndex * symbolHeight;
                    reel.style.transition = "none";
                    reel.style.setProperty('--finalY', finalY + 'px');
                    reel.classList.add('bounce');
                    reel.style.transform = `translateY(${finalY}px)`;

                    setTimeout(() => reel.classList.remove('bounce'), 200);
                    reel.dataset.finalSymbol = finalSymbols[i];
                }
            }, intervalTime);
        }, i * 500); // 0.5s staggered start
    });

    setTimeout(() => {
        spinSound.pause();
        spinSound.currentTime = 0;

        const results = reels.map(r => r.dataset.finalSymbol);
        checkWin(bet, results);

        spinning = false; // allow next spin
    }, 2500 + 1000); 
}

// Win logic with flashing lights
function checkWin(bet, results) {
    const balanceElem = document.getElementById("balance");
    const jackpotElem = document.getElementById("jackpot");
    let balance = parseInt(balanceElem.innerText);
    let jackpot = parseInt(jackpotElem.innerText);

    let winnings = 0;
    let resultText = "No win this time.";

    if (results.every(r => r==="7️⃣")) {
        winnings = jackpot;
        jackpot = 1000;
        resultText = "💰 JACKPOT!!! 💰";
        jackpotSound.currentTime = 0;
        jackpotSound.play();
    } else if (results[0]===results[1] && results[1]===results[2]) {
        winnings = bet*6;
        resultText = "🔥 BIG WIN! 🔥";
        winSound.currentTime = 0;
        winSound.play();
    } else if (results[0]===results[1] || results[1]===results[2] || results[0]===results[2]) {
        winnings = bet*2;
        resultText = "You won $" + winnings;
        winSound.currentTime = 0;
        winSound.play();
    }

    // Show flashing lights for big win or jackpot
    if (winnings >= bet*6) {
        flashOverlay.style.display = "block";
        slotContainer.classList.add("win-glow");
        setTimeout(() => {
            flashOverlay.style.display = "none";
            slotContainer.classList.remove("win-glow");
        }, 2000);
    }

    if (winnings>0) {
        balance += winnings;
        document.getElementById("result").classList.add("win");
    } else {
        document.getElementById("result").classList.remove("win");
    }

    balanceElem.innerText = balance;
    jackpotElem.innerText = jackpot;
    document.getElementById("result").innerText = resultText;
}
</script>

</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(HTML, balance=balance, jackpot=jackpot)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
