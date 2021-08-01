#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Feb 14 16:39:44 2021

@author: anand
"""

import sys

def generate_eval_output(tsv_file, hypothesis_file):
    with open(tsv_file,'r') as tsv:
        next(tsv)
        segments=[]
        for line in tsv:
            segments.append({'segment':line.strip().split()[0]})

    
    with open(hypothesis_file,'r') as hypothesis:
        for line in hypothesis:
            print(line)
            line=line.strip()
            if len(line.strip())>4:
                utt=line.strip().rsplit(maxsplit=1)
                (spk,idx)=utt[-1][1:-1].split('-')
                if len(utt)==2:
                    segments[int(idx)]['text']=utt[0]
                else:
                    segments[int(idx)]['text']=''
    return segments

def write_segments(segments, out_file):
    seg_dict={}
    with open(out_file,'w') as fp:
        for seg in segments:
            print(seg)
            if 'text' not in seg:
                print("Missing text, not all segments were decoded")
                seg['text']=""
            fp.write(f"{seg['segment'].split('/')[-1][:-4]}\t{seg['text']}\n")
            seg_dict[seg['segment'].split('/')[-1][:-4]]=seg['text']
        
    return seg_dict
            

if __name__=="__main__":
    tsv_file=sys.argv[1]
    hypothesis_file=sys.argv[2]
    output_file=sys.argv[3]
    segments=generate_eval_output(tsv_file, hypothesis_file)
    write_segments(segments, output_file)
