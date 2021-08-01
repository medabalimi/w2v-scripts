#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct  2 01:51:56 2020

@author: anand
"""

import librosa

import os,sys
import soundfile as sf
import numpy
import parse
import glob
import re

import random
import json


import click
from tqdm import tqdm
from collections import defaultdict
from collections import Counter

valid_fs=[8000,16000]
max_frames=320000
min_frames=16000
stm_parser=parse.compile('{audio_filename} {channel:d} {speaker} {start:g} {end:g} {options} {text}')
wav_parser=parse.compile('{wav_id}\t{wav_path}')
segments_parser=parse.compile('{seg_id} {wav_id} {start:g} {end:g}')
text_parse=parse.compile('{seg_id}\t{text}')
def resample_audio(signal, orig_fs, target_fs):
    """
    :param signal: signal to resample to
    :param orig_fs: original sampling frequency
    :param target_fs: target sampling frequency
    :return:
    """
    signal = librosa.core.resample(signal, orig_fs, target_fs)

    if signal.ndim == 1:
        signal = signal.reshape(signal.shape[0], -1)
    elif signal.shape[1] > signal.shape[0]:
        signal = signal.T
        
    return signal

audio_files_ext=['wav','flac','mp3','ogg','m4a', 'm3a', 'webm']

stmline_is_comment= lambda a: a.strip()[0:2]==';;'
stmline_is_empty = lambda a: len(a)<10
   

REGEX_FOR_INVALID_CHARS=re.compile( r"[^A-Z\ ']+" )

def cleanup_text(text):
    text=text.replace("’","'")     
    text = re.sub(r"\[[A-Z_\/]+\]"," ", text)
    text = re.sub(r"\!SIL"," ", text)
    
 
    text = re.sub("\["," ", re.sub("\]"," ", text))
    
    word_list = text.split()
 
    text=' '.join(word_list)

        
    text=text.replace('-', ' ')
    
    text = re.sub('\s{2,}',' ', text.strip())
    
    
    return text

    

def read_wav_scp(data_folder):
    wav_ids={}
    with open(f'{data_folder}/wav.scp','r') as wav_scp_file:
        for line in wav_scp_file:
            d=line.strip().split(maxsplit=1)
            wav_ids[d[0]]=d[1]
            
    return wav_ids  

def read_segments(data_folder):
    seg_info={}
    with open(f'{data_folder}/segments','r') as seg_file:
        for line in seg_file:
            seg_parsed=segments_parser.parse(line.strip())
            if seg_parsed:
                seg=seg_parsed.named
                seg_id=seg.pop('seg_id')
                seg_info[seg_id]=seg
                seg_info[seg_id]['text']=""
                seg_info[seg_id]['valid']=True
    if os.path.exists(f'{data_folder}/text'):
        with open(f'{data_folder}/text','r') as text_file:
            for line in text_file:
                print(line)
                try:
                    [seg_id,text]=line.strip().split(maxsplit=1)
                except:
                    seg_id=line.strip()
                    text=""
                    valid=False

                try:
                    text
                except Exception as exp:
                    print(text)
                    raise Exception(exp)
                else:
                    valid=True

                seg_info[seg_id]['text']=text
                seg_info[seg_id]['valid']=valid
    
    return seg_info

def get_audio_from_segments(segments, wav_scp, audio_root):
    audio_file=''
    fs=None
    signal=None
    
    for seg_id,seg in segments.items():
        if audio_file != wav_scp[seg['wav_id']]:
            print(f"Reading: {audio_file}")

            audio_file = wav_scp[seg['wav_id']]
            audio_file_path=os.path.join(audio_root,audio_file)

            print(audio_file_path)
            

            signal,fs=librosa.load(audio_file_path, 
                                    mono=False, sr=None)
            if signal.ndim == 1:
                signal = signal.reshape(signal.shape[0], -1)
            elif signal.shape[1] > signal.shape[0]:
                signal = signal.T

        seg_start = numpy.floor(fs * seg['start']).astype(int)
        seg_end = numpy.ceil(fs * seg['end']).astype(int)
        yield seg_id,signal[seg_start:seg_end,0,],fs
    
def generate_segments(data_folder, audio_root, target_fs=16000, 
                      output_dir=None, 
                      manifest_dir=None, 
                      valid_percent=0.1, seed=42):


    if output_dir==None:
        output_dir=audio_root
    if manifest_dir==None:
        manifest_dir=data_folder
    
    output_dir=os.path.join(output_dir,'segments')
        
    manifest_dir=os.path.join(manifest_dir,'manifest')
        
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(manifest_dir, exist_ok=True)
    
    
    rand = random.Random(seed)

    train={}
    train_error={}
    valid={}
    files_processed=0
    skipped_segs=0
    skipped_len=0.0
    processed_segs=0
    processed_len=0
    files_to_fix={}
    set_durations=defaultdict(float)
    with open(os.path.join(manifest_dir,'train.tsv'),'w') as train['mf'], \
         open(os.path.join(manifest_dir,'train_error.tsv'),'w') as train_error['mf'], \
         open(os.path.join(manifest_dir,'valid.tsv'),'w') as valid['mf'], \
         open(os.path.join(manifest_dir,'train.ltr'),'w') as train['ltr'], \
         open(os.path.join(manifest_dir,'train_error.ltr'),'w') as train_error['ltr'], \
         open(os.path.join(manifest_dir,'valid.ltr'),'w') as valid['ltr'], \
         open(os.path.join(manifest_dir,'train.wrd'),'w') as train['wrd'], \
         open(os.path.join(manifest_dir,'train_error.wrd'),'w') as train_error['wrd'], \
         open(os.path.join(manifest_dir,'valid.wrd'),'w') as valid['wrd'], \
         open(os.path.join(manifest_dir,'dict.ltr.txt'),'w') as dict_ltr:


        ltr_dict={}
        wav_scp=read_wav_scp(data_folder)
        segments=read_segments(data_folder)
        wav_scp=read_wav_scp(data_folder)
        train['mf'].write(os.path.abspath(f'{output_dir}\n'))
        train_error['mf'].write(os.path.abspath(f'{output_dir}\n'))
        valid['mf'].write(os.path.abspath(f'{output_dir}\n'))
        sentences=''
        for seg_id,signal,fs in get_audio_from_segments(segments,wav_scp, audio_root):
        
#        for seg_id in segments:
            segment=segments[seg_id]
            audio_path=os.path.join(output_dir,segment['wav_id'])
            os.makedirs(audio_path, exist_ok=True)
            out_fname=f"{segment['wav_id']}/{seg_id}.wav"
            audio_seg_file=os.path.join(output_dir,out_fname)
            if not os.path.exists(audio_seg_file):
            #    print(audio_seg_file)
                sf.write(audio_seg_file,signal,fs)
            duration=sf.info(audio_seg_file).frames
            dest = train if rand.random() > valid_percent else valid
            dest['mf'].write(f'{out_fname}\t{duration}\n')
            dest['wrd'].write(f'{segment["text"].strip()}\n') 
            dest['ltr'].write(f"{' '.join(segment['text'].strip().replace(' ','|'))} |\n")
            sentences= sentences + segment['text'].strip()+ ' '
            processed_segs += 1
            processed_len += duration/target_fs
            set_name=dest['mf'].name.split('/')[-1]
            set_durations[set_name]=set_durations[set_name]+duration/target_fs

        ltr_count=Counter(sentences)
        if ' ' in ltr_count:
            ltr_count['|']=ltr_count.pop(' ')
        for w in ltr_count:
            if w not in ltr_dict:
                ltr_dict[w]=ltr_count[w]
            else:
                ltr_dict[w]=ltr_dict[w]+ltr_count[w]



                            #print(f"skipped {skipped_segs} of length {duration}. Total skipped {skipped_len}")
        for w in {k: v for k, v in sorted(ltr_dict.items(), key=lambda item: item[1], reverse=True)}:
            dict_ltr.write(f'{w} {ltr_dict[w]}\n')

def validate_fs(ctx,param,value):
    if not value in valid_fs:
        raise click.BadParameter(f'Invalid sample rate. Should be one of {valid_fs}')
    return value
        

@click.command()
@click.option('--target_fs', default=16000, callback=validate_fs, \
              help='Target samplerate. If not specified, same of source')
   
@click.option('--audio_output_folder', default=None, \
              help="Folder to write the output files to. "+
              "Default: 'segments' subfolder in the input folder")
@click.option('--manifest_folder', default=None, \
              help="Folder to write the manifest files to. "+
              "Default: 'manifest' subfolder in the input folder")
@click.option('--valid_percent', default=0.0, type=click.FloatRange(0,1), \
              help="percentage of data to use as validation set (0<= val<= 1)"+
              "Default value: 0.0")
@click.option('--rnd_seed', default=42, type=int, \
              help="random seed. Default: 42")
@click.argument('data_folder')
@click.argument('audio_root')
def segment_audio(data_folder,audio_root, audio_output_folder, manifest_folder, target_fs, \
                  valid_percent, rnd_seed):
    generate_segments(data_folder, audio_root, target_fs, 
                      audio_output_folder, 
                      manifest_folder, 
                      valid_percent, rnd_seed)

if __name__=="__main__":
    segment_audio()
    
