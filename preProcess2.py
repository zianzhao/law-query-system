# -*- coding: UTF-8 -*-

import jieba.posseg as pseg
import pymysql as mysql

'''----------------------------------------------------------------------------
Module name:
preprocess.py

Description:
Tokenize the txt and calculate the tf-idf value
Modified to operate with mysql
Read from mysql and write back

Author:
Zhao Zian
Rev. 2 10.26.2016
----------------------------------------------------------------------------'''

'''----------------------------------------------------------------------------
Set default code
Description: set default code as utf-8
Author: ZRX
----------------------------------------------------------------------------'''
import sys
stdout = sys.stdout
reload(sys)
sys.stdout = stdout
sys.setdefaultencoding('utf-8')

'''----------------------------------------------------------------------------------
fenci

Purpose:
Tokenize the txt and delete stop words

Parameters:
[in] string intext - the content of the law case
[in] list stopWord - the list contain stopWords

Return:
string outText - the sliced content

Author:
Zhao Zian
Rev. 2 10.26.2016
----------------------------------------------------------------------------------'''

'''----------------------------------------------------------------------------------
fenci

Revision: write file id at the beginning

Author:
Zhao Zian
Rev. 2.1 2.22,2017
----------------------------------------------------------------------------------'''

'''----------------------------------------------------------------------------------
fenci

Revision: delete the named entity in text

Author:
Zhao Zian
Rev. 2.2 2.22,2017
----------------------------------------------------------------------------------'''


def fenci(intext, stopword, file_id):
    outtext = "%d " % file_id
    # tokenize and delete the stop word
    words = list(set(pseg.cut(intext)))
    for i in range(len(words)):
        if words[i].flag[:2] == 'nr':
            if 1 < len(words[i].word) < 5:
                words[i] = 0
        else:
            pos = str(words[i]).index('/')
            words[i] = str(words[i])[:pos]

    while True:
        try:
            words.remove(0)
        except:
            break

    seg = set(words) - set(stopword)
    for word in seg:
        if (word != u'\n') and (word != u'\r') and (word != u'\t') and (word != ' '):
            outtext += (str(word) + ' ')
    return outtext


''' Main section begins'''
# the outFile
outFile = open('/users/zw/desktop/texts.txt', 'w')
# get the stopword list
words = open('stopword_origin.txt', 'r')
stopWord = words.read()

# connect the database
db = mysql.connect(user='root', passwd='12345678', db='lawcase', charset='utf8')
cursor = db.cursor()
cursor.execute("SET NAMES utf8")
cursor.execute("FLUSH QUERY CACHE")

# find the number of lawcases
cursor.execute('select count(*) from divorce_data')
tmp = cursor.fetchone()
num = tmp[0]    # number of lawcases

for i in range(num):
    try:
        # get the content of lawcase i+1
        cursor.execute('select content from divorce_data where id = %d' % (i+1))
        tmp = cursor.fetchone()
        text = tmp[0]

        outText = fenci(text, stopWord, i+1)
        outFile.write(outText + '\n')
    except Exception as e:
       pass


cursor.close()          # close the database
db.close() 
words.close()           # close the stopword file
outFile.close()         # close the output file 

