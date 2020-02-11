#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 10 13:40:17 2020

@author: hamishgibbs
"""

import json
import geopandas as gpd
import geocoder
import geopy
import shapely
import time

#%%
sing = gpd.read_file("/Users/hamishgibbs/Documents/nCOV-2019/Web_Scraping/Singapore_Data/singapore_data.geojson")
print(list(sing))
#%%
sing['case_id'] = range(1, len(sing['stayed'])+1)
#%%
stayed_data = []
locator = geopy.Nominatim(user_agent="myGeocoder", timeout=30)
prohib = ['Singapore']

for a, case_num in enumerate(sing['case_id']):
    
    stayed = sing.loc[a, 'stayed']
    
    try:
        if stayed != '' and stayed not in prohib:
            location = locator.geocode(stayed + ", Singapore")

        stayed_data.append({'caseNo':case_num, 'text_orig':stayed, 'point':shapely.geometry.Point((location.longitude, location.latitude)), 'type':'stayed'})
        print(stayed)
    except Exception as e:
        print(e)
        continue
    
#%%
print(stayed_data)
#%%

visited_data = []

prohib = ['China', 'Wuhan', 'Malaysia', 'Singapore', 'GP Clinic', 'No info by MOH', 'Jewel']
locator = geopy.Nominatim(user_agent="myGeocoder", timeout=30)

for a, case_num in enumerate(sing['case_id']):
    
    visited = sing.loc[a, 'visited']
    visited = visited.split(', ')
    
    for text in visited:
        if text != '' and text not in prohib:
            print(text)
            location = locator.geocode(text + ", Singapore")
            
            try:
                visited_data.append({'caseNo':case_num, 'text_orig':text, 'point':shapely.geometry.Point((location.longitude, location.latitude)), 'type':'visited'})
                
            except Exception as e:
                print(e)
                continue
        
    
#%%
print(visited_data)
#shiny quick plot all_confirmed_prf

#%%
visited_gpd = gpd.GeoDataFrame(pd.DataFrame(visited_data), geometry = 'point')
stayed_gpd = gpd.GeoDataFrame(pd.DataFrame(stayed_data), geometry = 'point')
all_gpd = pd.merge(visited_gpd, stayed_gpd, on=list(visited_gpd), how='outer')

#%%
all_gpd.to_file("/Users/hamishgibbs/Documents/nCOV-2019/Web_Scraping/Singapore_Data/singapore_additional_geodata.geojson", driver='GeoJSON')
sing.to_file("/Users/hamishgibbs/Documents/nCOV-2019/Web_Scraping/Singapore_Data/singapore_data_id.geojson", driver='GeoJSON')