from common_func import print_IRinfo

class IrDataProc:
	ALL_KEY = 10
	def __init__(self):
		print 'IrData Loded'
	
	def Print_IrData(self, rx_data):
		if type(rx_data) == str:
			for i in range(10):
				strs = 'mode'+str(i)
				if rx_data[3:-2] == strs:
					printstr = ('%s selected' % strs)
					print_IRinfo(printstr)
					return i

				elif rx_data[3:-2] == 'end':
					printstr = ('End Command')
					print_IRinfo(printstr)
					return 0xf
		return False


if __name__ == "__main__":
	print 'hello'

