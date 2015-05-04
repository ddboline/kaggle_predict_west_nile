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

SPECIES = ['CULEX ERRATICUS', 'CULEX PIPIENS', 'CULEX PIPIENS/RESTUANS',
           'CULEX RESTUANS', 'CULEX SALINARIUS', 'CULEX TARSALIS',
           'CULEX TERRITANS']

#TRAPS = ['T001', 'T002', 'T003', 'T004', 'T005', 'T006', 'T007', 'T008',
#         'T009', 'T011', 'T012', 'T013', 'T014', 'T015', 'T016', 'T017',
#         'T018', 'T019', 'T025', 'T027', 'T028', 'T030', 'T031', 'T033',
#         'T034', 'T035', 'T036', 'T037', 'T039', 'T040', 'T043', 'T044',
#         'T045', 'T046', 'T047', 'T048', 'T049', 'T050', 'T051', 'T054',
#         'T054C', 'T060', 'T061', 'T062', 'T063', 'T065', 'T066', 'T067',
#         'T069', 'T070', 'T071', 'T072', 'T073', 'T074', 'T075', 'T076',
#         'T077', 'T078', 'T079', 'T080', 'T081', 'T082', 'T083', 'T084',
#         'T085', 'T086', 'T088', 'T089', 'T090', 'T091', 'T092', 'T094',
#         'T094B', 'T095', 'T096', 'T097', 'T099', 'T100', 'T102', 'T103',
#         'T107', 'T114', 'T115', 'T128', 'T129', 'T135', 'T138', 'T141',
#         'T142', 'T143', 'T144', 'T145', 'T146', 'T147', 'T148', 'T149',
#         'T150', 'T151', 'T152', 'T153', 'T154', 'T155', 'T156', 'T157',
#         'T158', 'T159', 'T160', 'T161', 'T162', 'T200', 'T206', 'T209',
#         'T212', 'T215', 'T218', 'T219', 'T220', 'T221', 'T222', 'T223',
#         'T224', 'T225', 'T226', 'T227', 'T228', 'T229', 'T230', 'T231',
#         'T232', 'T233', 'T235', 'T236', 'T237', 'T238', 'T900', 'T903',
#         'T002A', 'T002B', 'T065A', 'T090A', 'T090B', 'T090C', 'T128A',
#         'T200A', 'T200B', 'T218A', 'T218B', 'T218C', 'T234']

def clean_data(df):
    df['Species'] = df['Species'].map({k: n for (n, k) in enumerate(SPECIES)})
    df['is_sat_trap'] = df['Trap'].apply(lambda x: len(x[4:]) > 0).astype(int)
    df['Trap'] = df['Trap'].apply(lambda x: x[1:4]).astype(int)

    df = df.drop(labels=['Date', 'Date.1', 'Address', 'Street',
                         'AddressNumberAndStreet', 'CodeSum', 'SnowFall',
                         'Water1', 'Station', 'Depth', 'wpBCFG', 'wpBLDU',
                         'wpBLSN', 'wpDU', 'wpFG+', 'wpFU', 'wpFZDZ',
                         'wpFZFG', 'wpFZRA', 'wpGR', 'wpGS', 'wpMIFG', 'wpPL',
                         'wpPRFG', 'wpSG', 'wpSN', 'wpSQ', 'wpTSSN', 'wpUP',
                         'wpVCFG', 'AddressAccuracy'], axis=1)
    return df

def load_data(do_plots=False):
    train_df = pd.read_csv('train_full.csv.gz', compression='gzip',
                           low_memory=False)
    test_df = pd.read_csv('test_full.csv.gz', compression='gzip',
                          low_memory=False)
    submit_df = pd.read_csv('sampleSubmission.csv.gz', compression='gzip')

    train_df = clean_data(train_df)
    test_df = clean_data(test_df)

#    print(train_df.columns)
#    print(test_df.columns)
#    print(submit_df.columns)

    print(train_df.dtypes)
    print(test_df.dtypes)
    print(submit_df.dtypes)

#    for col in test_df.columns:
#        if test_df[col].dtype == object:
#            print(col, test_df[col].dtype)
#    print(sorted(train_df['is_sat_trap'].unique()))
#    print(sorted(train_df['Trap'].unique()))
    if do_plots:
        from plot_data import plot_data
        plot_data(train_df, prefix='train_html')
        plot_data(test_df, prefix='test_html')

    xtrain = train_df.drop(labels=['NumMosquitos', 'WnvPresent'],
                           axis=1).values
    ytrain = train_df[['NumMosquitos', 'WnvPresent']].values
    xtest = test_df.values
    ytest = submit_df
    return xtrain, ytrain, xtest, ytest

if __name__ == '__main__':
    xtrain, ytrain, xtest, ytest = load_data(do_plots=False)

    print([df.shape for df in (xtrain, ytrain, xtest, ytest)])
