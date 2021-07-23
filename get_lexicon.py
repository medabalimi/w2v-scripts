#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar 21 01:50:39 2021

@author: anand
"""
import click

from collections import defaultdict 

def def_val():
    return 0


def generate_lexicon(word_list, lex_type='letter'):
    """
    

    Parameters
    ----------
    word_list : List of words
        List of words for which lexicon has to be generated
    lex_type : TYPE, optional
        Type of lexicon to be generated. The default is 'letter'.
        Other types to be implemented are: 
            'phonetic'
            'syllabic'

    Returns
    -------
    lexicon

    """
    lexicon={}
    for word in word_list:
        word_clean=word.strip()
        if ' ' in word_clean:
            raise TypeError('Invalid word list. Word list should contain words not phrases')
        if word not in lexicon:
            lexicon[word_clean]=' '.join([ltr for ltr in word_clean]).strip()+' |'
    
    return {k: v for k, v in sorted(lexicon.items(), key=lambda item: item[0])}

def word_list(ifp):
    words=defaultdict(def_val)
    for line in ifp:
        for word in line.strip().split():
            words[word] += 1
            
    return words

def validate_input_type(ctx,param,value):
    valid_input=['words','text']
    if not value in valid_input:
        raise click.BadParameter(f"Invalid input type. Should be one of {valid_input}")
    return value

@click.command()
@click.option('--input_type', default='words', callback=validate_input_type, \
              help="""Input file type. One of 
              'words': If input is list of words
              'text': if input is a text file
              If not specified, assumed to be list of words""")
@click.argument('input_file')
@click.argument('output_file')
def main(input_file, output_file, input_type):
    print(input_type)
    if input_type=='text':
        words=word_list(open(input_file,'r'))
        print(words)
    else:
        words=open(input_file,'r')
    lexicon=generate_lexicon(words)
    with open(output_file,'w') as ofp:
        for k in lexicon:
            ofp.write(f'{k}\t{lexicon[k]}\n')


if __name__=="__main__":
    main()

            
        
    