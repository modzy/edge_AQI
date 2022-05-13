import time
import adafruit_scd4x, board, busio
from digitalio import DigitalInOut, Direction, Pull
from adafruit_pm25.i2c import PM25_I2C

PM25_sensor_init = False
while not PM25_sensor_init:
	try:
		print('Initializing PM25 sensor...')
		i2c = busio.I2C(board.SCL, board.SDA, frequency=100000)
		pm25 = PM25_I2C(i2c, None)
		PM25_sensor_init = True
	except:
		continue

SCD40_sensor_init = False
while not SCD40_sensor_init:
	try:
		print('Initializing SCD40 sensor...')
		i2c = board.I2C()
		scd4x = adafruit_scd4x.SCD4X(i2c)
		SCD40_sensor_init = True
		print("Serial number:", [hex(i) for i in scd4x.serial_number])
		scd4x.start_periodic_measurement()
	except:
		continue

pt = int(time.time())
with open('logs/data_log_'+str(pt)+'.csv', 'w') as writer:
	i = 0
	writer.write('ts, t1, h1, t2, h2, co2, pm1.0s, pm2.5s, pm10.0s, pm1.0e, pm2.5e, pm10.0e, pm0.3, pm0.5, pm1.0, pm2.5, pm5.0, pm10.0\n')
	
	while True:		 
		if scd4x.data_ready:
			try:
				scd4x_CO2 = scd4x.CO2
			except:
				scd4x_CO2 = 0
			try:
				scd4x_temperature = scd4x.temperature
			except:
				scd4x_temperature = 0
			try:
				scd4x_relative_humidity = scd4x.relative_humidity
			except:
				scd4x_relative_humidity = 0
		else:
			continue

		try:
			aqdata = pm25.read()
		except RuntimeError:
			print("Unable to read from PM25 sensor, retrying...")
			continue

		t = 0 # temperature from the old HTU21D sensor, kept only to keep data log format consistent
		h = 0 # humidiy from the old HTU21D sensor, kept only to keep data log format consistent
	
		ct = int(time.time())
		i+=1
		
		print(i, ct, t, h, scd4x_temperature, scd4x_relative_humidity, scd4x_CO2,
			aqdata["pm10 standard"], 
			aqdata["pm25 standard"], 
			aqdata["pm100 standard"],
			aqdata["pm10 env"], 
			aqdata["pm25 env"], 
			aqdata["pm100 env"],
			aqdata["particles 03um"],
			aqdata["particles 05um"],
			aqdata["particles 10um"],
			aqdata["particles 25um"],
			aqdata["particles 50um"],
			aqdata["particles 100um"]
		)
		
		writer.write(str(ct)+', '+str(t)+', '+str(h)+', '
			+str(scd4x_temperature)+', '
			+str(scd4x_relative_humidity)+', '
			+str(scd4x_CO2)+', '
			+str(aqdata["pm10 standard"])+', '
			+str(aqdata["pm25 standard"])+', '
			+str(aqdata["pm100 standard"])+', '
			+str(aqdata["pm10 env"])+', '
			+str(aqdata["pm25 env"])+', ' 
			+str(aqdata["pm100 env"])+', '
			+str(aqdata["particles 03um"])+', '
			+str(aqdata["particles 05um"])+', '
			+str(aqdata["particles 10um"])+', '
			+str(aqdata["particles 25um"])+', '
			+str(aqdata["particles 50um"])+', '
			+str(aqdata["particles 100um"])
			+'\n')

		writer.flush()
		
		while (ct - pt) < 5:
			time.sleep(1)
			ct = int(time.time())
		pt = ct		  