#!/usr/bin/env python
# coding: UTF-8

import Tkinter as tk
from PIL import Image, ImageTk

from threading import Thread
from Queue import Queue
import logging

from serial import Serial

from TimerControl import Timer, TimerControl

import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from numpy import arange

from pandas import Series, DataFrame
import pandas as pd

def hex2int(s, n=None, signed=True):
	if set(s).issubset(set('0123456789ABCDEFabcdef')):
		if n is not None:
			s = s[:n]
		res = int(s, 16)
		if signed and res > (2 ** (4*n - 1) - 1):
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

		logging.info('serial communication set up')

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
	logging.basicConfig(level=logging.INFO, format='(%(threadName)s) %(message)s')

	win = tk.Tk()
	win.title('Artificial Horizon')
	horizon = Horizon(win)
	horizon.pack()
	logging.info('horizon initialized')

	mp = MovingPlot(win)

	q_raw = Queue()

	t_uart = Thread(name="listen to UART", target=listenToSerial, args=(q_raw,))
	t_uart.setDaemon(True)
	t_uart.start()
	logging.info('UART thread started')

	o = Orientation()
	o.calibrate(10)
	t_process = Thread(name="manage raw data", target=o.enqueue_raw_data, args=(q_raw,horizon))
	t_process.setDaemon(True)
	t_process.start()
	logging.info('data processing thread started')

	tim_redraw = Timer(horizon.redraw, delay=0.1, running=True, repeat=True)
	tim_plot = Timer(o.plot, args=mp, delay=1, running=True, repeat=True)
	tctl = TimerControl(updateInterval=0.05, timers=[tim_redraw, tim_plot], running=True)
	logging.info('redraw timer initialized')

	logging.info('entering main loop')
	win.mainloop()

class Orientation():
	sensitivities = {250: 8.75e-3, 500: 17.5e-3, 2000: 70e-3}
	def __init__(self, freq=100., fs=500):
#		self.roll = 0.
#		self.pitch = 0.
#		self.yaw = 0.
		self.freq = freq
		self.fs = fs
		self.sensitivity = Orientation.sensitivities[fs]

		self.ctr = 0
		self.calib_ctr = 0
		self.calib_goal = 0
		self.calib_data = ([], [], [])

		self.cx = 0
		self.cy = 0
		self.cz = 0

#		self.status = [0]
		self.x = [0]
		self.y = [0]
		self.z = [0]


	def enqueue_raw_data(self, src, horizon):
		while True:
			d = src.get() # waiting for data

			logging.debug('data received')
#			self.ctr += 1

			status = hex2int(''.join(d[0:2]), signed=False)
			dy = hex2int(''.join(d[2:6]), 4) * self.sensitivity / self.freq
			dx = hex2int(''.join(d[6:10]), 4) * self.sensitivity / self.freq
			dz = -hex2int(''.join(d[10:14]), 4) * self.sensitivity / self.freq

			if self.calib_ctr > 0:
				self.calib_ctr -= 1
				if self.calib_ctr == 0:
					self.cx = mean(self.calib_data[0])
					self.cy = mean(self.calib_data[1])
					self.cz = mean(self.calib_data[2])
					self.reset()
				else:
					self.calib_data[0].append(dx)
					self.calib_data[1].append(dy)
					self.calib_data[2].append(dz)

#			self.status.append(status)

			# get cumulative sum
			self.x.append(self.x[-1] + dx - self.cx)
			self.y.append(self.y[-1] + dy - self.cy)
			self.z.append(self.z[-1] + dz - self.cz)

			if len(self.x) > 6000:
#				self.status = self.status[-1000:]
				self.x = self.x[-6000:]
				self.y = self.y[-6000:]
				self.z = self.z[-6000:]

#			self.roll += dx
#			self.pitch += dy
#			self.yaw += dz

			if not (status & 0xF0):
				horizon.set_roll(self.x[-1])
				horizon.set_pitch(self.y[-1])

			src.task_done()

	def plot(self, plot):
		ax = plot.figure.axes[0]
		ax.cla()
		ax.set_xlim(0, 6000)
#		ax.set_ylim(-180, 180)

#		r = (arange(len(self.x)) - len(self.x)) / self.freq
		df = DataFrame({'roll': self.x, 'pitch': self.y, 'yaw': self.z})
		logging.info(df.describe())
		df.plot(ax=ax, legend=False)

#		ax.plot(r, self.x, 'r-', r, self.y, 'g-', r, self.z, 'b-')
		plot.draw()

	def calibrate(self, s=10):
		self.calib_data = ([], [], [])
		self.calib_ctr = s*self.freq
		self.calib_goal = s*self.freq
		logging.info('calibration initialized')

	def reset(self):
		self.x = [0]
		self.y = [0]
		self.z = [0]


class Horizon(tk.Canvas):
	def __init__(self, app, **kwargs):
		tk.Canvas.__init__(self, app, width=280, height=280)

		self.roll = 0
		self.pitch = 0

		self.displayed_roll = 0
		self.displayed_pitch = 0

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
		if a > 30:
			a = 30
		elif a < -30:
			a = -30
		self.pitch = a

	def redraw(self):
		logging.debug('redraw horizon')

		if (self.roll != self.displayed_roll) or (self.pitch != self.displayed_pitch):
			self.tkimg_horizon = ImageTk.PhotoImage(self.img_horizon.crop((95, 95-(3*self.pitch), 305, 305-(3*self.pitch))).rotate(self.roll, resample=Image.BICUBIC))
			self.itemconfigure('Horizon', image=self.tkimg_horizon)
			self.displayed_pitch = self.pitch

			if (self.roll != self.displayed_roll):
				self.tkimg_scale = ImageTk.PhotoImage(self.img_scale.rotate(self.roll, resample=Image.BICUBIC))
				self.itemconfigure('Scale', image=self.tkimg_scale)
				self.displayed_roll = self.roll


class MovingPlot(matplotlib.backends.backend_tkagg.FigureCanvasTkAgg):
	def __init__(self, app):
		matplotlib.use('TkAgg')

		self.fig = Figure(figsize=(10,3), dpi=100)
		self.splot = self.fig.add_subplot(111)

		matplotlib.backends.backend_tkagg.FigureCanvasTkAgg.__init__(self, self.fig, master=app)
		self.show()
		self.get_tk_widget().pack()

def mean(l):
	return sum(l) / float(len(l))

initThreads()
