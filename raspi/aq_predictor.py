import pandas as pd
import numpy as np
import glob, os, time
from io import StringIO
import RPi.GPIO as GPIO

from modzy.edge.client import EdgeClient
API_URL, API_KEY = ('127.0.0.1', '<Modzy.APIkey>')
client = EdgeClient(API_URL,55000)

data_count = -12*60-1	#how many datapoints the model expects
list_of_files = glob.glob('logs/*.csv')	#data logger directory

latest_file = max(list_of_files, key=os.path.getctime)
print('Using',latest_file, 'as data source')

red = 17
yellow = 27
green = 22

GPIO.setmode(GPIO.BCM)
GPIO.setup(red, GPIO.OUT, initial=GPIO.LOW) 	#red
GPIO.setup(yellow, GPIO.OUT, initial=GPIO.LOW) 	#yellow
GPIO.setup(green, GPIO.OUT, initial=GPIO.LOW) 	#green

def set_lights(current_co2, predicted_co2):
	if current_co2 <1000:
		GPIO.output(green, GPIO.HIGH)
		GPIO.output(red, GPIO.LOW)
	elif current_co2 >1000:
		GPIO.output(green, GPIO.LOW)
		GPIO.output(red, GPIO.HIGH)
		
	if predicted_co2 <1000:
		GPIO.output(yellow, GPIO.LOW)
	elif predicted_co2 >1000:
		GPIO.output(yellow, GPIO.HIGH)

def load_data(latest_file):
	with open(latest_file) as f:
		small_data = f.readline()
		last_lines = f.readlines()[data_count:]
	
	for line in last_lines:
		small_data += line

	df = pd.read_csv(StringIO(small_data), header=0)
	df.columns = df.columns.str.replace(' ', '')
	y = df['co2'].fillna(0).values[data_count:]
	return(y)

def predict_aq(y):
	job_id = client.submit_embedded("fr5unm0rq8","0.0.1",{"input": y.tobytes()})
	final_job_details = client.block_until_complete(job_id)
	results = client.get_results(job_id)
	return results

pt = int(time.time())
with open('th_logs/prediction_log_'+str(pt)+'.csv', 'w') as writer:
	writer.write('ts, prediction \n')
	while True:
		y = load_data(latest_file)

		if (len(y) < abs(data_count)):
			print('insufficient data has been logged for an accurate prediction, please wait...', str(len(y))+'/'+str(abs(data_count)))
# 			time.sleep(int((abs(data_count) - len(y))/120))

			y1 = np.full(721, y[-1])
			y = np.append(y1, y)

		try:
			prediction = predict_aq(y)
			if not prediction.get('failed',0):
				final_result = (prediction['results']['job']['results.json']['data']['result'])
		except Exception as E:
			print(E)

		ct = int(time.time())
			
		final_result['current'] = y[-1]
		final_result['timestamp'] = ct
		
		print(final_result)
		set_lights(final_result['current'], final_result['next_hour'])

		writer.write(str(final_result['timestamp'])+', '+str(final_result['current'])+'\n')
		writer.flush()
		
		while (ct - pt) < 5:
			time.sleep(1)
			ct = int(time.time())
		pt = ct