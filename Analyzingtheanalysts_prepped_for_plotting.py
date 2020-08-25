# -*- coding: utf-8 -*-
"""
Created on Tue Aug 25 18:09:52 2020

@author: John Arnold
"""


#Ggplot test

import pandas as pd
import numpy as np

#GGplot
import plotnine as p9

from plotnine import *





# to download the data directly:
c_remote_data ='https://raw.githubusercontent.com/nickhould/craft-beers-dataset/master/data/processed/beers.csv'
c_col = ["#2f4858", "#f6ae2d", "#f26419",
         "#33658a", "#55dde0", "#2f4858",
         "#2f4858", "#f6ae2d", "#f26419",
         "#33658a", "#55dde0", "#2f4858"]

def labels(from_, to_, step_):
    return pd.Series(np.arange(from_, to_ + step_, step_)).apply(lambda x: '{:,}'.format(x)).tolist()
def breaks(from_, to_, step_):
    return pd.Series(np.arange(from_, to_ + step_, step_)).tolist()

data = pd.read_csv(c_remote_data)
data = (
    data.filter([
        'abv',
        'ibu',
        'id',
        'name',
        'style',
        'brewery_id',
        'ounces'
    ]).
    set_index('id')
)

fig = (
    ggplot(data.dropna(subset = ['abv'])) +
    geom_histogram(aes(x = 'abv'))
)