##
## Scan I2C to see what Addresses are in use.
##

## Commented out print statements are used for debugging purposes
## Uncomment them to follow the flow and data through the program.

from machine import I2C, Pin

def print_devices( i2c, devices ):
    print("In Print I2C Device Addresses")
    print("I2C ID = ", i2c)
    if ( devices ):
        for dev in devices:
            print(hex(dev))

#print("Start I2C Scan")

i2c0 = I2C(0, sda=Pin(8), scl=Pin(9), freq=400000)

i2c1 = I2C(1, sda=Pin(6), scl=Pin(7), freq=400000)

#print("Begin Scan 0")
devices0 = i2c0.scan()
#print("End   Scan 0")

print_devices( i2c0, devices0 )

#print("Begin Scan 1")
devices1 = i2c1.scan()
#print("End   Scan 1")

print_devices( i2c1, devices1 )
