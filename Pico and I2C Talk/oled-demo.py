##
## MicroPython Demo for using oLED display that are 128x64 pixels and has I2C
##

from machine import Pin, I2C

import ssd1306

#i2c = I2C(0, sda=Pin(8), scl=Pin(9), freq=400000 )
i2c = I2C(1, sda=Pin(6), scl=Pin(7), freq=400000 )

print("I2C Created: ", i2c)

display = ssd1306.SSD1306_I2C( 128, 64, i2c, addr=0x3C )

display.text("Hello World!", 0,0,1)
display.hline(0, 10, 128, 1)
display.vline(100, 0, 64, 1)
display.show()
