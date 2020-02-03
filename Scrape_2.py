#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 30 22:23:41 2020

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

#%%
'''
Script Overview:
    
Web scraping of Baidu movement interactive web map

Outputs:

Line chart data outgoing/incoming

for every date:
Top destination/arrival details city & provincial

'''

#helper functions to wait different periods
def very_short_wait():
    time.sleep(0.0000001)
    
def short_wait():
    time.sleep(1.5)
    
def long_wait():
    time.sleep(10)

#function to return xpath of element identified in beautiful soup
def xpath_soup(element):
    
    components = []
    child = element if element.name else element.parent
    for parent in child.parents:  
        siblings = parent.find_all(child.name, recursive=False)
        components.append(
            child.name if 1 == len(siblings) else '%s[%d]' % (
                child.name,
                next(i for i, s in enumerate(siblings, 1) if s is child)
                )
            )
        child = parent
    components.reverse()
    
    return '/%s' % '/'.join(components)

#function to scrape the data of the active side panel
def scrape_panel_data(driver):
    panel_final_data = []
    
    full_page_soup = BeautifulSoup.BeautifulSoup(driver.page_source, 'html.parser')
    panel_container = full_page_soup.find_all('div', attrs={'class': 'mgs-list'})
    
    
    panel_data = panel_container[0].find_all('tr')
    
    
    for item in panel_data:
            
        item_data = item.find_all('td')
        
        if len(item_data) == 3:
            panel_final_data.append({'rank':item_data[0].getText(), 'city':item_data[1].getText(), 'percent':item_data[2].getText()})
    
    panel_df = pd.DataFrame(panel_final_data) 
    
    return(panel_df)

def scrape_line_graph(driver):
    line_chart = driver.find_element_by_xpath('//*[@id="content"]/div/div[6]')

    line_chart_data = []
    #chart data only appears one value at a time - hover over every item in the chart and get its value
    
    #hover over chart starting from left to 700 pixels R (steps of 20 px)
    #This offset is in relation to default chrome window - changing window/monitor size will result in incorrect data
    for xoffset in range(0, 700, 7):
        hover = ActionChains(driver).move_to_element_with_offset(line_chart, xoffset=xoffset, yoffset=150)
        hover.perform()
        time.sleep(0.001)
        
        #get the container holding the current data of the hovered point
        current_line_data_container = driver.find_element_by_xpath('//*[@id="content"]/div/div[6]/div[1]/div[2]')
    
        #extract value and date from hovered point
        line_data_soup = BeautifulSoup.BeautifulSoup(current_line_data_container.get_attribute('outerHTML'), 'html.parser')
    
        line_value_soup = line_data_soup.find_all('div')
    
        for line in line_value_soup:
            
            #try catch for any hovered points without data
            try:
                line = line.getText()
                
                text_location_2020 = line.find('今年迁徙规模指数: ')
                text_location_2019 = line.find('去年迁徙规模指数: ')
                       
                #see if there is a 2020 data value:
                if text_location_2020 > 0:
                    
                    #if there is a 2020 value: extract date, 2020 value and 2019 value
                    line_date = line[: text_location_2020]
                    data_2020 = line[text_location_2020:text_location_2019]
                    data_2019 = line[text_location_2019:]
                    data_2020_value = data_2020.split(': ')[1]
                    data_2019_value = data_2019.split(': ')[1]
                    
                else:
                    #if there is no 2020 value, extract date and 2019 value
                    line_date = line[: text_location_2019]
                    data_2019 = line[text_location_2019:]
                    data_2020_value = 'NULL'
                    data_2019_value = data_2019.split(': ')[1]
            except:
                continue
    
            line_chart_data.append({'date':line_date, '2019':data_2019_value, '2020':data_2020_value}) 
    
    #reconcile numeric dates with chinese dates (recorded)
    td = (datetime.date.today() + datetime.timedelta(days=15)) - datetime.date(2020, 1, 1)
    
    line_date_labels = []
    
    #correctly format numeric dates - this will error with leap year?
    for i in range(td.days + 1):
        line_date_label = str(datetime.date(2020, 1, 1) + datetime.timedelta(days=i))
        line_date_label = line_date_label[5:]
        line_date_label = line_date_label.replace('-', '_')
        line_date_labels.append(line_date_label)

    #try to create dataframe from line date - if there is no data - return none
    try:
        line_df = pd.DataFrame(line_chart_data)
        line_df.drop_duplicates(inplace=True)
        line_df.reset_index(inplace=True)
        
        #correct an error where the last selected record becomes the first if the function used in succession 
        if line_df.loc[0, '2020'] == 'NULL':
            line_df = line_df.drop(0, axis=0)
        
        line_df['date'] = line_date_labels
            
        line_df.reset_index(inplace=True)
        
        line_df = line_df.filter(['date', '2019', '2020'])
        
        return(line_df)
    except Exception as e: 
        print(e)
        return(None)
    
def scrape_both_line_charts(i):
    
    url = 'https://qianxi.baidu.com/'
    
    city_xpath = city_name_xpaths[i]
           
    #initialize web driver
    driver = webdriver.Chrome(executable_path = executable_path)
    
    #let page load
    driver.get(url)
    short_wait()
    
    #define buttons that are constant no matter the layout of the site
    city_name_drop_down = driver.find_element_by_xpath('//*[@id="content"]/div/div[2]/div[1]/div/div')
    incoming_button = driver.find_element_by_xpath('//*[@id="content"]/div/div[2]/div[3]/div/div[1]')
    outgoing_button = driver.find_element_by_xpath('//*[@id="content"]/div/div[2]/div[3]/div/div[2]')

    
    #click on city dropdown
    city_name_drop_down.click()
    short_wait()
        
    try:
        city_button = driver.find_element_by_xpath(city_xpath)
        city_button.click()
        short_wait()
        
        #make a directory with the city name
        current_download_directory = download_directory_all + city_names[i]
        os.mkdir(current_download_directory)
        
        outgoing_button.click()
        
        #line charts do not change for different date values
        #scrape outgoing line chart
        line_df = scrape_line_graph(driver)
        write_csv(line_df, current_download_directory + '/' + city_names[i] + '_line_outgoing.csv')
        
        incoming_button.click()
        short_wait()
        #scrape incoming line chart
        line_df = scrape_line_graph(driver)
        write_csv(line_df, current_download_directory + '/' + city_names[i] + '_line_incoming.csv')
        
        short_wait()
        
        driver.quit()

    except Exception as e: 
        print(e)
        
        driver.quit()        
    
def write_csv(df, file_name):
    if df is not None:
        df.to_csv(file_name)
#%%
'''
Initial website parse to extract static elements
'''

#remember to install correct version of chrome driver executable (open chrome and inspect version)
executable_path = '/Users/hamishgibbs/Documents/nCOV-2019/Web_Scraping/Baidu_Web_Scraping/chromedriver'

#url to be scraped
url = 'https://qianxi.baidu.com/'

#initialize web driver - not using a headless web browser to continue to monitor progress
driver = webdriver.Chrome(executable_path = executable_path)

#let page load
driver.get(url)
short_wait()

#extract all html of page
soup = BeautifulSoup.BeautifulSoup(driver.page_source, 'html.parser')

driver.quit()


#%%
#get text and xpath of city name and dates stored in main dropdown lists
city_name_elements = soup.find_all('a', attrs={'class': 'sel_city_name'})
city_name_xpaths = [xpath_soup(i) for i in city_name_elements]
city_names = [i.getText() for i in city_name_elements]

date_name_container = soup.find_all('ul', attrs={'class': 'hui-option-list'})
date_name_elements = date_name_container[0].find_all('li')
date_name_xpaths = [xpath_soup(i) for i in date_name_elements]
date_names = [i.getText() for i in date_name_elements]
date_names_sub = [i.replace('-', '_') for i in date_names]
#%%
'''
Using data from initial scrape, conduct full, systematic web scrape

Proposed changes to workflow 
    - scrape every line chart for every city (return and scrape every panel for every date)
    - continue with headless driver
    - run multiple windows in parallel (10) - while
    
    - avoid tru multiprocessing by batching into 10 RAM is not the issue but time.sleep()

'''

download_directory_all = '/Users/hamishgibbs/Documents/nCOV-2019/Web_Scraping/Scraped_Data/'

open_chrome_windows = 0

for i in range(0, len(city_name_xpaths) + 1, 1):
    scrape_both_line_charts(i)
#%%
with Pool(3) as p:
    p.map(scrape_both_line_charts, list(range(0, len(city_name_xpaths) + 1, 1)))
#%%
    
def scrape_panels_for_select_dates(i):
    
    city_xpath = city_name_xpaths[i]
           
    #initialize web driver
    driver = webdriver.Chrome(executable_path = executable_path)
    
    #let page load
    driver.get(url)
    short_wait()
    
    #define buttons that are constant no matter the layout of the site
    city_name_drop_down = driver.find_element_by_xpath('//*[@id="content"]/div/div[2]/div[1]/div/div')
    date_drop_down = driver.find_element_by_xpath('//*[@id="content"]/div/div[2]/div[2]/div/div/div')
    incoming_button = driver.find_element_by_xpath('//*[@id="content"]/div/div[2]/div[3]/div/div[1]')
    outgoing_button = driver.find_element_by_xpath('//*[@id="content"]/div/div[2]/div[3]/div/div[2]')
    
    #click on city dropdown
    city_name_drop_down.click()
    short_wait()
    
    #select four dates from now to 1/1 to now for scraping panels
    select_date_button_index = []
    
    for date_index in range(int((len(date_names)+1)/4), len(date_names)+1, int((len(date_names)+1)/4)):
        select_date_button_index.append(date_index)
    
    select_date_buttons = [date_name_xpaths[index] for index in select_date_button_index]
    
    city_button = driver.find_element_by_xpath(city_xpath)
    city_button.click()
    short_wait()
    
    #load data into existing directories (where lines have already been scraped)
    current_download_directory = download_directory_all + city_names[i]
    
    try:
        outgoing_button.click()
        
        for a, date_xpath in enumerate(select_date_buttons):
            date_drop_down.click()
            short_wait()
            
            #make a directory for each date
            current_date_download_directory = current_download_directory + '/' + date_names_sub[a]
            os.mkdir(current_date_download_directory)
            
            #click on new date
            date_button = driver.find_element_by_xpath(date_xpath)
            date_button.click()
            short_wait()
            
            #parse outgoing cities panel
            panel_df = scrape_panel_data(driver)
            panel_df.to_csv(current_date_download_directory + '/' + city_names[i] + '_' + date_names_sub[a] + '_cities_outgoing.csv')
            
            #activate provinces panel
            province_panel_button.click()
            short_wait()
            
            #parse outgoing provinces panel
            panel_df = scrape_panel_data(driver)
            panel_df.to_csv(current_date_download_directory + '/' + city_names[i] + '_' + date_names_sub[a] + '_provinces_outgoing.csv')
            
            #reset cities panel
            city_panel_button.click()
            short_wait()
            
            #change to incoming trips
            incoming_button.click()
            short_wait()
            
            #parse incoming cities data
            panel_df = scrape_panel_data(driver)
            panel_df.to_csv(current_date_download_directory + '/' + city_names[i] + '_' + date_names_sub[a] + '_cities_incoming.csv')
             
            #activate provinces panel
            province_panel_button.click()
            short_wait()
            
            #parse incoming provinces
            panel_df = scrape_panel_data(driver)
            panel_df.to_csv(current_date_download_directory + '/' + city_names[i] + '_' + date_names_sub[a] + '_provinces_incoming.csv')
            
            #reset to cities panel
            city_panel_button.click()
            short_wait()
            
            #reset to outgoing for next date
            outgoing_button.click()
            short_wait()
        
        driver.quit()

    except Exception as e: 
        print(e)
        
        driver.quit()
            

    
    
#%%

#here: sort out error handling to ensure that every city name is clicked
#for every city hyperlink:

error_occurred_last_time = False

for i in range(71, len(city_name_xpaths) + 1, 1):
    
    city_xpath = city_name_xpaths[i]
    
    #initialize web driver
    driver = webdriver.Chrome(executable_path = executable_path)
    
    #let page load
    driver.get(url)
    short_wait()
    
    #click on guidance mask to access page elements (guidance mask covers the new page when it is loaded)
    #guidance_mask = driver.find_element_by_xpath('//*[@id="content"]/div/div[7]')
    #guidance_mask.click()
    #short_wait()
    
    #define buttons that are constant no matter the layout of the site
    city_name_drop_down = driver.find_element_by_xpath('//*[@id="content"]/div/div[2]/div[1]/div/div')
    date_drop_down = driver.find_element_by_xpath('//*[@id="content"]/div/div[2]/div[2]/div/div/div')
    outgoing_button = driver.find_element_by_xpath('//*[@id="content"]/div/div[2]/div[3]/div/div[1]')
    incoming_button = driver.find_element_by_xpath('//*[@id="content"]/div/div[2]/div[3]/div/div[2]')
    
    
    #click on city dropdown
    if error_occurred_last_time == False:
        city_name_drop_down.click()
        short_wait()    
    
    #create new folder to store data for this city
    
    #try to click on each city name element (some links do not work)
    try:
        city_button = driver.find_element_by_xpath(city_xpath)
        city_button.click()
        short_wait()
        
        #get constant panel buttons
        city_panel_button = driver.find_element_by_xpath('//*[@id="content"]/div/div[5]/div[1]/div/div[1]')
        province_panel_button = driver.find_element_by_xpath('//*[@id="content"]/div/div[5]/div[1]/div/div[2]')
        
        #make a directory with the city name
        current_download_directory = download_directory_all + city_names[i]
        os.mkdir(current_download_directory)
        
        #line charts do not change for different date values
        #scrape outgoing line chart
        line_df = scrape_line_graph(driver)
        line_df.to_csv(current_download_directory + '/' + city_names[i] + '_line_outgoing.csv')
        
        incoming_button.click()
        short_wait()
        #scrape incoming line chart
        line_df = scrape_line_graph(driver)
        line_df.to_csv(current_download_directory + '/' + city_names[i] + '_line_incoming.csv')
        
        #click on outgoing
        outgoing_button.click()
        short_wait()
        
        #for each date:
        for a, date_xpath in enumerate(date_name_xpaths):
            date_drop_down.click()
            short_wait()
            
            #make a directory for each date
            current_date_download_directory = current_download_directory + '/' + date_names_sub[a]
            os.mkdir(current_date_download_directory)
            
            #click on new date
            date_button = driver.find_element_by_xpath(date_xpath)
            date_button.click()
            short_wait()
            
            #parse outgoing cities panel
            panel_df = scrape_panel_data(driver)
            panel_df.to_csv(current_date_download_directory + '/' + city_names[i] + '_' + date_names_sub[a] + '_cities_outgoing.csv')
            
            #activate provinces panel
            province_panel_button.click()
            short_wait()
            
            #parse outgoing provinces panel
            panel_df = scrape_panel_data(driver)
            panel_df.to_csv(current_date_download_directory + '/' + city_names[i] + '_' + date_names_sub[a] + '_provinces_outgoing.csv')
            
            #reset cities panel
            city_panel_button.click()
            short_wait()
            
            #change to incoming trips
            incoming_button.click()
            short_wait()
            
            #parse incoming cities data
            panel_df = scrape_panel_data(driver)
            panel_df.to_csv(current_date_download_directory + '/' + city_names[i] + '_' + date_names_sub[a] + '_cities_incoming.csv')
             
            #activate provinces panel
            province_panel_button.click()
            short_wait()
            
            #parse incoming provinces
            panel_df = scrape_panel_data(driver)
            panel_df.to_csv(current_date_download_directory + '/' + city_names[i] + '_' + date_names_sub[a] + '_provinces_incoming.csv')
            
            #reset to cities panel
            city_panel_button.click()
            short_wait()
            
            #reset to outgoing for next date
            outgoing_button.click()
            short_wait()
            
        error_occurred_last_time = False
            
    except Exception as e: 
        print(e)

        error_occurred_last_time = True
        continue

    driver.quit()

        
#%%
#update line scrape
city_xpath = city_name_xpaths[71]

#initialize web driver
driver = webdriver.Chrome(executable_path = executable_path)

#let page load
driver.get(url)
short_wait()

#define buttons that are constant no matter the layout of the site
city_name_drop_down = driver.find_element_by_xpath('//*[@id="content"]/div/div[2]/div[1]/div/div')
date_drop_down = driver.find_element_by_xpath('//*[@id="content"]/div/div[2]/div[2]/div/div/div')
outgoing_button = driver.find_element_by_xpath('//*[@id="content"]/div/div[2]/div[3]/div/div[1]')
incoming_button = driver.find_element_by_xpath('//*[@id="content"]/div/div[2]/div[3]/div/div[2]')

#click on city dropdown
city_name_drop_down.click()
short_wait()    

city_button = driver.find_element_by_xpath(city_xpath)
city_button.click()
short_wait()

#get constant panel buttons
city_panel_button = driver.find_element_by_xpath('//*[@id="content"]/div/div[5]/div[1]/div/div[1]')
province_panel_button = driver.find_element_by_xpath('//*[@id="content"]/div/div[5]/div[1]/div/div[2]')

line_df = scrape_line_graph(driver)

print(line_df)

driver.quit()

#when scrape is completed - return to scrape 202 line charts

#this will get messed up with leap year
#list of dates between today and 1/1/2020

    