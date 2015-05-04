#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 29 01:29:17 2015

@author: ddboline
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import pandas as pd
import numpy as np

SPECIES = ['CULEX ERRATICUS', 'CULEX PIPIENS', 'CULEX PIPIENS/RESTUANS',
           'CULEX RESTUANS', 'CULEX SALINARIUS', 'CULEX TARSALIS',
           'CULEX TERRITANS']

def clean_data(df):
    df['Species'] = df['Species'].map({k: n for (n, k) in enumerate(SPECIES)})
    n_null = (df['Species'].isnull()).sum()
    nan_species = np.random.random_integers(0, len(SPECIES)-1, size=(n_null,))
    if n_null > 0:
        df.loc[df['Species'].isnull(), 'Species'] = nan_species

    df['is_sat_trap'] = df['Trap'].apply(lambda x: len(x[4:]) > 0).astype(int)
    df['Trap'] = df['Trap'].apply(lambda x: x[1:4]).astype(int)

    df = df.drop(labels=['Date', 'Date.1', 'Address', 'Street',
                         'AddressNumberAndStreet', 'CodeSum', 'SnowFall',
                         'Water1', 'Station', 'Depth', 'wpBCFG', 'wpBLDU',
                         'wpBLSN', 'wpDU', 'wpFG+', 'wpFU', 'wpFZDZ',
                         'wpFZFG', 'wpFZRA', 'wpGR', 'wpGS', 'wpMIFG', 'wpPL',
                         'wpPRFG', 'wpSG', 'wpSN', 'wpSQ', 'wpTSSN', 'wpUP',
                         'wpVCFG', 'AddressAccuracy', 'WetBulb', 
                         'StnPressure'], axis=1)
    return df

def load_data(do_plots=False):
    train_df = pd.read_csv('train_full.csv.gz', compression='gzip',
                           low_memory=False)
    test_df = pd.read_csv('test_full.csv.gz', compression='gzip',
                          low_memory=False)
    submit_df = pd.read_csv('sampleSubmission.csv.gz', compression='gzip')

    train_df = clean_data(train_df)
    test_df = clean_data(test_df)

    print(submit_df.dtypes)

    for col in test_df.columns:
        if (test_df[col].isnull()).sum() > 0:
            print(col, test_df[col].dtype)
#    print(sorted(train_df['is_sat_trap'].unique()))
#    print(sorted(test_df['Species'].unique()))
    if do_plots:
        from plot_data import plot_data
        plot_data(train_df, prefix='train_html')
        plot_data(test_df, prefix='test_html')

    xtrain = train_df.drop(labels=['NumMosquitos', 'WnvPresent'],
                           axis=1).values
    ytrain = train_df[['NumMosquitos', 'WnvPresent']].values
    xtest = test_df.drop(labels=['Id'], axis=1).values
    ytest = submit_df
    return xtrain, ytrain, xtest, ytest

if __name__ == '__main__':
    xtrain, ytrain, xtest, ytest = load_data(do_plots=False)

    print([df.shape for df in (xtrain, ytrain, xtest, ytest)])
