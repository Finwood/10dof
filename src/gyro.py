#!/usr/bin/python2.7
# -*- codung: utf-8 -*-

from sys import argv
import re

# [2014-10-16 12:13:32.311] C: -22
preg = re.compile('\[([^\]]+)\] (0|C): (-?\d+)')
print ';'.join(["'%s'" %item for item in ('time', 'status', 'value')])

for line in open(argv[1]):
	m = preg.match(line)
	if m:
		print ';'.join(["'%s'" %item for item in m.groups()])

