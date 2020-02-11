#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 10 09:49:24 2020

@author: hamishgibbs
"""

import json
from geojson import Point, Feature, FeatureCollection, dump
#%%

path = '/Users/hamishgibbs/Documents/nCOV-2019/Web_Scraping/Singapore_Data/'
in_fn = 'singapore_data.json'
out_fn = 'singapore_data.geojson'

raw = open(path + in_fn).read()

#for UTF-8 encoded chinese characters:


#else:
json_data = json.loads(raw)

features = []
for i, feature in enumerate(json_data['data']):
    
    try:
        point = Point((float(feature['lng']), float(feature['lat'])))
        feature = Feature(geometry=point, properties=feature)
        features.append(feature)
    except Exception as e:
        print(e)

#%%
with open(path + out_fn, 'w') as f:
    dump(FeatureCollection(features), f)



