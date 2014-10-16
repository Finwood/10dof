#!/usr/bin/python2.7
# -*- codung: utf-8 -*-

from pandas import DataFrame, Series
import pandas as ps
import numpy as np

from sys import argv

pd.read_csv('06.log.csv', skiprows=50, nrows=100, names=['time', 'status', 'value'], parse_dates=[0], index_col=0)
