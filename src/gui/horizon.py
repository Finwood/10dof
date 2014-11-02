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
	try:
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
	except:
		pass

def initThreads():
	logging.basicConfig(level=logging.DEBUG, format='(%(threadName)s) %(message)s')

	win = tk.Tk()
	win.title('Artificial Horizon')
	horizon = Horizon(win)
	horizon.pack()
	horizon.grid(row=0, column=1)

	q_raw = Queue()

	t_uart = Thread(name="listen to UART", target=listenToSerial, args=(q_raw,))
	t_uart.setDaemon(True)
	t_uart.start()

	o = Orientation()
	t_process = Thread(name="manage raw data", target=o.enqueue_raw_data, args=(q_raw,horizon))
	t_process.setDaemon(True)
	t_process.start()

	win.mainloop()

class Orientation():
	def __init__(self):
		self.roll = 0.0
		self.pitch = 0.0
		self.yaw = 0.0

	def enqueue_raw_data(self, src, horizon):
		while True:
			d = src.get() # waiting for data

			logging.debug('data received')

			(status, dy, dx, dz) = (''.join(d[0:2]), hex2int(''.join(d[2:6]), 4), hex2int(''.join(d[6:10]), 4), -hex2int(''.join(d[10:14]), 4))
			self.roll += dx * 8.75e-5
			self.pitch += dy * 8.75e-5
			self.yaw += dz * 8.75e-5

			horizon.set_roll(self.roll)
			horizon.set_pitch(self.pitch)

			src.task_done()

class Horizon(tk.Canvas):
	def __init__(self, app, **kwargs):
		self.app = app
		tk.Canvas.__init__(self, app, width=280, height=280)

		self.roll = 0
		self.pitch = -90

		self.img_horizon = Image.open('img/horizon.png')
		self.img_frame = Image.open('img/frame.png')
		self.img_scale = Image.open('img/scale.png')

		self.tkimg_horizon = ImageTk.PhotoImage(self.img_horizon)
		self.tkimg_frame = ImageTk.PhotoImage(self.img_frame)
		self.tkimg_scale = ImageTk.PhotoImage(self.img_scale)
		self.create_image(140, 140, image=self.tkimg_horizon, tag='Horizon')
		self.create_image(140, 140, image=self.tkimg_frame, tag='Frame')
		self.create_image(140, 140, image=self.tkimg_scale, tag='Scale')

	def set_roll(self, a):
		self.roll = int(a) % 360

	def set_pitch(self, a):
		a = int(a)
		if a > 90:
			a = 90
		elif a < -90:
			a = -90
		self.pitch = a

	def roll_step(self, step):
		self.roll += step
		self.roll %= 360
		self.redraw()

	def pitch_step(self, step):
		self.pitch += step
		if self.pitch < -90:
			self.pitch = -90
		elif self.pitch > 90:
			self.pitch = 90
		self.redraw()

	def redraw(self):
		logging.debug('redraw horizon')

		self.tkimg_horizon = ImageTk.PhotoImage(self.img_horizon.crop((95, 95-self.pitch, 305, 305-self.pitch)).rotate(self.roll, resample=Image.BICUBIC))
		self.itemconfigure('Horizon', image=self.tkimg_horizon)

		self.tkimg_scale = ImageTk.PhotoImage(self.img_scale.rotate(self.roll, resample=Image.BICUBIC))
		self.itemconfigure('Scale', image=self.tkimg_scale)

def inc():
	global horizon, win
	horizon.roll_step(-1)
	horizon.pitch_step(1)
	win.after(10, inc)

def main():
	global horizon, win
	win = tk.Tk()
	win.title('Artificial Horizon')
	horizon = Horizon(win)
	horizon.pack()
	horizon.grid(row=0, column=1)

	inc()
	win.mainloop()

initThreads()
