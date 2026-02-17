from flask import Flask, render_template_string, jsonify, request
import random

app = Flask(__name__)

balance = 500
jackpot = 1000
symbols = ["🍒","🍋","🔔","💎","7️⃣"]

HTML = """
<!DOCTYPE html>
<html>
<head>
<title>Vegas Slot Machine</title>
<style>
body {
    background: radial-gradient(circle at center, #000 0%, #111 100%);
    color: gold;
    text-align: center;
    font-family: 'Arial', sans-serif;
    overflow-x: hidden;
}
h1 { font-size: 60px; margin-top: 20px; text-shadow: 0 0 10px #ff0; }
h2 { margin: 10px 0; }
.reels { display: flex; justify-content: center; margin: 20px; }
.reel {
    font-size: 100px;
    width: 130px;
    height: 130px;
    margin: 10px;
    border: 5px solid gold;
    border-radius: 15px;
    background: #222;
    display: flex;
    justify-content: center;
    align-items: center;
    box-shadow: 0 0 20px #ff0 inset;
    transition: transform 0.2s;
}
.reel.spin { transform: scale(1.2); }
button, input { font-size: 25px; padding: 12px 25px; margin: 10px; border: none; border-radius: 10px; cursor: pointer; }
button { background: red; color: white; }
button:hover { background: darkred; }
input { width: 80px; text-align: center; }
.flash { animation: flash 0.3s infinite alternate; }
@keyframes flash { from { box-shadow: 0 0 20px #ff0 inset; } to { box-shadow: 0 0 50px #fff inset; } }
.lever { width: 20px; height: 120px; background: silver; border-radius: 10px; display: inline-block; position: relative; margin-left: 20px; cursor: pointer; }
.lever:active { transform: rotate(20deg); transform-origin: bottom center; transition: 0.1s; }
#result { text-shadow: 0 0 10px #fff; }
</style>
</head>
<body>

<h1>🎰 VEGAS SLOT MACHINE 🎰</h1>
<h2>Balance: $<span id="balance">{{balance}}</span></h2>
<h2>Jackpot: $<span id="jackpot">{{jackpot}}</span></h2>

<div>
<label for="bet">Choose your bet ($1-$500): </label>
<input type="number" id="bet" value="50" min="1" max="500">
<div class="lever" onclick="spin()"></div>
</div>

<div class="reels">
<div class="reel" id="r1">7️⃣</div>
<div class="reel" id="r2">7️⃣</div>
<div class="reel" id="r3">7️⃣</div>
</div>

<button onclick="spin()">SPIN</button>
<h2 id="result"></h2>

<!-- Sounds -->
<audio id="winSound" src="/static/sounds/win-sound.mp3"></audio>
<audio id="jackpotSound" src="/static/sounds/jackpot-sound.mp3"></audio>

<script>
let spinning = false;
const r1 = document.getElementById("r1");
const r2 = document.getElementById("r2");
const r3 = document.getElementById("r3");
const balanceEl = document.getElementById("balance");
const jackpotEl = document.getElementById("jackpot");
const resultEl = document.getElementById("result");
const winSound = document.getElementById("winSound");
const jackpotSound = document.getElementById("jackpotSound");
const betEl = document.getElementById("bet");
const symbols = ["🍒","🍋","🔔","💎","7️⃣"];

// ===== Web Audio API for spin sound =====
let audioCtx = null;
let spinBuffer = null;
let spinSource = null;

async function loadSpinSound(){
    if(!audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    const res = await fetch("/static/sounds/slot_reels.mp3");
    const arrayBuffer = await res.arrayBuffer();
    spinBuffer = await audioCtx.decodeAudioData(arrayBuffer);
}
loadSpinSound();

function startSpinSound(){
    if(!audioCtx || !spinBuffer) return;
    spinSource = audioCtx.createBufferSource();
    spinSource.buffer = spinBuffer;
    spinSource.loop = true;
    spinSource.connect(audioCtx.destination);
    spinSource.start(0, 0.2); // Start at 0.2s into the audio
}

function stopSpinSound(){
    if(spinSource){
        spinSource.stop();
        spinSource.disconnect();
        spinSource = null;
    }
}

function sleep(ms){ return new Promise(resolve => setTimeout(resolve, ms)); }

function animateReel(element, finalSymbol, duration){
    return new Promise(async (resolve)=>{
        let elapsed = 0;
        let speed = 50;
        while(elapsed < duration){
            element.innerText = symbols[Math.floor(Math.random()*symbols.length)];
            element.classList.add("spin");
            await sleep(speed);
            elapsed += speed;
            speed += 5;
        }
        element.classList.remove("spin");
        element.innerText = finalSymbol;
        resolve();
    });
}

async function spin(){
    if(spinning) return;
    spinning = true;
    resultEl.innerText = "";

    let betAmount = parseInt(betEl.value);
    if(isNaN(betAmount) || betAmount < 1 || betAmount > 500){
        alert("Enter a valid bet between 1 and 500.");
        spinning = false;
        return;
    }

    let response = await fetch(`/spin?bet=${betAmount}`);
    let data = await response.json();
    if(data.error){ alert(data.error); spinning = false; return; }

    // Start spin sound immediately
    startSpinSound();

    // Animate reels in order with 0.5s stagger
    const reelPromises = [];
    reelPromises.push(animateReel(r1, data.reels[0], 2000));
    await sleep(500);
    reelPromises.push(animateReel(r2, data.reels[1], 2500));
    await sleep(500);
    reelPromises.push(animateReel(r3, data.reels[2], 3000));

    // Wait for all reels to finish
    await Promise.all(reelPromises);

    // Stop spin sound
    stopSpinSound();

    balanceEl.innerText = data.balance;
    jackpotEl.innerText = data.jackpot;

    // Play win/jackpot sounds
    if(data.result === "jackpot"){
        jackpotSound.currentTime=0; jackpotSound.play();
        resultEl.innerText = "🎉 JACKPOT $" + data.win;
        flashLights();
    } else if(data.result === "win"){
        winSound.currentTime=0; winSound.play();
        resultEl.innerText = "✨ WIN $" + data.win;
        flashLights();
    } else {
        resultEl.innerText = "Try Again";
    }

    spinning = false;
}

function flashLights(){
    document.body.classList.add("flash");
    setTimeout(()=>{ document.body.classList.remove("flash"); }, 2000);
}
</script>
</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(HTML, balance=balance, jackpot=jackpot)

@app.route("/spin")
def spin_route():
    global balance, jackpot
    bet = int(request.args.get("bet",50))
    if bet < 1: bet = 1
    if bet > 500: bet = 500
    if balance < bet: return jsonify({"error":"Not enough money"})

    balance -= bet
    r1 = random.choice(symbols)
    r2 = random.choice(symbols)
    r3 = random.choice(symbols)
    jackpot += bet // 2
    result = "lose"
    win = 0
    if r1==r2==r3:
        result="jackpot"; win=jackpot; balance+=jackpot; jackpot=1000
    elif r1==r2 or r2==r3 or r1==r3:
        result="win"; win=bet*4; balance+=win
    return jsonify({"reels":[r1,r2,r3],"result":result,"win":win,"balance":balance,"jackpot":jackpot})

if __name__=="__main__":
    app.run(host="0.0.0.0", port=5000)
