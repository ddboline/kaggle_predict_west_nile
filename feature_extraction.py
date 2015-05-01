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

import csv
import gzip

import numpy as np
import pandas as pd

from dateutil.parser import parse

WEATHER_VARS_WITH_M_T = (u'tmax', u'tmin', u'tavg', u'depart', u'dewpoint', 
                         u'wetbulb', u'heat', u'cool', u'snowfall', 
                         u'preciptotal', u'stnpressure', u'sealevel', 
                         u'resultspeed', u'resultdir', u'avgspeed')

WEATHER_PHENOMENA = ('BCFG', 'BLDU', 'BLSN', 'BR', 'DU', 'DZ', 'FG', 'FG+', 
                     'FU', 'FZDZ', 'FZFG', 'FZRA', 'GR', 'GS', 'HZ', 'MIFG', 
                     'PL', 'PRFG', 'RA', 'SG', 'SN', 'SQ', 'TS', 'TSRA', 
                     'TSSN', 'UP', 'VCFG', 'VCTS')

def haversine_distance(lat1, lon1, lat2, lon2):
    r_earth = 6371.
    dlat = np.abs(lat1-lat2)*np.pi/180.
    dlon = np.abs(lon1-lon2)*np.pi/180.
    lat1 *= np.pi/180.
    lat2 *= np.pi/180.
    dist = 2. * r_earth * np.arcsin(
                            np.sqrt(
                                np.sin(dlat/2.)**2 + 
                                    np.cos(lat1) * np.cos(lat2) * 
                                    np.sin(dlon/2.)**2))
    return dist

def feature_extraction():
    spray_df = pd.read_csv('spray.csv.gz', compression='gzip')
    weather_df = pd.read_csv('weather.csv.gz', compression='gzip')
#    train_df = pd.read_csv('train.csv.gz', compression='gzip')
#    test_df = pd.read_csv('test.csv.gz', compression='gzip')
    
    spray_lat_lon_list = []
    for idx, row in spray_df.iterrows():
        spray_lat_lon_list.append((row['Latitude'], row['Longitude']))

    weather_features = []
    weather_labels = list(weather_df.columns)
    for idx, row in weather_df.iterrows():
        rowdict = {k: row[k] for k in weather_labels}
        for k in WEATHER_VARS_WITH_M_T:
            if k in rowdict:
                if rowdict[k] == 'M':
                    rowdict[k] = np.nan
                elif rowdict[k] == 'T':
                    rowdict[k] = 0.0
        for k in rowdict:
            if rowdict[k] == '-':
                rowdict[k] = np.nan
        for ph in WEATHER_PHENOMENA:
            rowdict['wp%s' % ph] = 0
        for ph in rowdict['CodeSum'].split():
            if ph in WEATHER_PHENOMENA:
                rowdict['wp%s' % ph] = 1
        weather_features.append(rowdict)
    for ph in WEATHER_PHENOMENA:
        weather_labels.append('wp%s' % ph)

    for prefix in 'train', 'test':
        with gzip.open('%s.csv.gz' % prefix, 'rb') as csvfile:
            outfile = gzip.open('%s_full.csv.gz' % prefix, 'wb')
            csv_reader = csv.reader(csvfile)
            labels = next(csv_reader)
            
            out_labels = labels + ['n_spray'] + weather_labels
            csv_writer = csv.writer(outfile)
            csv_writer.writerow(out_labels)
            
            for idx, row in enumerate(csv_reader):
                if idx % 1000 == 0:
                    print('processed %d' % idx)
                row_dict = dict(zip(labels, row))
                
                current_date = parse(row_dict['Date'])
                cur_lat = float(row_dict['Latitude'])
                cur_lon = float(row_dict['Longitude'])
                
                row_dict['n_spray'] = 0
                for slat, slon in spray_lat_lon_list:
                    sdist = haversine_distance(cur_lat, cur_lon, slat, slon)
                    if sdist < 2.0:
                        row_dict['n_spray'] += 1

                most_recent = 1000000
                most_recent_w = weather_features[0]
                for wfeat in weather_features:
                    wdate = parse(wfeat['Date'])
                    if current_date.year != wdate.year:
                        continue
                    wdur = abs((current_date - wdate).days)
                    if wdur < most_recent:
                        most_recent = wdur
                        most_recent_w = wfeat
                for lab in weather_labels:
                    if lab == 'Date':
                        continue
                    row_dict[lab] = most_recent_w[lab]
                row_val = [row_dict[col] for col in out_labels]
                csv_writer.writerow(row_val)
                print(row_dict)
    return

if __name__ == '__main__':
    feature_extraction()
