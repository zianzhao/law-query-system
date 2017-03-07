#!/usr/bin/env python
# -*- coding: utf-8 -*

from gensim import corpora, models, similarities
from jieba import *
# import time

import sys
stdout = sys.stdout
reload(sys)
sys.stdout = stdout
sys.setdefaultencoding('utf-8')

'''
Module name: similarity

Purpose: find the most similar case according to the description

Author: : Zian Zhao

Version: 1.0 3.7,1017
'''
# tic = time.time()
# load the model, corpus and dictionary
lsi_model = models.LsiModel.load('lsi.model', mmap='r')
dictionary = corpora.Dictionary.load('dictionary.dict')
corpus = corpora.MmCorpus('cases.mm')

# get the stopword list
words = open('stopword_origin.txt', 'r')
stopword = words.read()
words.close()

# get the corpus
infile = open('texts.txt', 'r')
texts = infile.readlines()
for i in range(len(texts)):
    texts[i] = texts[i].split()
infile.close()

intext = "输入的描述"
seg = set(lcut_for_search(intext)) - set(stopword)
tmp_text = ""
for word in seg:
    if (word != '   ') and (word != '\r') and (word != '\t') and (word != ' '):
        tmp_text += (str(word) + ' ')

if len(tmp_text.split()):

    # toc1 = time.time()
    # print toc1-tic
    vec_bow = dictionary.doc2bow(tmp_text.lower().split())
    vec_lsi = lsi_model[vec_bow]
    index = similarities.MatrixSimilarity.load('sims.index')
    sims = index[vec_lsi]
    sims = sorted(enumerate(sims), key=lambda item: -item[1])
    # toc2 = time.time()
    # print toc2 - tic
    if sims[0][1] < 0.5:
        print sims[0][1]
        print "Similar file does not exist in the database."
    else:
        count = 0
        for item in sims:
            count += 1
            print texts[item[0]][0]
            if count > 20:
                break



