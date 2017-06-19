# boot.py -- run on boot-up

from network import WLAN
from time import sleep_ms

wlan = WLAN()

wlan.init(mode=WLAN.STA)
wlan.connect('WiFi-T204', auth=(WLAN.WPA2, '112233445566778899AABBCCDD'), timeout=5000)
while not wlan.isconnected():
    sleep_ms(50)
print(wlan.ifconfig())
