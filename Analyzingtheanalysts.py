# -*- coding: utf-8 -*-
"""
Created on Sat Jul 18 13:19:32 2020

@author: John Arnold
"""

#Imports

import requests
import pandas as pd
import numpy as np
#regex
import re

#webscraper
from bs4 import BeautifulSoup
import csv

#To pull historical financial data
from pandas_datareader import data as pda
import datetime

#Bokeh
#pip install pandas bokeh pyproj
from bokeh.plotting import figure, output_file, show
from bokeh.models import ColumnDataSource
from bokeh.models.tools import HoverTool
from bokeh.palettes import Spectral8



#%% 
""" FIRST THINGS FIRST """

#Set your ticker and exchange e.g. "GE" and "NYSE" or "MSFT" and "NASDAQ"

ticker="GE"
exchange="NYSE"

#Run this script, check the "broke_list" variable for a list of the investment banks, change the banklist
#list variable according to which ones you want

banklist = ["Deutsche Bank", "Bank of America", "JPMorgan Chase", "Citigroup",\
            "Morgan Stanley", "Barclays", "Goldman Sachs Group"]

#Set your start and end dates for the historical stock prices
#Pull the ratings first if you want an idea of how far back to go. 

startdate = datetime.datetime(2017, 3, 1) 
enddate = datetime.datetime(2020, 9, 10)




#%%

""" Pull out the marketbeat ratings and other info
    Set the ticker and trade exchange """
    

url_start = "https://www.marketbeat.com/stocks/"
url_middleslash="/"
url_end = "/price-target/?MostRecent=0"

url1 = url_start+exchange+url_middleslash+ticker+url_end
#url1 = "https://www.marketbeat.com/stocks/NYSE/GE/price-target/?MostRecent=0"

#Need special parameters to auto select a dropdown on the site where url doesn't change

with requests.Session() as session:
    session.headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
    
    response = session.get(url1)
    soupmb = BeautifulSoup(response.content)
    
    data = {
        "ctl00$cphPrimaryContent$ddlShow":"All Ratings For This Stock",
         '__EVENTTARGET': soupmb.find('input', {'name': '__EVENTTARGET'}).get('value', ''),
        '__EVENTARGUMENT': soupmb.find('input', {'name': '__EVENTARGUMENT'}).get('value', ''),
        '__LASTFOCUS': soupmb.find('input', {'name': '__LASTFOCUS'}).get('value', ''),
        '__VIEWSTATE': soupmb.find('input', {'name': '__VIEWSTATE'}).get('value', ''),
        '__VIEWSTATEGENERATOR': soupmb.find('input', {'name': '__VIEWSTATEGENERATOR'}).get('value', ''),
        '__EVENTVALIDATION': soupmb.find('input', {'name': '__EVENTVALIDATION'}).get('value', ''),
    }
    
    response = session.post(url1, data = data)
    
    soupmb = BeautifulSoup(response.content)
    
print(response.status_code)


#%%

#Initial pull from the HTML

tabledesignation = soupmb.find("table", attrs = {"class":"scroll-table sort-table"})

ratinglist = []

#Pull the rows in the table, cleanup the ensuing mess,the flattened format of the HTML table is "stra"

for row in tabledesignation.find_all("tr"):
    for cell in row.find_all("td"):
            ratinglist.append(cell.contents)

#This is called list comprehension - READ UP ON THIS, COPY PASTED OFF OF STACK EXCHANGE
#Flatten the ratinglist, any [] get filled with nans on the line below
flatratinglist = [name for sublist in ratinglist for name in (sublist or [np.nan])]

stra = []

for item in flatratinglist:
    stra.append(str(item))
    
#%%
#Remove the Ad block of HTML, hopefully it is it in the same position on all ticker pages
#POTENTIAL issue that could break the HTML pull
newstra = [x for x in stra if not 'div class="txt-center fake-sticky' in x]

newdates = newstra[::7]
broke = newstra[1::7]
newbroke = []
for item in broke:
    newbroke.extend(re.findall('recommendations\/">(.+)?<\/a>', item))
    
newact = newstra[2::7]
newrati = newstra[3::7]
newpt = newstra[4::7]

#%%
"""Setting the data pulls into a workable Pandas dataframe"""


#display more rows in output
pd.set_option('display.max_columns',20)
pd.set_option('display.max_rows',75)
pd.set_option('display.width', 100)
#Set the ratings dataframe
df_ra = pd.DataFrame([newdates, newbroke, newact, newrati, newpt])
#Transpose it
df_ra = df_ra.T
#Rename the columns
df_ra.columns=["date", "brokerage", "action", "rating","pt"]


#df_ra nan's aren't being treated as actual NaNs since they're strings
# Require the anchor (^) as "Tigress Financial" gets pulled out
df_ra = df_ra.replace("^nan", np.nan, regex = True)

#Coerce values in "date" columns to date datatype
df_ra["date"] = pd.to_datetime(df_ra["date"])

#Fix JPM strings

df_ra = df_ra.replace("JPMorgan.+", "JPMorgan Chase", regex = True)


#Need to deal with the arrows, will add secondary columns for rating and pt 
#to take the left side arrow
#Logic to follow when graphing.
#If the value to be graphed does not have a preceding value (i.e. NaN)
#grab the left side arrow as the preceding value to be graphed (timeseries-wise)
#If there is an NaN and no arrow, take the preceding value before the NaNs

#Create new columns if arrows are present in rating or pt, grab right side of arrow value in pt and replace

#Wrangling the Data Frame to get the desired format - mostly dealing with right pointing arrows
df_ra["rating_prior"] = df_ra["rating"].str.extract("(.+) ➝")
df_ra["pt_prior"] = df_ra["pt"].str.extract("(.+) ➝")

df_ra["pt_part1"] = df_ra["pt"].str.extract("(^(?!.+➝).*$)")
df_ra["pt_part2"] = df_ra["pt"].str.extract("➝ (.+)")
df_ra["pt_part1"] = df_ra["pt_part1"].combine_first(df_ra["pt_part2"])
df_ra["pt"] = df_ra["pt_part1"]
df_ra = df_ra.drop("pt_part1", 1)
df_ra = df_ra.drop("pt_part2", 1)

df_ra["rating_part1"] = df_ra["rating"].str.extract("(^(?!.+➝).*$)")
df_ra["rating_part2"] = df_ra["rating"].str.extract("➝ (.+)")
df_ra["rating_part1"] = df_ra["rating_part1"].combine_first(df_ra["rating_part2"])
df_ra["rating"] = df_ra["rating_part1"]
df_ra = df_ra.drop("rating_part1", 1)
df_ra = df_ra.drop("rating_part2", 1)

#%% Pull Historical Performance Data for stock via DataReader

df_his = pda.DataReader(name = ticker, data_source = "yahoo", start = startdate, end = enddate)
df_his = df_his.reset_index()

#%% More data manipulation on df_ra to narrow down the list of brokerages and touchups

#Get a list of the unique brokerages in the list
broke_list = df_ra.brokerage.unique()
#Largest investment banks/brokerages from IBIS world
#Citigroup, JPMorgan Chase, Goldman Sachs, Morgan Stanley, Bank of America, Deutsche Bank, Barclays
#Own personal choirces, Oppenheimer, Royal Bank of Canada, Morningstar

#Change the pt and pt_prior columns to floats


df_ra["pt"]=df_ra["pt"].replace('[\$]',"", regex = True).astype(float)
df_ra["pt_prior"] = df_ra["pt_prior"].replace('[\$]',"", regex = True).astype(float)



#%% Graphing Time


#Set min and max for y-axis
max_y = df_his["Close"].max() + (df_his["Close"].max()*.15)
min_y = df_his["Close"].min() - (df_his["Close"].min()*.5)

min_x = min(df_ra["date"])
max_x = max(df_ra["date"])


#%%
df_ra_red = df_ra[df_ra["brokerage"].isin(banklist)]

p = figure(plot_width=800, plot_height=250, x_axis_type="datetime")
    
#For Bokeh need to create seperate dataframes for each of the banks
db = df_ra_red[df_ra_red.brokerage == 'Deutsche Bank']
bac = df_ra_red[df_ra_red.brokerage == 'Bank of America']
jpm = df_ra_red[df_ra_red.brokerage == 'JPMorgan Chase']
cg = df_ra_red[df_ra_red.brokerage == 'Citigroup']
ms = df_ra_red[df_ra_red.brokerage == 'Morgan Stanley']
barc = df_ra_red[df_ra_red.brokerage == 'Barclays']
gs = df_ra_red[df_ra_red.brokerage == 'Goldman Sachs Group']

TOOLS = 'crosshair,save,pan,box_zoom,reset,wheel_zoom'
p = figure(title="{} Bank Price Targets vs. Actual Closing Price".format(ticker), y_axis_type="linear",x_axis_type='datetime', tools = TOOLS,plot_width=1400, plot_height=600)

p.line(df_his["Date"], df_his["Close"], legend = "Closing Price", line_color = "green", line_width = 3)
p.step(db['date'], db.pt, legend="DB", line_color= Spectral8[0], line_width = 3)
p.step(bac['date'], bac.pt, legend="BAC", line_color=Spectral8[1], line_width = 3)
p.step(jpm['date'], jpm.pt, legend="JPM",line_dash="dotted",line_color="black", line_width = 4)
p.step(cg['date'], cg.pt, legend="Citigroup", line_color="#f46d43", line_width = 3)
p.step(ms['date'], bac.pt, legend="Morgan Stanley", line_color="black", line_width = 3)
p.step(barc['date'], bac.pt, legend="Barclays", line_color=Spectral8[5], line_width = 3)
p.step(gs['date'], bac.pt, legend="Goldman Sachs",line_dash="dashed", line_color=Spectral8[6], line_width = 3)

p.legend.location = "bottom_left"
p.legend.click_policy="hide"

p.xaxis.axis_label = 'Date'
p.yaxis.axis_label = 'pt'


show(p)

output_file("{} PTs vs Close Bokeh.html".format(ticker), title="Bokeh Pt plots")

