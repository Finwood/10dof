# coding: utf-8
from pandas import DataFrame, Series
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime as dt
def hex2int(s):
	return int(s, 16)
def ts2dt(s):
	return dt.fromtimestamp(float(s))
p = 'logs/100ORD_32LPF1_HPoff.03.csv'
df = pd.read_csv(p, index_col=0, converters={'tstamp': ts2dt, 'status': hex2int})
df.drop('status', axis=1, inplace=True)
pd.set_option('precision',8)

means = Series({'x': -9.80938637630776355535999755375087261199951171, 'y': 5.61844478698632343593999394215643405914306640, 'z': 5.38470368305401603237214658292941749095916748})

