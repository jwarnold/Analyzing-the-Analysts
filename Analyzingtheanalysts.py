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

#Seaborn
import matplotlib.pyplot as plt
import seaborn as sns




#%% 
""" FIRST THINGS FIRST """

#Set your ticker and exchange e.g. "GE" and "NYSE" or "MSFT" and "NASDAQ"

ticker="MSFT"
exchange="NASDAQ"

#Run this script, check the "broke_list" variable for a list of the investment banks, change the banklist
#list variable according to which ones you want

banklist = ["Deutsche Bank", "Bank of America", "JPMorgan Chase", "Citigroup",\
            "Morgan Stanley", "Barclays", "Goldman Sachs Group"]

#Set your start and end dates for the historical stock prices
#Pull the ratings first if you want an idea of how far back to go. 

startdate = datetime.datetime(2017, 3, 1) 
enddate = datetime.datetime(2020, 8, 10)




#%%%
"""Getting a list of the highest traded tickers in the last 3 months - mostly exploratory to see the most traded stocks
    Not a component of the graphs. Skip to the next cell for the data pull and graphing code"""

#Pull list of most actively traded stocks based on 3 month averages from yahoo finance
#https://ca.finance.yahoo.com/screener/predefined/most_actives?count=100&offset=0

r1 = requests.get("https://ca.finance.yahoo.com/screener/predefined/most_actives?count=100&offset=0", headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'})
r2 = requests.get("https://ca.finance.yahoo.com/screener/predefined/most_actives?count=100&offset=100", headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'})
print(r1.status_code)
print(r2.status_code)
c1 = r1.content
c2 = r2.content

#Parse the pulls
soup1 = BeautifulSoup(c1, "html.parser")
soup2 = BeautifulSoup(c2, "html.parser")

#Designate tables inside the html
tabledes = soup1.find("tbody")
#ticker = tabledes.find("a").contents
avgvol = tabledes.find("td", attrs = {"aria-label":"Avg Vol (3 month)"}).contents
mktcap = tabledes.find("td", attrs = {"aria-label":"Market Cap"}).contents

tabledes2 = soup2.find("tbody")

#Check their format
#print(ticker[0])
# print(avgvol[1])
# print(mktcap)

#Pull out the tickers, Avg. Volumes (3 Months) and mkt cap from the table designation
tickerlist1 = []
tickerlist2 = []

for tickers in tabledes.find_all("a"):
    tickerlist1.append(tickers.get_text())
    
for tickers in tabledes2.find_all("a"):
    tickerlist2.append(tickers.get_text())

tickerlist = tickerlist1 + tickerlist2


    
vollist1 = []
vollist2 = []

for vol in tabledes.find_all("td", attrs = {"aria-label":"Avg Vol (3 month)"}):
    vollist1.append(vol.get_text())
    
for vol in tabledes2.find_all("td", attrs = {"aria-label":"Avg Vol (3 month)"}):
    vollist2.append(vol.get_text())

vollist = vollist1 + vollist2

mktcaplist1 = []
mktcaplist2 = []

for mktcap in tabledes.find_all("td", attrs = {"aria-label":"Market Cap"}):
    mktcaplist1.append(mktcap.get_text())
    
for mktcap in tabledes2.find_all("td", attrs = {"aria-label":"Market Cap"}):
    mktcaplist2.append(mktcap.get_text())
    
mktcaplist = mktcaplist1 + mktcaplist2

#Clean up the lists (change to floats)

floatvol = []

for vol in vollist:
    if vol[-1]=="M":
        vol = vol[0:-1]
        vol=float(vol)
        vol = vol*1000000
        floatvol.append(float(vol))
    else:
        vol=vol.replace(",","")
        vol=float(vol)
        floatvol.append(float(vol))
print(floatvol)

floatcap=[]

for cap in mktcaplist:
    if cap[-1]=="T":
        cap = cap[0:-1]
        cap = float(cap)
        cap = cap*1000000000000
        floatcap.append(float(cap))
    elif cap[-1]=="B":
        cap = cap[0:-1]
        cap = float(cap)
        cap = cap*1000000000
        floatcap.append(float(cap))
    elif cap[-1]=="M":
        cap = cap[0:-1]
        cap = float(cap)
        cap = cap * 1000000
        floatcap.append(float(cap))
        
#Turn into a dataframe
        
df_ya = pd.DataFrame([tickerlist, floatvol, floatcap])

# with pd.option_context('display.max_rows', None, 'display.max_columns', None):
#     print(df_ya)
    
#Clean up the dataframes
    
df1_ya = df_ya.T
df1_ya.columns = ["Ticker","Avg_Vol(M)","mktcap(B)"]

df1_ya.sort_values(by="Avg_Vol(M)",ascending = False)

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

#Lost the smaller banks in df_ra, using df_ra_red for data in the relplot

broke_list = df_ra.brokerage.unique()
df_ra_red = df_ra[df_ra["brokerage"].isin(banklist)]


#Graphs
sns.set(style = "darkgrid")

fig1a = sns.relplot(x = "date", y = "pt", data = df_ra_red, \
                    hue = "brokerage", kind = "line",  )
    
fig1a._legend.remove()
fig2a = sns.regplot(x = 'Date', y = 'Close', data = df_his, \
                     fit_reg = False, marker = ".", scatter_kws = {'s':2})



#Make x axis date friendly
fig1a.fig.autofmt_xdate()

#Change the title and axes labels
fig1a.set(xlabel = "Date", ylabel = "Closing Price / Price Target")
fig1a.set(title = ticker)

#PLace legend outside of figure
plt.legend(bbox_to_anchor = (1.05, 1), loc=2, borderaxespad = 0.)

plt.grid(True)

plt.savefig('MSFT_600dpi.pdf', dpi =600)

