import machine
import network
import usocket as socket
import utime as time
import _thread
import json 

# Define the IR emitter and Red LED (in this code Red LED is sometimes called as buzzer) pins
ir_emitter_pin = machine.Pin(15, machine.Pin.OUT)
redLED_pin = machine.Pin(14, machine.Pin.OUT)
redLED_status = "Off"

# Function to control the IR emitter
def control_ir_emitter(status):
    if status == "on":
        ir_emitter_pin.on()
    elif status == "off":
        ir_emitter_pin.off()

# Function to get the buzzer status
def get_redLED_status():
    return "On" if redLED_pin.value() == 1 else "Off"

# Function to periodically check the ADC value and control the redLED
def check_adc_and_control_redLED():
    global redLED_status  # Declare redLED_status as global
    adc = machine.ADC(26) 
    while True:
        adc_value = adc.read_u16()
        print("ADC Value:", adc_value)

        if adc_value < 64420: # the threshold value must be tuned based on test environment. Ambient light also has IR rays. 
            print("Receiver/Transmitter blocked, turning on the red LED")
            redLED_pin.on()
        else:
            print("Receiver/Transmitter not blocked, turning off the red LED")
            redLED_pin.off()

        redLED_status = get_redLED_status()  # Update redLED_status
        print("Red LED Status:", redLED_status)
        time.sleep(1)


# Create a network connection
ssid = 'group1'       #Set access point name 
password = 'fartfart'      #Set your access point password
ap = network.WLAN(network.AP_IF)
ap.config(essid=ssid, password=password)
ap.active(True)            #activating

while ap.active() == False:
  pass
print('Connection is successful')
print(ap.ifconfig())

# Define HTTP response
def web_page():
    ir_emitter_status = get_ir_emitter_status()
    redLED_status = get_redLED_status()
    ir_emitter_color = "purple" if ir_emitter_status == "ON" else "black"
    buzzer_color = "red" if redLED_status == "On" else "gray"
    
    html = """<html><head>
    <title>Pico Web Server</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="icon" href="data:,">
    <style>
        html {
            font-family: Helvetica;
            text-align: center;
            background-color: #b0b2b2;
        }
        h1 {
            color: #0F3376;
            padding: 2vh;
        }
        p {
            font-size: 1.5rem;
        }
        .button {
            display: inline-block;
            background-color: #4CAF50;
            border: none;
            border-radius: 4px;
            color: white;
            padding: 16px 40px;
            text-decoration: none;
            font-size: 30px;
            margin: 2px;
            cursor: pointer;
        }
        .button2 {
            background-color: #555555;
        }
        .circle {
            width: 20px;
            height: 20px;
            border-radius: 50%;
            display: inline-block;
            margin-left: 10px;
        }
    </style>
    <script>
        function updateStatus() {
            var xhr = new XMLHttpRequest();
            xhr.onreadystatechange = function() {
                if (xhr.readyState == 4 && xhr.status == 200) {
                    var data = JSON.parse(xhr.responseText);
                    document.getElementById("irEmitterStatus").innerHTML = data.irEmitterStatus;
                    var irEmitterColor = data.irEmitterStatus === "ON" ? "purple" : "black";
                    document.getElementById("irEmitterIndicator").style.backgroundColor = irEmitterColor;
                    document.getElementById("RedLEDStatus").innerHTML = data.RedLEDStatus;
                    var buzzerColor = data.RedLEDStatus === "On" ? "red" : "gray";
                    document.getElementById("buzzerIndicator").style.backgroundColor = buzzerColor;
                }
            };
            xhr.open("GET", "/status", true);
            xhr.send();
        }
        setInterval(updateStatus, 1000); // Refresh every 1 second
    </script>
    </head>
    <body>
    <h1>IR Detector</h1>
    <p>IR Emitter: <strong id="irEmitterStatus">""" + ir_emitter_status + """</strong><div class="circle" id="irEmitterIndicator" style="background-color: """ + ir_emitter_color + """;"></div></p>
    <p>RedLED Status: <strong id="RedLEDStatus">""" + redLED_status + """</strong><div class="circle" id="buzzerIndicator" style="background-color: """ + buzzer_color + """;"></div></p>
    <p><a href="/?ir_emitter_pin=on"><button class="button">IR Emitter ON</button></a></p>
    <p><a href="/?ir_emitter_pin=off"><button class="button button2">IR Emitter OFF</button></a></p>
    </body>
    </html>"""
    return html

# Function to get the IR emitter status
def get_ir_emitter_status():
    return "ON" if ir_emitter_pin.value() == 1 else "OFF"

def get_status():
    status = {
        "irEmitterStatus": get_ir_emitter_status(),
        "RedLEDStatus": redLED_status,
    }
    return json.dumps(status)

# Start the ADC monitoring function in a separate thread
_thread.start_new_thread(check_adc_and_control_redLED, ())

# Create a socket server
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('', 80))
s.listen(5)

while True:
    conn, addr = s.accept()
    print('Got a connection from %s' % str(addr))
    request = conn.recv(1024)
    if request:
        request = str(request)
        print('Content = %s' % request)
        buzzer_on = request.find('/?redLED_pin=on') #buzzer is the red LED
        buzzer_off = request.find('/?redLED_pin=off')
        ir_emitter_on = request.find('/?ir_emitter_pin=on')
        ir_emitter_off = request.find('/?ir_emitter_pin=off')

    if buzzer_on == 6:
        print('BUZZER ON')
        redLED_pin.value(1)
    elif buzzer_off == 6:
        print('BUZZER OFF')
        redLED_pin.value(0)

    if ir_emitter_on == 6:
        print('IR EMITTER ON')
        control_ir_emitter("on")
    elif ir_emitter_off == 6:
        print('IR EMITTER OFF')
        control_ir_emitter("off")

    if request.find("/status") == 6:
        response = get_status()
        conn.send("HTTP/1.1 200 OK\n")
        conn.send("Content-Type: application/json\n")
        conn.send("Connection: close\n\n")
        conn.sendall(response)
    else:
        response = web_page()
        conn.send("HTTP/1.1 200 OK\n")
        conn.send("Content-Type: text/html\n")
        conn.send("Connection: close\n\n")
        conn.sendall(response)
    conn.close()

