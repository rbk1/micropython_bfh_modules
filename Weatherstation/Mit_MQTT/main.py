# Date:		17.05.2017
# Author:	RBK1

# Description:	Main function for the BFH Weatherstation
#		which communicates with the BFH Broker
#		and shows Data on the Demo Circuit.
#		The sensors are: - Temperature
#				 - Pressure
#				 - Humidity
# 				 - Lightsensor (Lux)
# ------------------------------------------------

# Klasse Importieren
from MS8607 import MS8607
from MAX44009 import MAX44009
from time import sleep
from mqtt import MQTTClient
from network import WLAN
import machine
import json

sleep(5)	# 5s Warten bis Boot up vollständig abgeschlossen

# Defines
ERROR 		= 	-255
TOPIC		= 	"bfh_sm/weatherstation/burgdorf"
ID		=	"J08U28M3UU1356RN"
BROKER		=	"192.168.1.3"
LASTWILL	=	{"temp" : 0, "hum" : 0, "press" : 0, "light" : 0, "id" : ID, "time" : ""}

# Variables
sensorTHPError 	= 0
sensorLError 	= 0
timeError 	= 0
vTemp 		= 0
vHum 		= 0
vPress 		= 0
vLux 		= 0
vTime 		= None
counter		= 0

# Objekt instanzieren
sensorTHP = MS8607()
print('Temp.-, Hum.-, Press.sensor imported')

sensorL = MAX44009()
print('Lighsensor imported')

# Funktionen ------------------------------------------------------------------------
def sendMSG():
    # Zeit in korrekte Form bringen
    hour = vTime[3]
    hour = hour + 2
    minute = vTime[4]
    day = vTime[2]
    mounth = vTime[1]
    year = vTime[0]

    message = {"temp" : vTemp, "hum" : vHum, "press" : vPress, "light" : vLux, "id" : ID, "time" : str(hour) + ":" + str(minute) + "," + str(day) + "." + str(mounth) + "." + str(year)}
    client.publish(TOPIC, json.dumps(message), True, 1)


# Main Code -------------------------------------------------------------------------

# Sensoren initialisieren
if sensorTHP._init() == ERROR:
    print('Tempsensor is not responding')
    sensorTHPError = 1
else:
    print('Sensor initialized')

if sensorL._init() == ERROR:
    print('Lightsensor is not responding')
    sensorLError = 1
else:
    print('Lightsensor initialized')


# Prüfen ob Internetverbindung steht
while not wlan.isconnected():
    machine.idle()
print('Wifi connected')

# MQTT initialisieren

client = MQTTClient("weatherstation", BROKER, port=1883, keepalive=10)
client.set_last_will(TOPIC, json.dumps(LASTWILL), True, 1)
if client.connect() == 0:	# Wenn verbindung erfolgreich aufgebaut werden konnte
    print('Connected with Broker', BROKER)
else:
    print('Could not connect to Broker!')

# RTC initialisieren und über das Netzwerk stellen
rtc = machine.RTC()
try:
    rtc.ntp_sync('pool.ntp.org', 3600)
except OSError as er:
    print('RTC konnte nicht über das Internet synchronisiert werden!')


# Sensorwerte über MQTT zum BFH Broker schicken
while True:

    # Nur ausführen wenn THP Sensor funktionstüchtig
    if not sensorTHPError:
        temp = sensorTHP.readTemp()
        if not temp == ERROR:
	    vTemp = temp    
    	
        press = sensorTHP.readPress()
        if not press == ERROR:
    	    vPress = round(press, 2)

        hum = sensorTHP.readHum()
        if not hum == ERROR:
            vHum = hum

    # Nur ausführen wenn Lichtsensor funktionstüchtig
    if not sensorLError:
        lux = sensorL.readLux()
        if not lux == ERROR:
	    vLux = lux

    # Nur ausführen wenn RTC initialisiert werden konnte
    if not timeError:
	vTime = rtc.now()

    sendMSG()
    print('Message sent', counter)
    counter = counter + 1

    sleep(2)
