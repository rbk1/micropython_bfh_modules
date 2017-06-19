from machine import UART
from time import sleep_ms

class CAM:
   # Variablen definieren
   i2c 					= 	None
   SENS 				= 	None
   OFFSET 				= 	None
   TCS 					= 	None
   TCO 					= 	None
   TREF 				= 	None
   TEMPSENS 				= 	None
   dT 					= 	None
   
   # Defines
   RESET_COMMAND 			= 	0x1E
   SENS_READ_COMMAND 			= 	0xA2
   OFFSET_READ_COMMAND 			= 	0xA4
   TCS_READ_COMMAND 			= 	0xA6
   TCO_READ_COMMAND 			= 	0xA8
   TREF_READ_COMMAND 			= 	0xAA
   TEMPSENS_READ_COMMAND 		=	0xAC
   PRESSURE_CONVERSION_COMMAND 		= 	0x48
   TEMPERATURE_CONVERSION_COMMAND 	= 	0x58
   ADC_READ_COMMAND 			= 	0x00
   WRITE_USER_REGISTER_COMMAND 		= 	0xE6
   USER_REGISTER_DATA 			= 	0x01
   MEASURE_COMMAND 			= 	0xF5
   TPADDR				=	0x76	# Temp, Pressure Addresse
   HADDR				= 	0x40	# Humidity Addresse
   
   # Buffers für I2C Datenübertragung definieren
   com_reset 				= 	bytearray(1)
   com_presconv 			= 	bytearray(1)
   com_tempconv 			= 	bytearray(1)
   com_userreg 				= 	bytearray(1)
   data_userreg 			= 	bytearray(1)
 
   # Buffers um die Informationen einzulesen
   data_prom 				= 	bytearray(2)
   data_adc 				= 	bytearray(3)

   # Buffer mit Werte füllen
   com_reset[0] 			= 	RESET_COMMAND
   com_presconv[0] 			= 	PRESSURE_CONVERSION_COMMAND
   com_tempconv[0] 			= 	TEMPERATURE_CONVERSION_COMMAND
   data_userreg[0] 			= 	USER_REGISTER_DATA


   # I2C Schnittstelle definieren
   def i2c_init(self):
      self.i2c = I2C(0, I2C.MASTER, baudrate=100000)


   # Temperatur lesen
   def readTemp(self):
	self.i2c.writeto(self.TPADDR, self.com_tempconv)
	sleep_ms(10)
	self.i2c.readfrom_mem_into(self.TPADDR, self.ADC_READ_COMMAND, self.data_adc)
	
	# Temperatur berrechnen und zurückgeben	
	rawTemp = ((self.data_adc[0] << 16) + (self.data_adc[1] << 8) + self.data_adc[2]) # 24 Bit aus Buffer
 	self.dT = rawTemp - (self.TREF * 2**8)			# Temperaturunterschied zu Referenz berrechnen
	actualTemp = (2000 + (self.dT * (self.TEMPSENS / 2**23))) / 100	# richtige Temperatur berrechnen
    	return actualTemp


   # Luftdruck lesen
   def readPress(self):
	self.i2c.writeto(self.TPADDR, self.com_presconv)
	sleep_ms(50)
	self.i2c.readfrom_mem_into(self.TPADDR, self.ADC_READ_COMMAND, self.data_adc)
	
	# Luftdruck berrechnen und zurückgeben	
	rawPress = ((self.data_adc[0] << 16) + (self.data_adc[1] << 8) + self.data_adc[2]) # 24 Bit aus Buffer
 	off = (self.OFFSET * 2**17) + ((self.TCO * self.dT) / 2**6)
	sensitivity = (self.SENS * 2**16) + ((self.TCS * self.dT) / 2**7)
	actualPress = (((rawPress * sensitivity / 2**21) - off) / 2**15) / 100
    	return actualPress

   
   # Luftfeuchtigkeit lesen
   def readHum(self):
	self.i2c.readfrom_mem_into(self.HADDR, self.MEASURE_COMMAND, self.data_adc)

	# Luftfeuchtigkeit berrechnen und zurückgeben
	rawHum = (self.data_adc[0] << 8) + self.data_adc[1]	# 16 Bit aus Buffer, rest CRC check
	actualHum = -6 + (125 * (rawHum / 2**16))		
	return actualHum
	

   # Prom lese Sequenz für Sensor Koeffizienten
   def readPROM(self):
	# Prom Addresse 1 definieren
	prom_command = self.SENS_READ_COMMAND	

	# Jede Prom Addresse auslesen
	while (prom_command != 0xFF):
  	   self.i2c.readfrom_mem_into(self.TPADDR, prom_command, self.data_prom)

	   if prom_command == self.SENS_READ_COMMAND:
	      self.SENS = (self.data_prom[0] << 8) + self.data_prom[1]
	      prom_command = self.OFFSET_READ_COMMAND		# Buffer auf 2. PROM Addresse stellen
	   
	   elif prom_command == self.OFFSET_READ_COMMAND:
	      self.OFFSET = (self.data_prom[0] << 8) + self.data_prom[1]
	      prom_command = self.TCS_READ_COMMAND		# Buffer auf 3. PROM Addresse stellen
	   
	   elif prom_command == self.TCS_READ_COMMAND:
	      self.TCS = (self.data_prom[0] << 8) + self.data_prom[1]
	      prom_command = self.TCO_READ_COMMAND		# Buffer auf 4. PROM Addresse stellen
	   
	   elif prom_command == self.TCO_READ_COMMAND:
	      self.TCO = (self.data_prom[0] << 8) + self.data_prom[1]
	      prom_command = self.TREF_READ_COMMAND		# Buffer auf 5. PROM Addresse stellen
	   
	   elif prom_command == self.TREF_READ_COMMAND:
	      self.TREF = (self.data_prom[0] << 8) + self.data_prom[1]
	      prom_command = self.TEMPSENS_READ_COMMAND		# Buffer auf 6. PROM Addresse stellen
	   
	   elif prom_command == self.TEMPSENS_READ_COMMAND:
	      self.TEMPSENS = (self.data_prom[0] << 8) + self.data_prom[1]
	      prom_command = 0xFF				# While Schlaufe verlassen


   # User Register Setzen auf 11 Bit Humidity Resolution
   def setUserRegister(self):
	self.i2c.writeto_mem(self.HADDR, self.WRITE_USER_REGISTER_COMMAND, self.data_userreg)

	#self.i2c.start()
	#self.i2c.write(self.Haddrw)		# Addresse für Feuchtigkeitssensor schicken
	#self.i2c.write(self.com_userreg)	# Command für User Register Setzen schicken
	#self.i2c.write(self.data_userreg)	# User Register Daten senden
	#self.i2c.stop()
	#return 0


   def reset(self):
	self.i2c.writeto(self.TPADDR, self.com_reset)

	#self.i2c.start()
	#self.i2c.write(self.TPaddrw)		# Addresse für Temperatursensor schicken
	#self.i2c.write(self.com_reset)		# Command für Reset
	#self.i2c.stop()
	#return 0


   # Interrupt deaktivieren und integration time definieren
   def _init(self):
	self.i2c_init()
    	self.reset()
	self.readPROM()
	self.setUserRegister()


