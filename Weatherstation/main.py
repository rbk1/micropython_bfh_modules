# Klasse Importieren
from MS8607 import MS8607
from MAX44009 import MAX44009
from time import sleep_ms

sleep_ms(4000)	# Warten bis Boot up vollständig abgeschlossen

# Defines
ERROR = -255

# Variables
sensorTHPError = 0
sensorLError = 0

# Objekt instanzieren
sensorTHP = MS8607()
print('Temp.-, Hum.-, Press.sensor imported')

sensorL = MAX44009()
print('Lighsensor imported')


# I2C konfigurieren
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

# Main
while True:

    if not sensorTHPError:
        temp = sensorTHP.readTemp()
        if not temp == ERROR:
    	    print('Temperatur \t\t= {:2.2f} C°'.format(temp))
        press = sensorTHP.readPress()
        if not press == ERROR:
    	    print('Luftdruck \t\t= {:4.2f} hPa'.format(press))
        hum = sensorTHP.readHum()
        if not hum == ERROR:
            print('Luftfeuchtigkeit \t= {:3.2f} %'.format(hum))

    if not sensorLError:
        lux = sensorL.readLux()
        if not lux == ERROR:
	    print('Lichtstärke \t\t= {:6.2f} Lux'.format(lux))
        print('\n------------------------------------\n')
    sleep_ms(5000)
