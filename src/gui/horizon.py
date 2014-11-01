#!/usr/bin/env python
# coding: UTF-8

from functools import partial
try:
	import tkinter as tk
except:
	import Tkinter as tk
from PIL import Image, ImageTk
from math import sin, cos, pi

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

	def pitch_step(self, step):
		self.dpitch += step
		self.pitch = self.dpitch%360
		self.redraw()

	def redraw(self):
		self.tkimg_horizon = ImageTk.PhotoImage(self.img_horizon.crop((95, 95-self.pitch, 305, 305-self.pitch)).rotate(self.roll, resample=Image.BICUBIC))
		self.itemconfigure('Horizon', image=self.tkimg_horizon)

		self.tkimg_scale = ImageTk.PhotoImage(self.img_scale.rotate(self.roll, resample=Image.BICUBIC))
		self.itemconfigure('Scale', image=self.tkimg_scale)

def inc():
	global horizon, app_win
	horizon.roll_step(-1)
#	horizon.pitch_step(1)
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
