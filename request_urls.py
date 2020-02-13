#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 11 14:58:39 2020

@author: hamishgibbs
"""

import pandas as pd
import requests
import json
import os
from datetime import datetime
from datetime import timedelta

#%%
def daterange(date1, date2):
    for n in range(int ((date2 - date1).days)+1):
        yield date1 + timedelta(n)


def create_request_url(datatype, geocode, date, direction='move_out'):
    '''
    

    Parameters
    ----------
    datatype : TYPE
        DESCRIPTION.
    geocode : TYPE
        DESCRIPTION.
    date : TYPE
        DESCRIPTION.
    direction : TYPE, optional
        DESCRIPTION. The default is 'move_out'.

    Returns
    -------
    None.

    '''
    
    return('https://huiyan.baidu.com/migration/' + datatype + '.jsonp?dt=city&id=' + str(geocode) + '&type=' + direction + '&date=' + str(date))

def text_to_df(text, data_type):
    '''
    

    Parameters
    ----------
    text : TYPE
        DESCRIPTION.

    Returns
    -------
    None.

    '''
    
    first_parenth = text.find('(')

    text = text[first_parenth+1:]

    text = text.replace(')', '')
    
    json_data = json.loads(text)
    
    if data_type in ['historycurve', 'internalflowhistory']:    
        df = pd.DataFrame(list(json_data['data']['list'].items()))
        df.rename({0:'date', 1:'value'}, axis=1, inplace=True)

    if data_type in ['cityrank', 'provincerank']:
        df = pd.DataFrame(json_data['data']['list'])
                 
    return(df)

def make_filename(datatype, geocode, date, direction='move_out'):
    '''
    

    Parameters
    ----------
    datatype : TYPE
        DESCRIPTION.
    geocode : TYPE
        DESCRIPTION.
    date : TYPE
        DESCRIPTION.
    direction : TYPE, optional
        DESCRIPTION. The default is 'move_out'.

    Returns
    -------
    None.

    '''
    
    fn = '/' + str(geocode) + '_' + str(date) + '_' + direction + '_' + datatype + '.csv'
    
    return(fn)

def scrape(datatype, geocode, date, direction='move_out'):
    '''
    

    Returns
    -------
    None.

    '''
    url = create_request_url(datatype, geocode, date, direction)
    
    r = requests.get(url)
    try:
        data = text_to_df(r.text, data_type=datatype)
        
        fn = make_filename(datatype, geocode, date, direction)
        
        return(data, fn)
    
    except Exception as e:
        print(e)


#%%
geocodes = pd.read_csv('/Users/hamishgibbs/Documents/nCOV-2019/Web_Scraping/Unique_URLs/shp_pop.csv')
geocodes = list(geocodes['CNTY_CODE'])

start_date = datetime.strptime('2020-01-01', '%Y-%M-%d')
today = datetime.today()

dates = []
for dt in [dt for dt in daterange(start_date, today)]:
    
    day = str(dt.day)
    month = str(dt.month)
    year = str(dt.year)
    
    if(len(day) == 1):
        day = '0' + day
    else:
        day = day

    if(len(month) == 1):
        month = '0' + month
    else:
        month = month

    dates.append(year + month + day)

#%%
data_types = ['cityrank', 'provincerank', 'historycurve', 'internalflowhistory']

#%%
download_directory_all = '/Users/hamishgibbs/Documents/nCOV-2019/Web_Scraping/Scraped_Data'

for geocode in geocodes:
   
    try:
        current_download_directory = download_directory_all + '/' + str(geocode)
        os.mkdir(current_download_directory)
    except Exception as e:
        print(e, 'Cannot make download directory for ' + str(geocode))
        pass
    
    try:
        s = scrape('historycurve', geocode, dates[0], 'move_out')
        s[0].to_csv(current_download_directory + s[1])
    except Exception as e:
        print(e, 'No historycurve out for ' + str(geocode))
        pass        

    try:        
        s = scrape('historycurve', geocode, dates[0], 'move_in')
        s[0].to_csv(current_download_directory + s[1])
    except Exception as e:
        print(e, 'No historycurve in for ' + str(geocode))
        pass
    
    try:
        s = scrape('internalflowhistory', geocode, dates[0], 'move_out')
        s[0].to_csv(current_download_directory + s[1])
    except Exception as e:
        print(e, 'No internalflowhistory for ' + str(geocode))
        pass
    
    for date in dates:
        
        try:
            date_directory = current_download_directory + '/' + str(date)
            os.mkdir(date_directory)
        except Exception as e:
            print(e, 'Cannot make date directory for ' + str(geocode))
            pass

        try:    
            s = scrape('cityrank', geocode, date, 'move_out')
            s[0].to_csv(date_directory + s[1])
        except Exception as e:
            print(e, 'No cityrank out for ' + str(geocode))
            pass

        try:                
            s = scrape('provincerank', geocode, date, 'move_out')
            s[0].to_csv(date_directory + s[1])
        except Exception as e:
            print(e, 'No provincerank out for ' + str(geocode))
            pass
            
        try:                
            s = scrape('cityrank', geocode, date, 'move_in')
            s[0].to_csv(date_directory + s[1])
        except Exception as e:
            print(e, 'No cityrank in for ' + str(geocode))
            pass

        try:
            s = scrape('provincerank', geocode, date, 'move_in')
            s[0].to_csv(date_directory + s[1])
        except Exception as e:
            print(e, 'No provincerank in for ' + str(geocode))
            pass


#%%
#test
s = scrape('internalflowhistory', geocodes[0], dates[0], 'move_out')

#%%
url = create_request_url('internalflowhistory', geocodes[0], dates[0], 'move_out')
r = requests.get(url)
#%%
'''
can you get more cities than they have on the site?
start_city
'''

partial = [350300, 350500, 371200, 610400, 650100, 652300]








