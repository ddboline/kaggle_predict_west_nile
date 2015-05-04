#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Created on Mon May  4 12:55:05 2015

@author: ddboline
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import numpy as np

from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestClassifier,\
                             GradientBoostingRegressor, \
                             GradientBoostingClassifier
from sklearn.cross_validation import train_test_split
#from sklearn.metrics.roc_curve
from sklearn.metrics import roc_auc_score, mean_squared_error
from sklearn.grid_search import GridSearchCV

from load_data import load_data

def transform_to_log(y):
    return np.log1p(y)

def transform_from_log(ly):
    return np.round(np.expm1(ly)).astype(int)

def scorer(estimator, X, y):
    ypred = estimator.predict(X)
    return 1.0/mean_squared_error(ypred, y)

def train_nmosq_model(model, xtrain, ytrain, do_grid_search=False):
    xTrain, xTest, yTrain, yTest = train_test_split(xtrain, 
                                                    ytrain[:,0],
                                                    test_size=0.5)
    n_est = [10, 20]
    m_dep = [2, 3, 4, 5, 6, 7, 10]

    if do_grid_search:
        model = GridSearchCV(estimator=model,
                                    param_grid=dict(n_estimators=n_est, 
                                                    max_depth=m_dep),
                                    scoring=scorer,
                                    n_jobs=-1, verbose=1)
    model.fit(xTrain, yTrain)
    print(model.score(xTest, yTest))
    if hasattr(model, 'best_params_'):
        print(model.best_params_)

def train_has_wnv_model(model, xtrain, ytrain):
    xTrain, xTest, yTrain, yTest = train_test_split(xtrain, 
                                                    ytrain[:,1],
                                                    test_size=0.5)
    model.fit(xTrain, yTrain)
    ypred = model.predict_proba(xTest)
    print(roc_auc_score(yTest, ypred[:, 1]))
    return

def prepare_submission(model, xtest, ytest):
    ypred = model.predict_proba(xtest)
    ytest.loc[:, 'WnvPresent'] = ypred[:, 1]
    ytest['Id'] = ytest['Id'].astype(int)
    ytest.to_csv('submission.csv', index=False)

def my_model():
    xtrain, ytrain, xtest, ytest = load_data()
        
#    ytrain = transform_to_log(ytrain)
#    
#    model = GradientBoostingRegressor(loss='ls', verbose=1, max_depth=10, 
#                                        n_estimators=20)
#    train_nmosq_model(model, xtrain, ytrain)
    
    model = GradientBoostingClassifier(verbose=1)

    train_has_wnv_model(model, xtrain ,ytrain)
    
    prepare_submission(model, xtest, ytest)
    
    return

if __name__ == '__main__':
    my_model()