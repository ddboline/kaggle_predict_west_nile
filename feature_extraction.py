#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Created on Fri May  1 16:28:06 2015

@author: ddboline
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import pandas as pd

from dateutil.parser import parse

def feature_extraction():
    spray_df = pd.read_csv('spray.csv.gz', compression='gzip')
    weather_df = pd.read_csv('weather.csv.gz', compression='gzip')
    
    spray_lat_lon_list = []
    for idx, row in spray_df.iterrows():
        spray_lat_lon_list.append((row['Latitude'], row['Longitude']))
    
    for idx, row in weather_df.iterrows():
        print(row)
        exit(0)
    return

if __name__ == '__main__':
    feature_extraction()
