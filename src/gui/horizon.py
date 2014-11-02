#!/usr/bin/env python
# coding: UTF-8

from functools import partial
import Tkinter as tk
from PIL import Image, ImageTk

from threading import Thread
from Queue import Queue
import logging

from serial import Serial


def hex2int(s, n=None, signedInt=True):
	if set(s).issubset(set('0123456789ABCDEFabcdef')):
		if n is not None:
			s = s[:n]
		res = int(s, 16)
		if signedInt and res > (2 ** (4*n - 1) - 1):
			res -= (2 ** (4*n))
		return res
	else:
		return 0

def ts2dt(s):
	return dt.fromtimestamp(float(s))

def listenToSerial(dest):
	# find -L /dev/serial/by-id/ -samefile /dev/ttyUSB0
	s = Serial('/dev/serial/by-id/usb-FTDI_FT232R_USB_UART_A9Y55FFV-if00-port0', 38400, timeout=1)
	buf = []

	try:
		while True:
			c = s.read(1)
			if c != '':
				if c == '\n':
					if len(buf) == 14:
						dest.put(buf)
					buf = []
				else:
					buf.append(c)
	except:
		pass
	finally:
		s.close()

def manageRawData(src):
	# init
	while True:
		d = src.get()
		(status, dx, dy, dz) = (''.join(buf[0:2]), hex2int(''.join(buf[2:6]), 4), hex2int(''.join(buf[6:10]), 4), hex2int(''.join(buf[10:14]), 4))
		# do something
		src.task_done()

def initThreads():
	q_raw = Queue()
	t_uart = Thread(name="listen to UART", target=listenToSerial, args=(q_raw,))
	t_uart.setDaemon(True)
	t_uart.start()
	t_process = Thread(name="manage raw data", target=manageRawData, args=(q_raw,))
	t_process.setDaemon(True)
	t_process.start()

class Horizon(tk.Canvas):
	def __init__(self, app, **kwargs):
		self.app = app
		tk.Canvas.__init__(self, app, width=280, height=280)

		self.roll = 0
		self.droll = 0
		self.pitch = 0
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
		command=partial(horizon.roll_step, 5)).pack(fill='x')
	tk.Button(button_frame, text="<---", height=3,
		command=partial(horizon.roll_step, -5)).pack(fill='x')
	tk.Button(button_frame, text="Beenden", width=40, height=3,
		command=app_win.destroy).pack()

	horizon.grid(row=0, column=1)
	button_frame.grid(row=0, column=2)

	app_win.after(100, inc)
	app_win.mainloop()

main()
