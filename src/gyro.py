#!/usr/bin/python2.7
# -*- codung: utf-8 -*-

from pandas import DataFrame, Series
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from sys import argv
path = argv[1]

def hex2int(s):
	return int(s, 16)

from datetime import datetime as dt
def ts2dt(s):
	return dt.fromtimestamp(float(s))

df = pd.read_csv(path, skiprows=50, names=['time', 'status', 'value'], index_col=0, converters={'time': ts2dt, 'status': hex2int})
# do something with status
cs = df.drop('status', axis=1).cumsum(0)
plt.figure()
cs.plot()
plt.show()
