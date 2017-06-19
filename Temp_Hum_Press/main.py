# Klasse Importieren
from MS8607 import MS8607
from time import sleep_ms

sleep_ms(4000)

# Objekt instanzieren
sensor = MS8607()
print('Sensor imported')

# I2C konfigurieren
sensor._init()
print('Sensor initialized')

# Main
while True:

    temp = sensor.readTemp()
    print('Temperatur in Grad Celsius = ', temp)
    press = sensor.readPress()
    print('Luftdruck in hPa = ', press)
    hum = sensor.readHum()
    if not hum == -255:
        print('Luftfeuchtigkeit in % = ', hum)
    sleep_ms(2000)
