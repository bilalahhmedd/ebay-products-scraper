#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import numpy as np
import os

files=["jeans","pants","shorts","underwear"]
'''
input parameters
'''

#just a precaution if this string is in col name then replace it 
col_string_replace=""



for fil in files:

    dest_folder = '/home/fahad//Desktop/Hammoq/ebay-products-scraper-main 22 feb/ebay-products-scraper-main/scraping-ebay-1.0.3/'+fil
    input_xlsx = 'men_lowers/'+ fil+'.xlsx'

    '''
    read input xlsx file
    '''
    df_to_scrap = pd.read_excel(input_xlsx)
    cols = list(df_to_scrap.columns)

    '''
    create destination folder
    '''
    if not os.path.exists(dest_folder):
        os.mkdir(dest_folder)
        print(f'{dest_folder} created successfully')

    '''
    Read txt from multidir.sh
    '''

    data=[]
    with open('multidir.sh','r') as f:
        for txt in f.readlines():
            data.append(txt)

    current_path = os.path.realpath('./')
    for col in cols:
        if not os.path.exists(f"{dest_folder}/{col.replace(col_string_replace,'')}"):
            os.makedirs(f"{dest_folder}/{col.replace(col_string_replace,'')}")
        
        with open(f"{dest_folder}/{col.replace(col_string_replace,'')}/multidir.sh",'w') as w:
            for i,txt in enumerate(data):
                if i ==0:
                    w.write(txt)
                    for val in df_to_scrap[col].dropna():
                        w.write(val.replace('in','In').replace(' ','_')+'\n')
                else:
                    w.write(txt)
        
        os.chdir(f"{dest_folder}/{col.replace(col_string_replace,'')}/")
        print(os.path.realpath('./'))
        
        try:
            os.system('bash multidir.sh')
        except:
            print(f"{col} caught an exception while crawling")
        
        os.chdir(current_path)




