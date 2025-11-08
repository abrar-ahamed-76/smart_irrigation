from flask import Flask, jsonify, render_template_string, request
import random
from threading import Thread

app = Flask(__name__)

pump_status = "OFF"
mode = "AUTO"
logs = []

def add_log(msg):
    logs.append(msg)
    if len(logs) > 5:
        logs.pop(0)

# HTML with background image
html_page = """
<!DOCTYPE html>
<html>
<head>
<title>🌿 Smart Irrigation Dashboard</title>
<style>
  body {
      font-family: Arial, sans-serif;
      background: url('https://radiocrafts.com/wp-content/uploads/2021/09/Smart_Irrigation_Featured_Image_For_Applications_Page_2.png') no-repeat center center fixed;
      background-size: cover;
      text-align: center;
      color: #fff;
  }
  .container {
      background: rgba(0, 0, 0, 0.6);
      width: 400px;
      margin: auto;
      margin-top: 30px;
      padding: 20px;
      border-radius: 10px;
      box-shadow: 0 0 10px #000;
  }
  img {width: 70px; height: 70px;}
  button {
      padding: 8px 15px; margin: 5px;
      border: none; border-radius: 5px; cursor: pointer; font-weight: bold;
  }
  .on {background: green; color: white;}
  .off {background: red; color: white;}
  .auto {background: #007BFF; color: white;}
  .manual {background: #FFA500; color: white;}
  pre {
      background: rgba(255, 255, 255, 0.1);
      color: #fff;
      padding: 10px;
      border-radius: 5px;
      text-align: left;
  }
  h2 {color: #ffffcc;}
</style>
</head>
<body>
  <h2>🌾 Smart Irrigation System</h2>
  <img src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSW9qcZOkKo1k7LM83GxppSwr62uwCYtAhb7BkSnDaj&s" width="150">

  <div class="container">
      <h3>🌡 Temperature: <span id="temp">--</span>°C</h3>
      <h3>💧 Soil Moisture: <span id="moisture">--</span>%</h3>
      <h3>☁ Weather: <span id="weather">--</span> <img id="wimg" width="40"></h3>
      <h3>🚰 Tank Level: <span id="tank">--</span>%</h3>
      <h3>⚙ Mode: <span id="mode">--</span></h3>
      <h3>🔌 Pump: <span id="pump">--</span></h3>
      <img id="pumpimg" src="" alt="Pump" width="80"><br>

      <button class="auto" onclick="setMode('AUTO')">Auto Mode</button>
      <button class="manual" onclick="setMode('MANUAL')">Manual Mode</button><br>
      <button class="on" onclick="manualControl('ON')">Turn ON</button>
      <button class="off" onclick="manualControl('OFF')">Turn OFF</button>

      <h3>🧾 System Log</h3>
      <pre id="log">Loading...</pre>
  </div>

<script>
function updateData(){
  fetch('/data').then(r=>r.json()).then(d=>{
    document.getElementById('moisture').innerText = d.moisture;
    document.getElementById('temp').innerText = d.temperature;
    document.getElementById('mode').innerText = d.mode;
    document.getElementById('tank').innerText = d.tank_level;
    document.getElementById('pump').innerText = d.pump_status;
    document.getElementById('log').innerText = d.logs.join("\\n");
    document.getElementById('weather').innerText = d.weather;

    // Weather image
    const wimg = document.getElementById('wimg');
    if(d.weather=="Sunny") wimg.src="https://cdn-icons-png.flaticon.com/512/869/869869.png";
    else if(d.weather=="Rainy") wimg.src="https://cdn-icons-png.flaticon.com/512/414/414974.png";
    else if(d.weather=="Cloudy") wimg.src="https://cdn-icons-png.flaticon.com/512/414/414927.png";
    else wimg.src="https://cdn-icons-png.flaticon.com/512/414/414968.png";

    // Pump image
    const pimg = document.getElementById('pumpimg');
    if(d.pump_status=="ON")
       pimg.src="https://cdn-icons-png.flaticon.com/512/4837/4837294.png";
    else
       pimg.src="https://cdn-icons-png.flaticon.com/512/1048/1048940.png";
  });
}

function setMode(m){
  fetch('/mode', {
    method:'POST', headers:{'Content-Type':'application/json'},
    body:JSON.stringify({mode:m})
  });
}

function manualControl(s){
  fetch('/control', {
    method:'POST', headers:{'Content-Type':'application/json'},
    body:JSON.stringify({status:s})
  });
}

setInterval(updateData,2000);
</script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(html_page)

@app.route('/data')
def get_data():
    global pump_status, mode
    moisture = random.randint(20,80)
    temperature = random.randint(20,35)
    tank_level = random.randint(30,100)
    weather = random.choice(["Sunny","Rainy","Cloudy","Humid"])

    if mode == "AUTO":
        if moisture < 40 and tank_level > 30:
            pump_status = "ON"
            add_log("Auto: Moisture low — Pump ON")
        else:
            pump_status = "OFF"
            add_log("Auto: Moisture OK — Pump OFF")

    return jsonify({
        "moisture":moisture,
        "temperature":temperature,
        "tank_level":tank_level,
        "weather":weather,
        "pump_status":pump_status,
        "mode":mode,
        "logs":logs
    })

@app.route('/mode', methods=['POST'])
def change_mode():
    global mode
    mode = request.json.get('mode', 'AUTO')
    add_log(f"Mode changed to {mode}")
    return jsonify({"mode": mode})

@app.route('/control', methods=['POST'])
def manual_control():
    global pump_status, mode
    if mode == "MANUAL":
        status = request.json.get('status')
        pump_status = status
        add_log(f"Manual: Pump {status}")
    else:
        add_log("Ignored manual command (Auto mode)")
    return jsonify({"pump_status": pump_status})

def run_app():  
    app.run(host='0.0.0.0',port=5000, debug=False, use_reloader=False)

Thread(target=run_app).start()