#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Mar  6 07:34:29 2021

@author: anand
"""

import torchaudio
import augment
import numpy as np
import os
import click
import json


#%%

def load_manifest(manifest_path, data_set='train'):
    dataset={}
    tsvfile=f'{manifest_path}/{data_set}.tsv'
    wrdfile=f'{manifest_path}/{data_set}.wrd'
    ltrfile=f'{manifest_path}/{data_set}.ltr'
    with open(tsvfile,'r') as tsv, \
         open(wrdfile,'r') as wrd, \
         open(ltrfile,'r') as ltr:
        dataset['audio_root']=tsv.readline().strip();
        manifest=zip(tsv.readlines(),wrd.readlines(), ltr.readlines())
        dataset['data']=[]
        for tsv_info, trans_wrd, trans_ltr in manifest:
            (afile,frames)=tsv_info.strip().split('\t')
            dataset['data'].append({'audio':afile, 'frames':frames,
                                    'wrd':trans_wrd.strip(),
                                    'ltr':trans_ltr.strip()
                                    })
            
    
    return dataset

def split_path(file_path):
    paths=file_path.split('/')
    filename=paths[-1]
    dir_path='/'.join(paths[:-1])
    return dir_path,filename
    
def augment_data(src_manifest, dest_manifest='augment', 
                 data_set='train', max_audio_frames=600000, aug_per_file=10, ignore_orig=False):
    
    dataset=load_manifest(src_manifest, data_set)
    out_dataset={'audio_root':dataset['audio_root'], 'data':[]}
    if dest_manifest=='augment':
        dest_manifest=f'{src_manifest}/augment'
    os.makedirs(dest_manifest, exist_ok=True)
    # input signal properties

    # output signal properties
    target_info = {'channels': 1, 
               'length': 0, # not known beforehand
               'rate': 16_000}

    random_pitch = lambda: np.random.randint(-400, +200)
    random_speed = lambda: np.random.uniform(0.75, 1.25)

    # output signal properties
    target_info = {'channels': 1, 
                   'length': 0, # not known beforehand
                   'rate': 16_000}
    audio_root=f"{dataset['audio_root']}"
    mf_out={}
    mf_out['tsv']=open(os.path.join(dest_manifest,f'{data_set}.tsv'),'w')
    mf_out['wrd']=open(os.path.join(dest_manifest,f'{data_set}.wrd'),'w')
    mf_out['ltr']=open(os.path.join(dest_manifest,f'{data_set}.ltr'),'w')
    
    mf_out['tsv'].write(f"{audio_root}\n")
    
    for data in dataset['data']:
        out_dataset['data'].append(data)
        if not ignore_orig:
            mf_out['tsv'].write(f"{data['audio']}\t{data['frames']}\n")
            mf_out['wrd'].write(f"{data['wrd']}\n") 
            mf_out['ltr'].write(f"{data['ltr']}\n") 
        audio_in=f"{audio_root}/{data['audio']}"
        print(audio_in)
        x, sr = torchaudio.load(audio_in)        
        # input signal properties
        src_info = {'rate': sr}
        
        for aug_id in range(aug_per_file):


            random_dropout = np.random.uniform(0, 0.25)
            no_frames_valid=False

            while not no_frames_valid:
                y = augment.EffectChain().time_dropout(max_seconds=0.1).pitch(random_pitch).speed(random_speed).rate(16_000).apply(x, src_info=src_info, target_info=target_info)
                frames=max(y.shape)
                if (frames >= max_audio_frames) and (max_audio_frames>0):
                    print(f"Generated audio is too long {frames} frames, retrying")
                else:
                    no_frames_valid=True
            #y = augment.EffectChain().time_dropout(max_seconds=random_dropout).apply(x, src_info=src_info)
            rel_out_file=f"augmentations_{aug_per_file}/{aug_id}/{data['audio']}"
            aug_out_file=f"{audio_root}/{rel_out_file}"
            aug_out_folder,filename=split_path(aug_out_file)
            if not os.path.exists(aug_out_folder):
                os.makedirs(aug_out_folder, exist_ok=True)
            torchaudio.save(aug_out_file,y,sample_rate=sr)
            #print(f"y={max(y.shape)}, frames={frames}")
            mf_out['tsv'].write(f"{rel_out_file}\t{frames}\n")
            mf_out['wrd'].write(f"{data['wrd']}\n") 
            mf_out['ltr'].write(f"{data['ltr']}\n") 
            
            out_dataset['data'].append({'audio': rel_out_file, 
                                        'frames': frames,
                                        'wrd': data['wrd'],
                                        'ltr': data['ltr']
                                    })
            
            
    json.dump(out_dataset,open('/tmp/debug.json','w'))


            
            
@click.command()
@click.option('--augs', default=10, type=click.IntRange(1,20), \
              help="No. of augmentations per audio file. "+
              "Default value: 10")
@click.option('--ignore_orig', default=False, type=bool, \
              help="Do not keep original audio in augmented manifest")    
@click.option('--dataset', default='train', type=str, \
              help="Data set to process (typically one of train, dev, eval) "+
              "Default value: 'train'")
@click.option('--max_audio_frames', default=-1, type=int, \
              help="Max length of audio frames to be output post modification"
              ) 
    
@click.argument('src_manifest_path')
@click.argument('dest_manifest_path')
def main(src_manifest_path,dest_manifest_path,dataset,max_audio_frames, augs,ignore_orig):
    augment_data(src_manifest_path,dest_manifest_path,dataset,max_audio_frames,augs,ignore_orig)
    
if __name__=="__main__":
    main()       
        
    
    
    
