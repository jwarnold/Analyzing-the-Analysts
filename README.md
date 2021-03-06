# Analyzing-the-Analysts
Analyzing the Price Targets set by brokerages against actual stock performance. An exploratory analysis to pull ratings data, historical stock performance and generate a time series graph to visualize how well the banks are at predicting stock prices.

Written in Python 3, I've only tested it for U.S. exchanges (NYSE, NASDAQ) the following are the requirements from the user:
  1) You'll need a few packages to get this to run properly
  
    a) beautifulsoup4
    
    b) Pandas and Numpy
    
    c) bokeh
   
    d) re (regex) 
    
  2) Set your working directory for where you want the graph to be saved
  3) Go to lines 31 - 50
  4) Input the company you want to see - by it's ticker e.g. "MSFT", "GE", "NIO"
  5) Input which exchange it is traded on. e.g. for MSFT, it's traded on the "NASDAQ", GE is traded on the "NYSE"
  6) Change your start and enddates accordingly
  7) Run my script, the graph will be saved where you set your working directory 
  8) If you want to see different brokerages / investment banks, find the "broke_list" variable to get you a list of ratings provided, change them in the bank list variable on         line 44
  
Please provide credit where credit is due:

  john.jw.arnold@gmail.com
  
  https://www.linkedin.com/in/john-arnold-99aab0189/
  
I am very open to criticism or pointers to my coding and style

Shameless plug: If you liked it or found it useful, consider interviewing me for a job! I am based in Toronto.
