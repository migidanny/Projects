from RPi import GPIO
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish

GPIO.setwarnings(False)

# Se inicializan los valores de las diferentes variables
R = 255
G = 255
B = 255
I = 100
Encendido = False
Resolucion = 32 - 1

# Valor del incremento o decremento por cada paso
IncDec = 1

# Broker MQTT
Broker = "localhost"

# INPUTS (9 en total):
# CLK y DT del encoder rotatorio del color rojo.
CLK_R = 2
DT_R = 3
# CLK y DT del encoder rotatorio del color verde.
CLK_G = 4
DT_G = 17
# CLK y DT del encoder rotatorio del color azul.
CLK_B = 27
DT_B = 22
# CLK y DT del encoder rotatorio correpondiente a la atenuación.
CLK_I = 10
DT_I = 9
# Boton Pulsador
btn = 11

# OUTPUTS (16 en total):
# 5 bits más significativos del color rojo
RED = (0, 6, 13, 19, 26)
# 5 bits más significativos del color verde
GREEN = (14, 15, 18, 23, 24)
# 5 bits más significativos del color azul
BLUE = (25, 8, 7, 1, 12)
# Relevador
relay = 20

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
GPIO.setup(RED, GPIO.OUT)
GPIO.setup(GREEN, GPIO.OUT)
GPIO.setup(BLUE, GPIO.OUT)
GPIO.setup(relay, GPIO.OUT)


# Funciones que se llaman en las interrupciones externas
def Boton(channel):
    global Encendido
    Encendido = not Encendido
    GPIO.output(relay, Encendido)
    publish.single("Modulo1/Iluminacion/RGB/Encendido", Encendido, hostname=Broker, qos=1, retain=True)


def Encoder_R(channel):
    global R
    global I
    while GPIO.input(CLK_R) == False:
        pass
    if GPIO.input(DT_R) == False:
        if R <= int(255 * I / 100) - int(IncDec * I / 100):
            R += int(IncDec * I / 100)
        else:
            R = int(255 * I / 100)
    else:
        if R > int(IncDec * I / 100):
            R -= IncDec
        else:
            R = 0
    publish.single("Modulo1/Iluminacion/RGB/Color/R", R, hostname=Broker, qos=1, retain=True)
    GPIO.output(
        RED, (
            int('{0:08b}'.format(R)[3:4]),
            int('{0:08b}'.format(R)[4:5]),
            int('{0:08b}'.format(R)[5:6]),
            int('{0:08b}'.format(R)[6:7]),
            int('{0:08b}'.format(R)[7:8])
        )
    )


def Encoder_G(channel):
    global G
    global I
    while GPIO.input(CLK_G) == False:
        pass
    if GPIO.input(DT_G) == False:
        if G <= int(255 * I / 100) - int(IncDec * I / 100):
            G += int(IncDec * I / 100)
        else:
            G = int(255 * I / 100)
    else:
        if G > int(IncDec * I / 100):
            G -= IncDec
        else:
            G = 0
    publish.single("Modulo1/Iluminacion/RGB/Color/G", G, hostname=Broker, qos=1, retain=True)
    GPIO.output(
        GREEN, (
            int('{0:08b}'.format(G)[3:4]),
            int('{0:08b}'.format(G)[4:5]),
            int('{0:08b}'.format(G)[5:6]),
            int('{0:08b}'.format(G)[6:7]),
            int('{0:08b}'.format(G)[7:8])
        )
    )


def Encoder_B(channel):
    global B
    global I
    while GPIO.input(CLK_B) == False:
        pass
    if GPIO.input(DT_B) == False:
        if B <= int(255 * I / 100) - int(IncDec * I / 100):
            B += int(IncDec * I / 100)
        else:
            B = int(255 * I / 100)
    else:
        if B > int(IncDec * I / 100):
            B -= IncDec
        else:
            B = 0
    publish.single("Modulo1/Iluminacion/RGB/Color/B", B, hostname=Broker, qos=1, retain=True)
    GPIO.output(
        BLUE, (
            int('{0:08b}'.format(B)[3:4]),
            int('{0:08b}'.format(B)[4:5]),
            int('{0:08b}'.format(B)[5:6]),
            int('{0:08b}'.format(B)[6:7]),
            int('{0:08b}'.format(B)[7:8])
        )
    )


def Encoder_I(channel):
    global R
    global G
    global B
    global I
    Ianterior = I
    while GPIO.input(CLK_I) == False:
        pass
    if GPIO.input(DT_I) == False:
        if I < 100:
            I += 1
    else:
        if I > 0:
            I -= 1

    R *= I / Ianterior
    G *= I / Ianterior
    B *= I / Ianterior
    publish.single("Modulo1/Iluminacion/RGB/Intensidad", I, hostname=Broker, qos=1, retain=True)
    GPIO.output(
        RED, (
            int('{0:08b}'.format(R)[3:4]),
            int('{0:08b}'.format(R)[4:5]),
            int('{0:08b}'.format(R)[5:6]),
            int('{0:08b}'.format(R)[6:7]),
            int('{0:08b}'.format(R)[7:8])
        )
    )
    GPIO.output(
        GREEN, (
            int('{0:08b}'.format(G)[3:4]),
            int('{0:08b}'.format(G)[4:5]),
            int('{0:08b}'.format(G)[5:6]),
            int('{0:08b}'.format(G)[6:7]),
            int('{0:08b}'.format(G)[7:8])
        )
    )
    GPIO.output(
        BLUE, (
            int('{0:08b}'.format(B)[3:4]),
            int('{0:08b}'.format(B)[4:5]),
            int('{0:08b}'.format(B)[5:6]),
            int('{0:08b}'.format(B)[6:7]),
            int('{0:08b}'.format(B)[7:8])
        )
    )


# Interrupcion al detectar el flanco de subida del boton pulsador
GPIO.add_event_detect(btn, GPIO.RISING, callback=Boton, bouncetime=300)

# Interrupciones al detectar el flanco de bajada de los diferentes encoders rotatorios
GPIO.add_event_detect(CLK_R, GPIO.FALLING, callback=Encoder_R, bouncetime=50)
GPIO.add_event_detect(CLK_G, GPIO.FALLING, callback=Encoder_G, bouncetime=50)
GPIO.add_event_detect(CLK_B, GPIO.FALLING, callback=Encoder_B, bouncetime=50)
GPIO.add_event_detect(CLK_I, GPIO.FALLING, callback=Encoder_I, bouncetime=50)


# MQTT
def on_connect(client, userdata, flags, rc):
    print("Conectado, codigo resultante: " + str(rc))
    client.subscribe("Modulo1/Iluminacion/RGB/#")


def on_message(client, userdata, msg):
    global R
    global G
    global B
    global I
    global Encendido
    msg.payload = msg.payload.decode("utf-8")
    print(msg.topic + " " + str(msg.payload))
    if msg.topic == "Modulo1/Iluminacion/RGB/Color/R":
        R = int(int(msg.payload) * I / 100)
        GPIO.output(
            RED, (
                int('{0:08b}'.format(R)[3:4]),
                int('{0:08b}'.format(R)[4:5]),
                int('{0:08b}'.format(R)[5:6]),
                int('{0:08b}'.format(R)[6:7]),
                int('{0:08b}'.format(R)[7:8])
            )
        )
    elif msg.topic == "Modulo1/Iluminacion/RGB/Color/G":
        G = int(int(msg.payload) * I / 100)
        GPIO.output(
            GREEN, (
                int('{0:08b}'.format(G)[3:4]),
                int('{0:08b}'.format(G)[4:5]),
                int('{0:08b}'.format(G)[5:6]),
                int('{0:08b}'.format(G)[6:7]),
                int('{0:08b}'.format(G)[7:8])
            )
        )
    elif msg.topic == "Modulo1/Iluminacion/RGB/Color/B":
        B = int(int(msg.payload) * I / 100)
        GPIO.output(
            BLUE, (
                int('{0:08b}'.format(B)[3:4]),
                int('{0:08b}'.format(B)[4:5]),
                int('{0:08b}'.format(B)[5:6]),
                int('{0:08b}'.format(B)[6:7]),
                int('{0:08b}'.format(B)[7:8])
            )
        )
    elif msg.topic == "Modulo1/Iluminacion/RGB/Intensidad":
        Ianterior = I
        I = int(msg.payload)

        R *= I / Ianterior
        G *= I / Ianterior
        B *= I / Ianterior

        GPIO.output(
            RED, (
                int('{0:08b}'.format(R)[3:4]),
                int('{0:08b}'.format(R)[4:5]),
                int('{0:08b}'.format(R)[5:6]),
                int('{0:08b}'.format(R)[6:7]),
                int('{0:08b}'.format(R)[7:8])
            )
        )
        GPIO.output(
            GREEN, (
                int('{0:08b}'.format(G)[3:4]),
                int('{0:08b}'.format(G)[4:5]),
                int('{0:08b}'.format(G)[5:6]),
                int('{0:08b}'.format(G)[6:7]),
                int('{0:08b}'.format(G)[7:8])
            )
        )
        GPIO.output(
            BLUE, (
                int('{0:08b}'.format(B)[3:4]),
                int('{0:08b}'.format(B)[4:5]),
                int('{0:08b}'.format(B)[5:6]),
                int('{0:08b}'.format(B)[6:7]),
                int('{0:08b}'.format(B)[7:8])
            )
        )

    elif msg.topic == "Modulo1/Iluminacion/RGB/Encendido":
        Encendido = int(msg.payload)
        GPIO.output(relay, Encendido)

    print("I: ", I, "R: ", R, "G: ", G, "B: ", B)


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(Broker, 1883, 60)
client.loop_forever()

GPIO.cleanup()
