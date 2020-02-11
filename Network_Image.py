#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 11 10:54:50 2020

@author: hamishgibbs
"""

import rpy2.robjects as robjects
from rpy2.robjects import pandas2ri
pandas2ri.activate()

readRDS = robjects.r['readRDS']
df = readRDS('/Users/hamishgibbs/Dropbox/nCov-2019/data_sources/mobility_data/china_prf_connectivity.rds')
df = pandas2ri.ri2py(df)
#%%




















