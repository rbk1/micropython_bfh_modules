from machine import Pin, I2C
#from time import sleep_ms

class MAX44009:
   i2c = None
   
   # Defines
   INTERRUPT_DESABLE_REG = 0x01
   CONFIGURATION_REG = 0x02
   HIGH_LUX_DATA = 0x03
   LOW_LUX_DATA = 0x04
   ADDRESS = 0x4A
   ERROR = -255
   
   # Buffers für I2C Datenübertragung definieren
   comInDis = bytearray(1)
   comConfig = bytearray(1)

   # Buffer um die Lux information einzulesen
   data_high = bytearray(1)
   data_low = bytearray(1)

   comInDis[0] = 0x00				# Command für User Interrupt Desable
   comConfig[0] = CONFIGURATION_REG		# Command für User Sensor Konfiguration 


   # I2C Schnittstelle definieren
   def i2c_init(self):
	try:
            self.i2c = I2C(0, I2C.MASTER, baudrate=100000)
	except OSError as er:
	    print(er.args[0])
	    return self.ERROR
	return 0

   # Lux lesen
   def readLux(self):
	try:
	    self.i2c.readfrom_mem_into(self.ADDRESS, self.HIGH_LUX_DATA, self.data_high)

	    # Lux berrechnen und zurückgeben	
	    exponent = (self.data_high[0] >> 4)		# Exponent berrechnen
            mantissa = (self.data_high[0] & 0x0F)		# Mantissa berrechnen
	    actualLux = ((2**exponent)*mantissa*0.72)	# Lux berrechnen
    	    return round(actualLux, 0)
	except OSError as er:
	    print('ERROR, lightsensor not responding!')
	    print(er.args[0])
	    return self.ERROR


   # Interrupt deaktivieren und integration time definieren
   def setConfiguration(self):
	try:
	    # Interrupt Einstellungen deaktivieren (Ohne Interrupt)
	    self.i2c.writeto_mem(self.ADDRESS, self.INTERRUPT_DESABLE_REG, self.comInDis)
	
	    # Sensor konfigurieren
	    self.i2c.writeto_mem(self.ADDRESS, self.CONFIGURATION_REG, self.comConfig)
	except OSError as er:
	    print('Could not set lightsensor configuration!')
	    print(er.args[0])
	    return self.ERROR
	return 0


   def _init(self):
	if self.i2c_init() == self.ERROR:
	    return self.ERROR
	
	if self.setConfiguration() == self.ERROR:
	    return self.ERROR
	return 0
	    













