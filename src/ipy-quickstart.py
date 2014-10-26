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
p = 'logs/100ORD_32LPF1.06.csv'
df = pd.read_csv(p, index_col=0, converters={'tstamp': ts2dt, 'status': hex2int})
df.drop('status', axis=1, inplace=True)
