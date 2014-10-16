#!/usr/bin/python2.7
# -*- codung: utf-8 -*-

with open('gyro.log') as f:
	for line in f:
		x = int(line)
		print x

