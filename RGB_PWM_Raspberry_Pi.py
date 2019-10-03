from RPi import GPIO
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish

GPIO.setwarnings(False)

# Se inicializan los valores de las diferentes variables
R = 255
G = 255
B = 255
I = 100
Encendido = 1
EncendidoMQTT = 1

# Valor del incremento o decremento por cada paso
IncDec = 10
IncDec_I = 2

# Broker MQTT
Broker = "localhost"

# INPUTS (9 en total):
# CLK y DT del encoder rotatorio del color rojo.
CLK_R = 19
DT_R = 26
# CLK y DT del encoder rotatorio del color verde.
CLK_G = 6
DT_G = 13
# CLK y DT del encoder rotatorio del color azul.
CLK_B = 27
DT_B = 22
# CLK y DT del encoder rotatorio correpondiente a la atenuación.
CLK_I = 10
DT_I = 9
# Boton Pulsador
btn = 11

# OUTPUTS (4 en total):
# Relevador
relay = 12
RED = 16
GREEN = 20
BLUE = 21

# BCM: Configuracion para  utilizar el numero de pin GPIO correspondiente.
# Board (no utilizado): la numeración se basa en el oden de los pines de arriba a abajo de la placa. 
GPIO.setmode(GPIO.BCM)

# Configuracion  de entradas
# Se configura CLK y DT como entradas
GPIO.setup(CLK_R, GPIO.IN)
GPIO.setup(DT_R, GPIO.IN)

GPIO.setup(CLK_G, GPIO.IN)
GPIO.setup(DT_G, GPIO.IN)

GPIO.setup(CLK_B, GPIO.IN)
GPIO.setup(DT_B, GPIO.IN)

GPIO.setup(CLK_I, GPIO.IN)
GPIO.setup(DT_I, GPIO.IN)

# Se configura el boton como entrada con resistencia pull-up (interna)
GPIO.setup(btn, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Configuracion de salidas
GPIO.setup(relay, GPIO.OUT)
GPIO.setup(RED, GPIO.OUT)
GPIO.setup(GREEN, GPIO.OUT)
GPIO.setup(BLUE, GPIO.OUT)

# Variables PWM
R_PWM = GPIO.PWM(RED, 500)
G_PWM = GPIO.PWM(GREEN, 500)
B_PWM = GPIO.PWM(BLUE, 500)

# Inician apagados (anodo comun)
R_PWM.start(100)
G_PWM.start(100)
B_PWM.start(100)


# _______________________________________________________________________________

# Funciones que se llaman en las interrupciones externas
def Boton(channel):
    global Encendido
    Encendido = int(not Encendido)
    GPIO.output(relay, (Encendido))
    publish.single("Modulo1/Iluminacion/RGB/Encendido", int(Encendido), hostname=Broker, qos=1, retain=True)


def Encoder_R(channel):
    global R
    global I
    while GPIO.input(CLK_R) == False:
        pass
    if GPIO.input(DT_R) == False:
        if R <= 255 - IncDec:
            R += IncDec
        else:
            R = 255
    else:
        if R >= IncDec:
            R -= IncDec
        else:
            R = 0
    publish.single("Modulo1/Iluminacion/RGB/Color/R", R, hostname=Broker, qos=1, retain=True)
    R_PWM.ChangeDutyCycle(100 - R / 255 * I)


def Encoder_G(channel):
    global G
    global I
    while GPIO.input(CLK_G) == False:
        pass
    if GPIO.input(DT_G) == False:
        if G <= 255 - IncDec:
            G += IncDec
        else:
            G = 255
    else:
        if G >= IncDec:
            G -= IncDec
        else:
            G = 0
    publish.single("Modulo1/Iluminacion/RGB/Color/G", G, hostname=Broker, qos=1, retain=True)
    G_PWM.ChangeDutyCycle(100 - G / 255 * I)


def Encoder_B(channel):
    global B
    global I
    while GPIO.input(CLK_B) == False:
        pass
    if GPIO.input(DT_B) == False:
        if B <= 255 - IncDec:
            B += IncDec
        else:
            B = 255
    else:
        if B >= IncDec:
            B -= IncDec
        else:
            B = 0
    publish.single("Modulo1/Iluminacion/RGB/Color/B", B, hostname=Broker, qos=1, retain=True)
    B_PWM.ChangeDutyCycle(100 - B / 255 * I)


def Encoder_I(channel):
    global R
    global G
    global B
    global I
    Ianterior = I
    while GPIO.input(CLK_I) == False:
        pass
    if GPIO.input(DT_I) == False:
        if I <= 100 - IncDec_I:
            I += IncDec_I
        else:
            I = 100
    else:
        if I >= IncDec_I:
            I -= IncDec_I
        else:
            I = 0

    publish.single("Modulo1/Iluminacion/RGB/Intensidad", I, hostname=Broker, qos=1, retain=True)
    R_PWM.ChangeDutyCycle(100 - R / 255 * I)
    G_PWM.ChangeDutyCycle(100 - G / 255 * I)
    B_PWM.ChangeDutyCycle(100 - B / 255 * I)


# MQTT
def on_connect(client, userdata, flags, rc):
    client.subscribe("Modulo1/Iluminacion/RGB/#")


def on_message(client, userdata, msg):
    global R
    global G
    global B
    global I
    global Encendido
    msg.payload = msg.payload.decode("utf-8")
    if msg.topic == "Modulo1/Iluminacion/RGB/Color/R":
        R = int(msg.payload)
        R_PWM.ChangeDutyCycle(100 - R / 255 * I)

    elif msg.topic == "Modulo1/Iluminacion/RGB/Color/G":
        G = int(msg.payload)
        G_PWM.ChangeDutyCycle(100 - G / 255 * I)

    elif msg.topic == "Modulo1/Iluminacion/RGB/Color/B":
        B = int(msg.payload)
        B_PWM.ChangeDutyCycle(100 - B / 255 * I)

    elif msg.topic == "Modulo1/Iluminacion/RGB/Intensidad":
        Ianterior = I
        I = int(msg.payload)
        R_PWM.ChangeDutyCycle(100 - R / 255 * I)
        G_PWM.ChangeDutyCycle(100 - G / 255 * I)
        B_PWM.ChangeDutyCycle(100 - B / 255 * I)

    elif msg.topic == "Modulo1/Iluminacion/RGB/Encendido":
        EncendidoMQTT = not (msg.payload == "1")
        if Encendido == EncendidoMQTT:
            Encendido = not Encendido
        GPIO.output(relay, EncendidoMQTT)


# __________________________________________________________________


# Interrupcion al detectar el flanco de subida del boton pulsador
GPIO.add_event_detect(btn, GPIO.RISING, callback=Boton, bouncetime=300)

# Interrupciones al detectar el flanco de bajada de los diferentes encoders rotatorios
GPIO.add_event_detect(CLK_R, GPIO.FALLING, callback=Encoder_R, bouncetime=50)
GPIO.add_event_detect(CLK_G, GPIO.FALLING, callback=Encoder_G, bouncetime=50)
GPIO.add_event_detect(CLK_B, GPIO.FALLING, callback=Encoder_B, bouncetime=50)
GPIO.add_event_detect(CLK_I, GPIO.FALLING, callback=Encoder_I, bouncetime=50)

# MQTT
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(Broker, 1883, 60)
client.loop_forever()

GPIO.cleanup()
