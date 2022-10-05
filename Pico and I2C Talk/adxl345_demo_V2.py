##
## Using Raspberry Pi Pico to use ADXL345 (3 axis accelerometer) in MicroPython
##
## Version 2:  Adds support for LCD 20x4 I2C displays
##
import ssd1306

from machine import I2C, Pin

from pico_i2c_lcd import I2cLcd

import ustruct
import utime
import sys

##--------------------------------------------
## I2C Constants and Variables

I2C_BUS  = 0       # Bus  1
I2C_SDA  = 8       # GPIO 6
I2C_SCL  = 9       # GPIO 7
I2C_FREQ = 400000  # 400kHz


##--------------------------------------------
## ADXL345 Constants
##

## I2C Addresses based on SDO Pin
#  SDO Pin high
ADXL345_ADDR    = 0x1D

#  SDO Pin low
# ADXL345_ADDR  = 0x53

# Registers
REG_DEVID       = 0x00
REG_POWER_CTL   = 0x2D
REG_DATAX0      = 0x32

# Other Constants
ADXL345_DEVID    = 0xE5
SENSITIVITY_2G   = 1.0 / 238.2  # (g/LSB)  -- was 1.0/256 but g was coming out 9.0 instead of 9.8
EARTH_GRAVITY    = 9.80665    # Earth's Graviational Acceleration [m/s^2]
GRAVITY_CONSTANT = SENSITIVITY_2G * EARTH_GRAVITY

##--------------------------------------------
## LCD2004 Constants

LCD2004_ADDR     = 0x27


##--------------------------------------------
## SSD1306 Constants

SSD1306_ADDR     = 0x3C

##--------------------------------------------
## Global Variables

i2c  = None
oled = None
lcd  = None

HAVE_SSD1306    = False
HAVE_ADXL345    = False
HAVE_LCD2004    = False


##--------------------------------------------
## I2C Functions

def reg_write(i2c, addr, reg, data ):
    """
    Writes bytes to the specific register
    """
    
    # Construct message buffer for transfer
    msg = bytearray()
    msg.append(data)
    
    # Write message to I2C Device
    i2c.writeto_mem( addr, reg, msg )
    
def reg_read( i2c, addr, reg, nbytes=1 ):
    """
    Read nbytes from specified register.
    If nbytes > 1, read from sonsecutive registers.
    """
    
    #print("nbytes = ", nbytes)
    
    # Make sure nbytes is 1 or greater.  If not, return empty bytearray
    if ( nbytes < 1 ):
        return bytearray()
    
    # Request nbytes from I2C device, starting at register.
    #print("Read I2C: ", i2c)
    #print("Arguments: Address = ", toHEX(addr), ", Register = ", toHEX(reg), ", NBytes = ", nbytes)
    data = i2c.readfrom_mem( addr, reg, nbytes )
    return data

##--------------------------------------------
## SSD1306 Functions

def display_clear():
    display.fill(0)
    display.show()
    

##--------------------------------------------
## Utility Functions

# toHEX() formats an integer to 0xFF format.
#
# built in hex() converts to 0xff
# string.format() converts to 0XFF
def toHEX(value):
    text = "0x" + f'{value:X}'
    return text

    
##--------------------------------------------
## LCD 20x4 Global Variables
    
LCD_ROWS     =  4
LCD_COLUMNS  = 20
    
##--------------------------------------------
## Iniialization Functions

def detect_devices(i2c):
    global HAVE_ADXL345, HAVE_LCD2004, HAVE_SSD1306
    
    # Obtain a list of I2C Device Addresses that are on this bus
    devices = i2c.scan()
    
    for device in devices:
        print(toHEX(device))
    
    HAVE_ADXL345  = ADXL345_ADDR in devices
    HAVE_LCD2004  = LCD2004_ADDR in devices
    HAVE_SSD1306  = SSD1306_ADDR in devices
    
            
def init():
    global i2c, oled, lcd
    global HAVE_ADXL345, HAVE_LCD2004, HAVE_SSD1306
    
    # Initialize I2C For I2C1 Grove Connector on the Grove Shield for Raspberry Pi Pico
    i2c = I2C( I2C_BUS, sda=Pin(I2C_SDA), scl=Pin(I2C_SCL), freq=I2C_FREQ )

    print("i2c = ", i2c)

    detect_devices(i2c)

    if ( not ( HAVE_SSD1306 or HAVE_LCD2004 ) ):
        print("No Display Devices present -- Abort")
        sys.exit()
        
    if ( not HAVE_ADXL345 ):
        print("No Accelerometer [ADXL345] detected -- Abort")
        sys.exit()
    
    if ( HAVE_SSD1306 ):
        # Initialize Display -- oLED SSD1306 device
        oled = ssd1306.SSD1306_I2C( 128, 64, i2c, addr=SSD1306_ADDR )
        oled.fill(0)
        oled.text("Hello, Mr. LeBrun!", 0,0,1)
        oled.show()
        
    if ( HAVE_LCD2004 ):
        # Initialize Display -- LCD 20x4 device
        lcd = I2cLcd( i2c=i2c, i2c_addr=LCD2004_ADDR, num_lines=LCD_ROWS, num_columns=LCD_COLUMNS)
        lcd.clear()
        lcd.putstr("Hello, Mr. LeBrun!")

    

##--------------------------------------------
## Main Function

# Run Initialization Code
init()
    
# Read Device ID from module
data = reg_read(i2c, ADXL345_ADDR, REG_DEVID)
if ( data != bytearray((ADXL345_DEVID, ))):
    print("ERROR: Device is not an ADXL345")
    print("Byte Array = ", data)
    sys.exit()
    
print("ADXL345 Device ID = ", toHEX(data[0]))

# Read Power Control Register
data = reg_read(i2c, ADXL345_ADDR, REG_POWER_CTL)
print("Power Control Register: ", data)

# Start ADXL345 data collection
data = int.from_bytes(data, "big") | (1 << 3)
print("Data Collection: ", data)
reg_write(i2c, ADXL345_ADDR, REG_POWER_CTL, data)

# Read back Power Control Register
data = reg_read(i2c, ADXL345_ADDR, REG_POWER_CTL)
print("Power Control Register: ", data)

# Give sensor time to start collecting data
utime.sleep(2.0)

# Clear LCD Display
if ( HAVE_LCD2004 ):
    lcd.clear()

# Forever Loop
while True:
    # Read data from sensor
    data = reg_read(i2c, ADXL345_ADDR, REG_DATAX0, 6)
    
    # Convert bytes into data values -- little-endin into 16 bit integer (signed)
    acc_x = ustruct.unpack_from("<h", data, 0)[0]
    acc_y = ustruct.unpack_from("<h", data, 2)[0]
    acc_z = ustruct.unpack_from("<h", data, 4)[0]
    
    # Convert 16 bit values into real measurement values
    acc_x *= GRAVITY_CONSTANT
    acc_y *= GRAVITY_CONSTANT
    acc_z *= GRAVITY_CONSTANT
    
    ## Output Results
   
    # Display to oLED display if present
    if ( HAVE_SSD1306 ):
        oled.fill(0)
        oled.text("Accelerometer", 0, 0, 1)
        oled.text("X Axis: " + "{:5.2f}".format(acc_x), 0, 20, 1)
        oled.text("Y Axis: " + "{:5.2f}".format(acc_y), 0, 32, 1)
        oled.text("Z Axis: " + "{:5.2f}".format(acc_z), 0, 44, 1)
        oled.show()
    
    # Display to LCD display if present
    if ( HAVE_LCD2004 ):
        lcd.move_to(0, 0)
        lcd.putstr("Accelerometer")
        lcd.move_to(0, 1)
        lcd.putstr("X Axis: " + "{:5.2f}".format(acc_x) + "   ")
        lcd.move_to(0, 2)
        lcd.putstr("Y Axis: " + "{:5.2f}".format(acc_y) + "   ")
        lcd.move_to(0, 3)
        lcd.putstr("Z Axis: " + "{:5.2f}".format(acc_z) + "   ")
    
    # How often should we check the accelerometer and display new results?
    # The sleep time (in seconds) determines the cycle rate for this.
    utime.sleep(0.1)



    
##--------------------------------------------
##--------------------------------------------
##--------------------------------------------
##--------------------------------------------
##--------------------------------------------


