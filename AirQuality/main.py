# Date:		17.05.2017
# Author:	RBK1

# Description:	Main function for the BFH Airqiality Sensor
#		which communicates with the BFH Broker
#		and shows Data on the Demo Circuit.
#	
# ------------------------------------------------

# Klasse Importieren
from time import sleep
from mqtt import MQTTClient
from network import WLAN
import machine
import json




# Main Code

# ADC initialisieren
adc = machine.ADC()
adc1 = adc.channel(pin='P10')

count = 0
# 2 Minuten aufwärmen
print('Aufwärmen')
while count < 10:
    sleep(1)
    count = count + 1
    print(10 - count)


while True:
    
    print(adc1.value())
    sleep(2)
