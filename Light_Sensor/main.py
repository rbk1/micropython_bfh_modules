# Klasse Importieren
from MAX44009 import MAX44009
from time import sleep_ms

# Objekt instanzieren
lightsensor = MAX44009()
print('Lightsensor imported')


sleep_ms(2000)

# I2C konfigurieren
lightsensor.i2c_init()
print('I2C initialized')

sleep_ms(1000)

# Lichsensor konfigurieren
lightsensor.setConfiguration()
print('configuration')

while True:

    lux = lightsensor.readLux()
    print('Lichtstärke in Lux = ', lux)
    sleep_ms(1000)
