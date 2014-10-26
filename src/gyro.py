#!/usr/bin/python2.7
# codung: utf-8

from pandas import DataFrame, Series
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime as dt

from sys import argv

def hex2int(s):
	return int(s, 16)

def ts2dt(s):
	return dt.fromtimestamp(float(s))

for p in argv[1:]:
#	fig, axes = plt.subplots(2, 1)
	fig, axes = plt.subplots(3, 1)
	df = pd.read_csv(p, index_col=0, converters={'tstamp': ts2dt, 'status': hex2int})
	if (df.status != 0x0F).sum() > 0:
		print "irgendetwas stimmt mit den Stati nicht, bitte guck selbst nach."
	else:
		print p
		df.drop('status', axis=1, inplace=True)
		(df * 8.75e-5 * 0.5).plot(ax=axes[0])
		(df * 8.75e-5 * 0.5).cumsum().plot(ax=axes[1])
		(df * 8.75e-5 * 0.5).cumsum().cumsum().plot(ax=axes[2])
#		((df.cumsum() - df[:500].cumsum().mean()) * 8.75e-5).cumsum().plot(ax=axes[1])
#		(df * 8.75e-5).cumsum().plot(ax=axes[1])
#		((df - df[:100].mean()) * 8.75e-5).cumsum().plot(ax=axes[1])
		fig.show()

raw_input()
