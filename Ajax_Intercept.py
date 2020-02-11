#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 10 11:47:09 2020

@author: hamishgibbs
"""

from selenium import webdriver
import time
import bs4 as BeautifulSoup
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options  
import pandas as pd
import os
import datetime
from multiprocessing import Pool
from itertools import compress
import numpy as np
from browsermobproxy import Server
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import json
from haralyzer import HarParser, HarPage


#%%

caps = DesiredCapabilities.CHROME
caps['loggingPrefs'] = {'performance': 'ALL'}
driver = webdriver.Chrome(desired_capabilities=caps)
driver.get('https://stackoverflow.com/questions/52633697/selenium-python-how-to-capture-network-traffics-response')

try:
    browser_log = driver.get_log('browser') 
    driver.quit()
except Exception as e:
    print(e)
    driver.quit()
#%%
def process_browser_log_entry(entry):
    response = json.loads(entry['message'])['message']
    return response

#%%
    
'''
try to save HAR file - select all options on the site, then save HAR file, parse massive json response 

write everything into a bot class

'''
server = Server("/Users/hamishgibbs/Documents/nCOV-2019/Web_Scraping/Baidu_Web_Scraping/browsermob-proxy-2.1.4/bin/browsermob-proxy",  options={'port': 8090})    


server.start()
proxy = server.create_proxy()

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--proxy-server={}".format(proxy.proxy))
driver = webdriver.Chrome(options=chrome_options)

proxy.new_har("myhar")
with open('/Users/hamishgibbs/Documents/nCOV-2019/Web_Scraping/Request_Intercept/myhar.har', 'w') as har_file:
    json.dump(proxy.har, har_file)
    
driver.get('https://sgwuhan.xose.net/')

time.sleep(10)

ok_btn = driver.find_element_by_xpath('//*[@id="okBtn"]')
ok_btn.click()
time.sleep(5)

server.stop()

driver.quit()

#%%
executable_path = '/Users/hamishgibbs/Documents/nCOV-2019/Web_Scraping/Baidu_Web_Scraping/chromedriver'

#initialize web driver
driver = webdriver.Chrome(executable_path = executable_path)

url = 'https://qianxi.baidu.com/'

#let page load
driver.get(url)
time.sleep(10)


#define buttons that are constant no matter the layout of the site
city_name_drop_down = driver.find_element_by_xpath('//*[@id="content"]/div/div[2]/div[1]/div/div')
date_drop_down = driver.find_element_by_xpath('//*[@id="content"]/div/div[2]/div[2]/div/div/div')
incoming_button = driver.find_element_by_xpath('//*[@id="content"]/div/div[2]/div[3]/div/div[1]')
outgoing_button = driver.find_element_by_xpath('//*[@id="content"]/div/div[2]/div[3]/div/div[2]')

for i in range(0, len(city_name_xpaths)):
    city_xpath = city_name_xpaths[i]
    
    city_name_drop_down.click()
    time.sleep(0.5)
    
    
    
    try:
        
        city_button = driver.find_element_by_xpath(city_xpath)
        city_button.click()
        
        outgoing_button.click()
        time.sleep(0.5)
        incoming_button.click()
        time.sleep(0.5)

    
        for a in range(0, len(date_name_xpaths), 1):
            
            incoming_button.click()
            
            date_xpath = date_name_xpaths[a]
            
            date_drop_down.click()
            time.sleep(0.5)
            
            date_button = driver.find_element_by_xpath(date_xpath)
            
            date_button_soup = BeautifulSoup.BeautifulSoup(date_button.get_attribute('innerHTML'), 'html.parser')

            date_button_text = date_button_soup.getText().replace('-', '_')
            
            date_button.click()
            short_wait()
            
            city_panel_button = driver.find_element_by_xpath('//*[@id="content"]/div/div[4]/div[1]/div/div[1]')
            province_panel_button = driver.find_element_by_xpath('//*[@id="content"]/div/div[4]/div[1]/div/div[2]')
            
            #get city data
            
            province_panel_button.click()
            time.sleep(0.5)

            #get province data
            
            outgoing_button.click()
            time.sleep(0.5)
            
            #get province data
            
            province_panel_button.click()
            time.sleep(0.5)
            
            #get city data

            city_panel_button.click()
            time.sleep(0.5)

                    
    except Exception as e:
        
        city_name_drop_down.click()
        
        print(e)
    
#%%
'''
Parse .har file
'''
with open('/Users/hamishgibbs/Documents/nCOV-2019/Web_Scraping/Request_Intercept/qianxi.baidu.com.har', 'r') as f:
    har_page = json.loads(f.read())

#%%
hot_city_index = []
line_data_index = []
city_data_index = []
prov_data_index = []

for i, log_entry in enumerate(har_page['log']['entries']):
    
    #get hot city
    #get line data
    #get panel data
    
    #search for hot_city
    if str(log_entry).find('cen&b') > 0:
        hot_city_index.append(i)

    #line_data
    if str(log_entry).find('historycurve') > 0:
        line_data_index.append(i)
    
    #panel_data
    if str(log_entry).find('cityrank') > 0:
        city_data_index.append(i)
    
    if str(log_entry).find('provincerank') > 0:
        prov_data_index.append(i)
        print(len(str(log_entry)))
        
#%%
        
'''
to scrape panel data
'''
        
panel_data = har_page['log']['entries'][panel_data_index[0]]['response']['content']['text']
first_parenth = panel_data.find('(')
panel_data = panel_data[first_parenth+1:]
panel_data = panel_data.replace(')', '')
panel_data=json.loads(panel_data)['data']['list']
panel_df = pd.DataFrame(panel_data)
print(panel_df)
#%%
'''
to scrape line data
'''     
line_data = har_page['log']['entries'][line_data_index[0]]['response']['content']['text']
first_parenth = line_data.find('(')
line_data = line_data[first_parenth+1:]
line_data = line_data.replace(')', '')
line_data=json.loads(line_data)['data']['list']
line_df = pd.DataFrame(list(line_data.items()))
print(line_df)
#%%
'''
to scrape hot city datan - looks like you get hot city info before each item
'''
hc_data = har_page['log']['entries'][hot_city_index[0]]['response']['content']['text']
first_parenth = hc_data.find('(')
hc_data = hc_data[first_parenth+1:]
hc_data = hc_data.replace(')', '')
hc_data=json.loads(hc_data)['current_city']
print(hc_data)


#%%
for i, log_entry in enumerate(har_page['log']['entries']):
    
    fn = '/Users/hamishgibbs/Documents/nCOV-2019/Web_Scraping/Request_Intercept/data_download_test/' + str(i) + '.csv' 
    
    #panel_data
    try:
        if str(log_entry).find('cityrank') > 0:
            panel_data = har_page['log']['entries'][i]['response']['content']['text']
            first_parenth = panel_data.find('(')
            panel_data = panel_data[first_parenth+1:]
            panel_data = panel_data.replace(')', '')
            panel_data=json.loads(panel_data)['data']['list']
            panel_df = pd.DataFrame(panel_data)
            panel_df.to_csv(fn)
    except Exception as e:
        print('city')
        print(har_page['log']['entries'][i]['response']['content']['text'])
        print(e)
    
    #panel_data
    try:
        if str(log_entry).find('provincerank') > 0:
            panel_data = har_page['log']['entries'][i]['response']['content']['text']
            first_parenth = panel_data.find('(')
            panel_data = panel_data[first_parenth+1:]
            panel_data = panel_data.replace(')', '')
            panel_data=json.loads(panel_data)['data']['list']
            panel_df = pd.DataFrame(panel_data)
            panel_df.to_csv(fn)
    except Exception as e:
        print('province')
        print(har_page['log']['entries'][i]['response']['content']['text'])
        print(e)
        
    #line_data
    try:
        if str(log_entry).find('historycurve') > 0:
            line_data = har_page['log']['entries'][i]['response']['content']['text']
            first_parenth = line_data.find('(')
            line_data = line_data[first_parenth+1:]
            line_data = line_data.replace(')', '')
            line_data=json.loads(line_data)['data']['list']
            line_df = pd.DataFrame(list(line_data.items()))
            line_df.to_csv(fn)
    except Exception as e:
        print('line')
        print(e)
    
    #search for hot_city
    try:
        #panel_data
        if str(log_entry).find('cen&b') > 0:
            hc_data = har_page['log']['entries'][i]['response']['content']['text']
            first_parenth = hc_data.find('(')
            hc_data = hc_data[first_parenth+1:]
            hc_data = hc_data.replace(')', '')
            hc_data=json.loads(hc_data)['current_city']
            hc_df = pd.DataFrame(list(hc_data.items()))
            hc_df.to_csv(fn)
    except Exception as e:
        print('hc')
        print(e)      
        
    #%%
def text_to_json(text):
    first_parenth = text.find('(')
    text = text[first_parenth+1:]
    text = text.replace(')', '')
    json_data=json.loads(text)['data']['list']
    
    return(json_data)
#%%

'''

then:
work sequentially- when encounter a hot city - make that data the new data - then parse panels and liens as approppriate
-looks like you get a hot city df before each data file? - this would make things very easy 
'''    

#%%        
        
    #to_get_panel data
    har_page['log']['entries'][panel_data_index[0]]['response']['content']['text']
#%%
        
        
#%%

#for every city - name dropdown click

#for lines
#incoming 
#outgoing

#for every date- 
    #click incoming_button
        #city
        #province
    #click outgoing button
        #city
        #province

'''
har structure - 
hot city
line data in 
line data out
panel in:
    city
    province
panel out:
    city
    province
next city
'''

#haralyzer
#idea - 
#click through every option, download one har file manually with chrome
#use python to parse the har - for active city/ lines data etc.