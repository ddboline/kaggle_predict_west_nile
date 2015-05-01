#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 29 01:29:17 2015

@author: ddboline
"""
import pandas as pd

def load_data():
    train_df = pd.read_csv('train.csv.gz', compression='gzip')
    test_df = pd.read_csv('test.csv.gz', compression='gzip')
    submit_df = pd.read_csv('sampleSubmission.csv.gz', compression='gzip')
    
    
    print train_df.columns
    print test_df.columns
    
    print train_df.dtypes
    print test_df.dtypes
    return

if __name__ == '__main__':
    load_data()
