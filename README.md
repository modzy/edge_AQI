# Modzy Edge running on a RaspberryPi
 
Running AI and ML models on an ['Edge' device](https://en.wikipedia.org/wiki/Edge_computing) like a [RaspberryPi](https://www.raspberrypi.com) is easy with Modzy! This repo contains everything necessary to set up an [Air Quality Index](https://www.airnow.gov/aqi/aqi-basics/) sensor to detect current air quality and use that data to generate a next-hour prediction on a RaspberryPi.

See the full documentation here: https://docs.modzy.com/docs/raspberrypi

## Hardware BOM
- [RaspberryPi 3B+](https://www.raspberrypi.com/products/raspberry-pi-3-model-b-plus/)
- [Adafruit PMSA003I Air Quality](http://www.adafruit.com/product/4632)
- [Adafruit SCD-40](http://www.adafruit.com/product/5187)
- 2x [Qwiic JST SH 4-pin Header Cable](https://www.adafruit.com/product/4209)
- [warning light](https://www.amazon.com/gp/product/B097GK4S2D/)
- jumper wires: [M-F](https://www.adafruit.com/product/1952), [M-M](https://www.adafruit.com/product/153)
- [breadboard](https://www.adafruit.com/product/4539)
- battery, if desired

## Software dependencies
- Set up the Pi by following the [RaspberryPi getting started guide](https://www.raspberrypi.com/documentation/computers/getting-started.html).  
- Update the Pi: 
	- `sudo apt-get update`
	- `sudo apt-get upgrade`
	- `sudo apt-get install python3-pip`
	- `sudo pip3 install --upgrade setuptools`
	- `sudo apt-get install -y i2c-tools libgpiod-dev`
- Install libraries:
	- Docker, following [these simple instructions](https://docs.docker.com/engine/install/debian/):  https://docs.docker.com/engine/install/debian/ and allow non-sudo users to use docker by running `sudo groupadd docker, sudo usermod -aG docker $USER`
	- CircuitPy and the libraries to interact with the AQI sensors:
		- `pip3 install --upgrade adafruit-python-shell`
		- `wget https://raw.githubusercontent.com/adafruit/Raspberry-Pi-Installer-Scripts/master/raspi-blinka.py`
		- `sudo python3 raspi-blinka.py`
		- `pip3 install adafruit-circuitpython-scd4x`
		- `pip3 install adafruit-circuitpython-pm25`
	- Finally, install the [Python Modzy-SDK](https://docs.modzy.com/docs/python):
		- `pip install modzy-sdk` or, if you have an unsupported processor `pip install git+https://github.com/modzy/sdk-python.git`

## Run logger and predictor
- Verify the script from this repo executes successfully: `python logger.py`
- Execute this script in the background on startup by creating [`/etc/systemd/system/aqi_logger.service`](https://raw.github.modzy.engineering/modzy-models/edge_air_quality/main/raspi/aqi_logger.service) and set it to autorun with these commands:
	`sudo systemctl daemon-reload`
	`sudo systemctl start aqi_logger.service`
	`sudo systemctl enable aqi_logger.service`
- Set up your [Device and Device Group in Modzy](https://dash.readme.com/project/modzy/v1.1/docs/raspberrypi)
- Execute `python aq_predictor.py` from this repo.
- That's it! You now have a device logging a variety of air quality indicators and running a model to predict what the air quality will be 1 hour in the future!
	- Note this model requires at least 1 hour of data before it can begin to make accurate predictions. 
