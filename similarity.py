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

intext = "张如仙和往寝室感情破裂,孩子归女方抚养"
seg = set(lcut_for_search(intext)) - set(stopword)
tmp_text = ""
for word in seg:
    if (word != u'\n') and (word != u'\r') and (word != u'\t') and (word != ' '):
        tmp_text += (str(word) + ' ')


vec_bow = dictionary.doc2bow(tmp_text.lower().split())
vec_lsi = lsi_model[vec_bow]
index = similarities.MatrixSimilarity(lsi_model[corpus])
sims = index[vec_lsi]
sims = sorted(enumerate(sims), key=lambda item: -item[1])
# toc = time.time()
# print toc - tic
for item in sims:
    print texts[item[0]][0]



