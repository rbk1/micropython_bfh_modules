from machine import I2C
from time import sleep_ms

class MS8607:
   # Variablen definieren
   i2c 					= 	None
   SENS 				= 	None
   OFFSET 				= 	None
   TCS 					= 	None
   TCO 					= 	None
   TREF 				= 	None
   TEMPSENS 				= 	None
   dT 					= 	None
   VTEMP				=	None
   
   # Defines
   ERROR				= 	-255
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
	try:
      	    self.i2c = I2C(0, I2C.MASTER, baudrate=100000)
	except OSError as er:
	    print(er.args[0])
	    return self.ERROR
	return 0

   # Temperatur lesen
   def readTemp(self):
	try:
	    self.i2c.writeto(self.TPADDR, self.com_tempconv)
	    sleep_ms(10)
	    self.i2c.readfrom_mem_into(self.TPADDR, self.ADC_READ_COMMAND, self.data_adc)

	    # Temperatur berrechnen und zurückgeben	
	    rawTemp = ((self.data_adc[0] << 16) + (self.data_adc[1] << 8) + self.data_adc[2]) # 24 Bit aus Buffer
 	    self.dT = rawTemp - (self.TREF * 2**8)	# Temperaturunterschied zu Referenz berrechnen
	    actualTemp = (2000 + (self.dT * (self.TEMPSENS / 2**23))) / 100	# richtige Temperatur berrechnen
	    actualTemp = actualTemp - 15
	    self.VTEMP = actualTemp		# Temperatur in VTEMP speichern für Luftfeuchtigkeit zu kompensieren
    	    return round(actualTemp, 2)
	except OSError as er:
	    print('Temperatursensor funktioniert nicht!')
	    return self.ERROR


   # Luftdruck lesen
   def readPress(self):
	try:
	    self.i2c.writeto(self.TPADDR, self.com_presconv)
	    sleep_ms(50)
	    self.i2c.readfrom_mem_into(self.TPADDR, self.ADC_READ_COMMAND, self.data_adc)
	    
	    # Luftdruck berrechnen und zurückgeben	
	    # 24 Bit aus Buffer
	    rawPress = ((self.data_adc[0] << 16) + (self.data_adc[1] << 8) + self.data_adc[2])
 	    off = (self.OFFSET * 2**17) + ((self.TCO * self.dT) / 2**6)
	    sensitivity = (self.SENS * 2**16) + ((self.TCS * self.dT) / 2**7)
	    actualPress = (((rawPress * sensitivity / 2**21) - off) / 2**15) / 100
    	    return round(actualPress, 2)
	except OSError as er:
	    print('Luftdrucksensor reagiert nicht!')
	    return self.ERROR

   
   # Luftfeuchtigkeit lesen
   def readHum(self):
	try:
	    # Feuchtigkeitsmessung starten, fehler -> Polling nicht unterstützt
	    self.i2c.readfrom_mem_into(self.HADDR, self.MEASURE_COMMAND, self.data_adc)

	except OSError as er:
	    try:
		# Nun sollten die Daten vom Sensor bereit zum einlesen sein,
		# Read Funktion neustarten.
		sleep_ms(10)
	    	humData = self.i2c.readfrom(self.HADDR, 3)

		# Luftfeuchtigkeit berrechnen und zurückgeben
	    	rawHum = (humData[0] << 8) + humData[1]	# 16 Bit aus Buffer, rest CRC check
	    	actualHum = -6 + (125 * (rawHum / 2**16))
	    	if not self.VTEMP == None:
	            compensatedHum = actualHum + ((20 - self.VTEMP) * -0.18) + 35 # -0.18 Temperatur Compensate Coefficient
	            return round(compensatedHum, 2)
	        return round(actualHum, 2)
	    except OSError as er:
	    	print('Luftfeuchtigkeitssensor reagiert nicht!')
	    	return self.ERROR
	

   # Prom lese Sequenz für Sensor Koeffizienten
   def readPROM(self):
	# Prom Addresse 1 definieren
	prom_command = self.SENS_READ_COMMAND	

	try:
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
	except OSError as er:
	    print('PROM konnte nicht gelesen werden!')
	    print('ERROR: Sensor nicht brauchbar!')
	    return self.ERROR
	return 0


   # User Register Setzen auf 11 Bit Humidity Resolution
   def setUserRegister(self):
	try:
	    self.i2c.writeto_mem(self.HADDR, self.WRITE_USER_REGISTER_COMMAND, self.data_userreg)
	except OSError as er:
	    print('UserRegister konnte nicht beschrieben werden!')
	    print('Versuche Sensor trotzdem zu verwenden')
	    return self.ERROR


   def reset(self):
	try:
	    self.i2c.writeto(self.TPADDR, self.com_reset)
	except OSError as er:
	    print('MS8607 konnte nicht neugestartet werden!')
	    #return self.ERROR
	return 0


   # Interrupt deaktivieren und integration time definieren
   def _init(self):
	if self.i2c_init() == self.ERROR:
	    return self.ERROR
    	if self.reset() == self.ERROR:
	    return self.ERROR
	if self.readPROM() == self.ERROR:
	    return self.ERROR
	if self.setUserRegister() == self.ERROR:
	    return self.ERROR


