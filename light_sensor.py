
import Adafruit_BBIO.ADC as ADC
import time 
import threading
from common_func import *

class LightSensor:
	str_state = ['dark', 'bright']
	state = 0
	old_state = 0
	old_val = 0
	old_static_light_val =0

	
	def __init__(self):
		ADC.setup()


	def checkDarkBrightChange(self,_sv):
		_genIsChanged = 0
		value = ADC.read("P9_40")	
		value = ADC.read_raw("P9_40")
		
		if _sv != self.old_static_light_val:
			self.old_static_light_val = _sv

		else:
			if abs(self.old_val - value) < 20:
				self.old_val = value
				return _genIsChanged, value


		if value < 80:
			self.state = 0
		else:
			self.state = 1

		#print value
		
		if self.old_state != self.state:
			strings = ('state has changed %s to %s Value = %d' % (self.str_state[self.old_state], self.str_state[self.state], value))
			print_staticLightInfo(strings)
			_genIsChanged = [1, self.state]
		self.old_state = self.state
		self.old_val = value
		return _genIsChanged, value 
				


if __name__ == "__main__":


	light_check = LightSensor()
	_list = list()
	while True:
		genIsChanged = light_check.checkDarkBrightChange(100)
		if genIsChanged !=0:
			_list.append(genIsChanged)

		if len(_list) != 0:
			print 'size of list ',len(_list)
			print _list.pop()

		time.sleep(0.05)


