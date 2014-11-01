#!/usr/bin/env python
# coding: UTF-8

from functools import partial
try:
	import tkinter as tk
except:
	import Tkinter as tk
from PIL import Image, ImageTk
from math import sin, cos, pi

import threading
import logging

from serial import Serial

valids = set('0123456789ABCDEFabcdef')
def hexToInt(s, n=2): # signed int
	global valids
	if set(s).issubset(valids):
		res = int(s[:n], 16)
		if res > (2 ** (4*n - 1) - 1):
			res -= (2 ** (4*n))
		return res
	else:
		return 0

def listenToSerial():
	# find -L /dev/serial/by-id/ -samefile /dev/ttyUSB0
	s = Serial('/dev/serial/by-id/usb-FTDI_FT232R_USB_UART_A9Y55FFV-if00-port0', 38400, timeout=1)
	buf = []
	global horizon

	try:
		while 1:
			c = s.read(1)
			if c != '':
				if c == '\n':
					if len(buf) == 14:
						f.write("%2s,%i,%i,%i\n" %(''.join(buf[0:2]), hexToInt(''.join(buf[2:6]), 4), hexToInt(''.join(buf[6:10]), 4), hexToInt(''.join(buf[10:14]), 4)))
					buf = []
				else:
					buf.append(c)
	except:
		s.close()

STEP = 5

class Horizon(tk.Canvas):
	def __init__(self, app, **kwargs):
		self.app = app
		tk.Canvas.__init__(self, app, width=280, height=280)

		self.roll = 0
		self.droll = 0
		self.pitch = 30
		self.dpitch = 0

		self.img_horizon = Image.open('img/horizon.png')
		self.img_frame = Image.open('img/frame.png')
		self.img_scale = Image.open('img/scale.png')

		self.tkimg_horizon = ImageTk.PhotoImage(self.img_horizon)
		self.tkimg_frame = ImageTk.PhotoImage(self.img_frame)
		self.tkimg_scale = ImageTk.PhotoImage(self.img_scale)
		self.create_image(140, 140, image=self.tkimg_horizon, tag='Horizon')
		self.create_image(140, 140, image=self.tkimg_frame, tag='Frame')
		self.create_image(140, 140, image=self.tkimg_scale, tag='Scale')

	def roll_step(self, step):
		self.droll += step
		self.roll = self.droll%360
		self.redraw()

	def redraw(self):
		self.tkimg_horizon = ImageTk.PhotoImage(self.img_horizon.rotate(self.roll, resample=Image.BICUBIC))
		self.itemconfigure('Horizon', image=self.tkimg_horizon)
		self.coords('Horizon', 140 + self.pitch * sin(self.roll / 180.0 * pi), 140 + self.pitch * cos(self.roll / 180.0 * pi)) # läuft!

		self.tkimg_scale = ImageTk.PhotoImage(self.img_scale.rotate(self.roll, resample=Image.BICUBIC))
		self.itemconfigure('Scale', image=self.tkimg_scale)

def inc():
	global horizon, app_win
	horizon.roll_step(-1)
	app_win.after(100, inc)

def main():
	global horizon, app_win
	app_win = tk.Tk()
	app_win.title('Artificial Horizon')
	horizon = Horizon(app_win)
	horizon.pack()
	button_frame = tk.Frame(app_win)

	tk.Button(button_frame, text="--->", height=3,
		command=partial(horizon.roll_step, STEP)).pack(fill='x')
	tk.Button(button_frame, text="<---", height=3,
		command=partial(horizon.roll_step, -STEP)).pack(fill='x')
	tk.Button(button_frame, text="Beenden", width=40, height=3,
		command=app_win.destroy).pack()

	horizon.grid(row=0, column=1)
	button_frame.grid(row=0, column=2)

	app_win.after(100, inc)
	app_win.mainloop()

main()
