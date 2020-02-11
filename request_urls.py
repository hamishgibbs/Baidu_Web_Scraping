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

#%%
geocodes = pd.read_csv('/Users/hamishgibbs/Documents/nCOV-2019/Web_Scraping/Unique_URLs/shp_pop.csv')
geocodes = list(geocodes['CNTY_CODE'])
dates = [20200209, 20200210]

#%%
data_types = ['cityrank', 'provincerank', 'historycurve']

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
    
    return('https://huiyan.baidu.com/migration/' + datatype + '.jsonp?dt=province&id=' + str(geocode) + '&type=' + direction + '&date=' + str(date))

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
    
    if data_type == 'historycurve':    
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

#%%
class Scraper:
    
    def __init__(self, datatype, geocode, date, direction='move_out'):
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
        
        self.datatype = datatype
        self.geocode = geocode
        self.date = date
        self.direction = direction
        self.url = create_request_url(self.datatype, self.geocode, self.date, self.direction)
    
    def scrape(self):
        '''
        

        Returns
        -------
        None.

        '''
        
        r = requests.get(self.url)
        try:
            data = text_to_df(r.text, data_type=self.datatype)
            
            fn = make_filename(self.datatype, self.geocode, self.date, self.direction)
        except Exception as e:
            print(e)
    
class ScrapedData:
    def __init__(self, data, fn):
        '''
        

        Parameters
        ----------
        data : TYPE
            DESCRIPTION.
        fn : TYPE
            DESCRIPTION.

        Returns
        -------
        None.

        '''
        
        self.data = data
        self.fn = fn
        
#%%
url = create_request_url('historycurve', geocodes[0], dates[0], 'move_in')
r = requests.get(url)
#%%
download_directory_all = '/Users/hamishgibbs/Documents/nCOV-2019/Web_Scraping/Scraped_Data_URLS'

for geocode in geocodes[71:len(geocodes)]:
    
    current_download_directory = download_directory_all + '/' + str(geocode)
    os.mkdir(current_download_directory)
    
    try:
        s = Scraper('historycurve', geocode, dates[0], 'move_out')
        s_data = s.scrape()
        s_data.data.to_csv(current_download_directory + s_data.fn)
        
        s = Scraper('historycurve', geocode, dates[0], 'move_in')
        s_data = s.scrape()
        s_data.data.to_csv(current_download_directory + s_data.fn)
        
        
        for date in dates:
            
            date_directory = current_download_directory + '/' + str(date)
            os.mkdir(date_directory)
            
            s = Scraper('cityrank', geocode, date, 'move_out')
            s_data = s.scrape()
            s_data.data.to_csv(date_directory + s_data.fn)
            
            s = Scraper('provincerank', geocode, date, 'move_out')
            s_data = s.scrape()
            s_data.data.to_csv(date_directory + s_data.fn)
            
            s = Scraper('cityrank', geocode, date, 'move_in')
            s_data = s.scrape()
            s_data.data.to_csv(date_directory + s_data.fn)
            
            s = Scraper('provincerank', geocode, date, 'move_in')
            s_data = s.scrape()
            s_data.data.to_csv(date_directory + s_data.fn)
    except Exception as e:
        print(e)

'''
can you get more cities than they have on the site?
start_city
'''














