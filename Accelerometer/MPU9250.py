from machine import I2C
from time import sleep_ms

class MPU9250:
    # Variablen definieren
    i2c 				=	None
    ACCEL_DATA				=	0
    GYRO_DATA				=	0
    TEMP_DATA				=	0
    
    # Defines
    ADDR				=	0x68
    
    CHIP_CONFIGURATION_REGISTER		=	0x1A
    ACCEL_CONFIGURATION_REGISTER	= 	0x1C
    ACCEL_CONFIGURATION2_REGISTER	=	0x1D
    SAMPLE_RATE_DIVIDER_REGISTER	=	0x19
    ACCEL_DATA_X_HIGH_REGISTER		=	0x3B
    ACCEL_DATA_X_LOW_REGISTER		=	0x3C
    ACCEL_DATA_Y_HIGH_REGISTER		=	0x3D
    ACCEL_DATA_Y_LOW_REGISTER		= 	0x3E
    ACCEL_DATA_Z_HIGH_REGISTER		=	0x3F
    ACCEL_DATA_Z_LOW_REGISTER		= 	0x40
    TEMP_DATA_HIGH_REGISTER		=	0x41
    TEMP_DATA_LOW_REGISTER		=	0x42
    GYRO_DATA_X_HIGH_REGISTER		=	0x43
    GYRO_DATA_X_LOW_REGISTER		=	0x44
    GYRO_DATA_Y_HIGH_REGISTER		=	0x45
    GYRO_DATA_Y_LOW_REGISTER		=	0x46
    GYRO_DATA_Z_HIGH_REGISTER		=	0x47
    GYRO_DATA_Z_LOW_REGISTER		=	0x48
    
    CHIP_CONFIGURATION_DATA		=	0x04	# gyro 9.9 ms delay
    ACCEL_CONFIGURATION_DATA		= 	0x08	# Full Scale 4g
    ACCEL_CONFIGURATION2_DATA		=	0x03	# 11.8 ms Delay
    SAMPLE_RATE_DIVIDER_DATA		=	0x13	# Dividing by 20

    # Buffers für I2C Übertragung definieren
    I2C_DATA_BUFFER 			= 	bytearray(1)

    # I2C Schnittstelle definieren
    def i2c_init(self):
    	self.i2c = I2C(0, I2C.MASTER, baudrate=100000)


    def setConfiguration(self):
	# Set Chip Configuration
	self.I2C_DATA_BUFFER[0] = self.CHIP_CONFIGURATION_DATA
	self.i2c.writeto_mem(self.ADDR, self.CHIP_CONFIGURATION_REGISTER, self.I2C_DATA_BUFFER)

        # Set Accel Configuration
	self.I2C_DATA_BUFFER[0] = self.ACCEL_CONFIGURATION_DATA
	self.i2c.writeto_mem(self.ADDR, self.ACCEL_CONFIGURATION_REGISTER, self.I2C_DATA_BUFFER)
	self.I2C_DATA_BUFFER[0] = self.ACCEL_CONFIGURATION2_DATA
	self.i2c.writeto_mem(self.ADDR, self.ACCEL_CONFIGURATION2_REGISTER, self.I2C_DATA_BUFFER)

	# Set Sample Rate Configuration
	self.I2C_DATA_BUFFER[0] = self.SAMPLE_RATE_DIVIDER_DATA
	self.i2c.writeto_mem(self.ADDR, self.SAMPLE_RATE_DIVIDER_REGISTER, self.I2C_DATA_BUFFER)

    # Read Temperatur
    def readTemp(self):
	# High Byte einlesen von Temperatursensor
	self.i2c.readfrom_mem_into(self.ADDR, self.TEMP_DATA_HIGH_REGISTER, self.I2C_DATA_BUFFER)
	self.TEMP_DATA = (self.I2C_DATA_BUFFER[0] << 8)
	# Low Byte einlesen von Temperatursensor
	self.i2c.readfrom_mem_into(self.ADDR, self.TEMP_DATA_LOW_REGISTER, self.I2C_DATA_BUFFER)
	self.TEMP_DATA += (self.I2C_DATA_BUFFER[0])
	actualTempData = self.TEMP_DATA
	return actualTempData

    # Read Gyrometer Functions
    def readGyroX(self):
	# High Byte einlesen von Gyrometer
	self.i2c.readfrom_mem_into(self.ADDR, self.GYRO_DATA_X_HIGH_REGISTER, self.I2C_DATA_BUFFER)
	self.GYRO_DATA = (self.I2C_DATA_BUFFER[0] << 8)
	# Low Byte einlesen von Gyrometer
	self.i2c.readfrom_mem_into(self.ADDR, self.GYRO_DATA_X_LOW_REGISTER, self.I2C_DATA_BUFFER)
	self.GYRO_DATA += (self.I2C_DATA_BUFFER[0])
	actualData = self.GYRO_DATA
	return actualData

    def readGyroY(self):
	# High Byte einlesen von Gyrometer
	self.i2c.readfrom_mem_into(self.ADDR, self.GYRO_DATA_Y_HIGH_REGISTER, self.I2C_DATA_BUFFER)
	self.GYRO_DATA = (self.I2C_DATA_BUFFER[0] << 8)
	# Low Byte einlesen von Gyrometer
	self.i2c.readfrom_mem_into(self.ADDR, self.GYRO_DATA_Y_LOW_REGISTER, self.I2C_DATA_BUFFER)
	actualData = self.GYRO_DATA
	return actualData

    def readGyroZ(self):
	# High Byte einlesen von Gyrometer
	self.i2c.readfrom_mem_into(self.ADDR, self.GYRO_DATA_Z_HIGH_REGISTER, self.I2C_DATA_BUFFER)
	self.GYRO_DATA = (self.I2C_DATA_BUFFER[0] << 8)
	# Low Byte einlesen von Gyrometer
	self.i2c.readfrom_mem_into(self.ADDR, self.GYRO_DATA_Z_LOW_REGISTER, self.I2C_DATA_BUFFER)
	actualData = self.GYRO_DATA
	return actualData

    # Read Accelerometer Functions

    def readAccelX(self):
	# High Byte einlesen von Accelerometer
	self.i2c.readfrom_mem_into(self.ADDR, self.ACCEL_DATA_X_HIGH_REGISTER, self.I2C_DATA_BUFFER)
	self.ACCEL_DATA = (self.I2C_DATA_BUFFER[0] << 8)
	# Low Byte einlesen von Accelerometer
	self.i2c.readfrom_mem_into(self.ADDR, self.ACCEL_DATA_X_LOW_REGISTER, self.I2C_DATA_BUFFER)
	self.ACCEL_DATA += (self.I2C_DATA_BUFFER[0])
	return self.ACCEL_DATA

    def readAccelY(self):
	# High Byte einlesen von Accelerometer
	self.i2c.readfrom_mem_into(self.ADDR, self.ACCEL_DATA_Y_HIGH_REGISTER, self.I2C_DATA_BUFFER)
	self.ACCEL_DATA = (self.I2C_DATA_BUFFER[0] << 8)
	# Low Byte einlesen von Accelerometer
	self.i2c.readfrom_mem_into(self.ADDR, self.ACCEL_DATA_Y_LOW_REGISTER, self.I2C_DATA_BUFFER)
	self.ACCEL_DATA += (self.I2C_DATA_BUFFER[0])
	return self.ACCEL_DATA

    def readAccelZ(self):
	# High Byte einlesen von Accelerometer
	self.i2c.readfrom_mem_into(self.ADDR, self.ACCEL_DATA_Z_HIGH_REGISTER, self.I2C_DATA_BUFFER)
	self.ACCEL_DATA = (self.I2C_DATA_BUFFER[0] << 8)
	# Low Byte einlesen von Accelerometer
	self.i2c.readfrom_mem_into(self.ADDR, self.ACCEL_DATA_Z_LOW_REGISTER, self.I2C_DATA_BUFFER)
	self.ACCEL_DATA += (self.I2C_DATA_BUFFER[0])
	return self.ACCEL_DATA



    # Interrupt deaktivieren und integration time definieren
    def _init(self):
	self.i2c_init()
	self.setConfiguration()




















