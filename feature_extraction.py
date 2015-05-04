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

WEATHER_VARS_WITH_M_T = (u'Tmax', u'Tmin', u'Tavg', u'Depart', u'DewPoint',
                         u'WetBulb', u'Heat', u'Cool', u'Snowfall',
                         u'PrecipTotal', u'StnPressure', u'SeaLevel',
                         u'ResultSpeed', u'ResultDir', u'AvgSpeed', u'Water1')

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

def lat_lon_box(lat, lon, dist):
    r_earth = 6371.
    d_2r = dist/(2.*r_earth)
    dlat = 2. * (d_2r)
    dlon = 2. * np.arcsin((np.sin(d_2r))/(np.cos(lat)))
    dlat *= 180./np.pi
    dlon *= 180./np.pi
    return abs(dlat), abs(dlon)

def feature_extraction():
    spray_df = pd.read_csv('spray.csv.gz', compression='gzip')

    spray_lat_lon_list = []
    for idx, row in spray_df.iterrows():
        spray_lat_lon_list.append((row['Latitude'], row['Longitude']))

    weather_features = []
    cumu_labels = ('Tmax', 'Tmin', 'PrecipTotal')
    cumu_features = {}
    cumu_total = 0
    current_year = -1
    with gzip.open('weather.csv.gz', 'r') as wfile:
        wcsv = csv.reader(wfile)
        weather_labels = next(wcsv)
        for row in wcsv:
            rowdict = dict(zip(weather_labels, row))
            rowdict['Date'] = parse(rowdict['Date'])
            current_date = rowdict['Date']
            if current_date.year != current_year:
                current_year = current_date.year
                cumu_features = {k: 0 for k in cumu_labels}
                cumu_total = 0
            for k in WEATHER_VARS_WITH_M_T:
                if k in rowdict:
                    rowdict[k] = rowdict[k].replace('M', 'nan')
                    rowdict[k] = rowdict[k].replace('T', '0.0')
            for k in rowdict:
                if rowdict[k] == '-':
                    rowdict[k] = 'nan'
                if type(rowdict[k]) == str:
                    rowdict[k] = rowdict[k].strip()
            for ph in WEATHER_PHENOMENA:
                rowdict['wp%s' % ph] = '0'
            for ph in rowdict['CodeSum'].split():
                if ph in WEATHER_PHENOMENA:
                    rowdict['wp%s' % ph] = '1'
            for lab in cumu_labels:
                _tmp = float(rowdict[lab])
                if not np.isnan(_tmp):
                    cumu_features[lab] += _tmp
            cumu_total += 1
            for lab in ('Tmax', 'Tmin', 'PrecipTotal'):
                rowdict['%s_cumu' % lab] = cumu_features[lab] / cumu_total
            weather_features.append(rowdict)
#            print('\n'.join(['%s: %s' % (k, rowdict[k]) for k in rowdict]))
#            exit(0)
    for ph in WEATHER_PHENOMENA:
        weather_labels.append('wp%s' % ph)
    for lab in cumu_labels:
        weather_labels.append('%s_cumu' % lab)


    for prefix in 'train', 'test':
        with gzip.open('%s.csv.gz' % prefix, 'rb') as csvfile:
            outfile = gzip.open('%s_full.csv.gz' % prefix, 'wb')
            csv_reader = csv.reader(csvfile)
            labels = next(csv_reader)

            out_labels = labels +\
                         ['n_spray_%d' % x for x in range(1,11)]
            for lab in weather_labels:
                if lab == 'Date':
                    continue
                out_labels.append(lab)

            csv_writer = csv.writer(outfile)
            csv_writer.writerow(out_labels)

            for idx, row in enumerate(csv_reader):
                if idx % 1000 == 0:
                    print('processed %d' % idx)
#                if idx > 100:
#                    exit(0)
                row_dict = dict(zip(labels, row))

                current_date = parse(row_dict['Date'])
                cur_lat = float(row_dict['Latitude'])
                cur_lon = float(row_dict['Longitude'])

                for idx in range(1, 11):
                    row_dict['n_spray_%d' % idx] = 0
                dlat, dlon = lat_lon_box(cur_lat, cur_lon, 1.5)
                for slat, slon in spray_lat_lon_list:
#                    print(dlat, dlon, abs(slat-cur_lat), abs(slon-cur_lon))
                    if abs(slat-cur_lat) > dlat or abs(slon-cur_lon) > dlon:
                        continue
                    sdist = haversine_distance(cur_lat, cur_lon, slat, slon)
                    for idx in range(1,11):
                        if sdist < idx/10.0:
                            row_dict['n_spray_%d' % idx] += 1

                for lab in ['Tmax_cumu', 'Tmin_cumu', 'PrecipTotal_cumu']:
                    row_dict[lab] = 0
                most_recent = 1000000
                most_recent_w = weather_features[0]
                for wfeat in weather_features:
                    wdate = wfeat['Date']
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
#                outfile.flush()
#                print('\n'.join(['%s: %s' % (k, row_dict[k]) for k in row_dict]))
#                exit(0)
    return

if __name__ == '__main__':
    feature_extraction()
