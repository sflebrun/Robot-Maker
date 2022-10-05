##
## Blink LED (GPIO 25)

from machine import Pin
import utime

print("Begin Blinking")

led = Pin(25, Pin.OUT)

while True:
    led.value(1)
    utime.sleep(0.5)
    led.value(0)
    utime.sleep(0.5)
    