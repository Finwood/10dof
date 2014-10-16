#!/usr/bin/python2.7
# -*- codung: utf-8 -*-

from pandas import DataFrame, Series
import pandas as ps
import numpy as np
import matplotlib.pyplot as plt

from sys import argv

df = pd.read_csv('06.log.csv', skiprows=50, nrows=100, names=['time', 'status', 'value'], parse_dates=[0], index_col=0)
df = df[df.status == '0C']
df.drop('status', axis=1, inplace=True)
cs = df.cumsum(0)
plt.figure()
cs.plot()
plt.show()
