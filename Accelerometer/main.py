# Klasse Importieren
from MPU9250 import MPU9250
from time import sleep_ms

sleep_ms(4000)

# Objekt instanzieren
sensor = MPU9250()
print('Sensor imported')

# I2C konfigurieren
sensor._init()
print('Sensor initialized')

# Main
while True:

    accelX = sensor.readAccelX()
    print('Beschleunigung in X Richtung = ', accelX)
    accelY = sensor.readAccelY()
    print('Beschleunigung in Y Richtung = ', accelY)
    accelZ = sensor.readAccelZ()
    print('Beschleunigung in Z Richtung = ', accelZ)
    sleep_ms(2000)
