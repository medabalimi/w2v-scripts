#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 26 03:12:13 2021

@author: anand
"""
import re
import sys
def clean_text(itext_file, otext_file, valid_chars):
    with open(itext_file,'r') as text, open(otext_file,'w') as ofp:
        for line in text:
            clean_up=line
            for i in range(len(line)):
                if line[i] not in valid_chars:
                    clean_up=clean_up.replace(line[i],' ')
                    
            #print(line,'|', ntext,'|', clean_up)

           
            clean_up=re.sub('\s{2,}',' ', clean_up.strip())
            ofp.write(clean_up+'\n')
            
   

       
if __name__=="__main__":
    valid_chars=[]
    for c in open(sys.argv[1],'r'):
        valid_chars.append(c.strip().split()[0])
    print(valid_chars)
    
    clean_text(sys.argv[2],sys.argv[3], valid_chars)
        