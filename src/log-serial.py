#!/usr/bin/python2.7

from serial import Serial
from sys import argv
from time import time
from struct import unpack

# find -L /dev/serial/by-id/ -samefile /dev/ttyUSB0
s = Serial('/dev/serial/by-id/usb-FTDI_FT232R_USB_UART_A9Y55FFV-if00-port0', 38400, timeout=1)

f = open(argv[1], 'w')

valids = set('0123456789ABCDEFabcdef')
def hexToInt(s, n=2):
	global valids
	if set(s).issubset(valids):
		res = int(s[:n], 16)
		if res > (2 ** (4*n - 1) - 1):
			res -= (2 ** (4*n))
		return res
	else:
		return 0

buf = []

try:
	while 1:
		c = s.read(1)
		if c != '':
			if c == '\n':
				if len(buf) == 6:
					f.write("%f,%2s,%i\n" %(time(), ''.join(buf[0:2]), hexToInt(''.join(buf[2:6]), 4)))
				buf = []
			else:
				buf.append(c)

except KeyboardInterrupt:
	print ('\n--- exiting ---')

finally:
	s.close()
	f.close()

