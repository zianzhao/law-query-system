# -*- coding: utf-8 -*-

import sys
import pymysql
import re
from time import clock  # for timing

# Set the default code
stdout = sys.stdout
reload(sys)
sys.stdout = stdout
sys.setdefaultencoding('utf-8')

'''
Module name: attachLabel

Purpose: use RE to attach the labels in the cases
         modified to fit mysql

Parameter:
None

Return value:
None

Author: Ruxuan Zhang (reflexit)

Version: 1.1 on 2017/3/9
'''

def attachLabel():
    wrong_id = []
    
    # connect the mysql database
    con = pymysql.connect(user = 'root', passwd = '12345678', db = 'lawcase', charset = 'utf8')
    cursor = con.cursor()
    cursor.execute("SET NAMES utf8")
    cursor.execute("FLUSH QUERY CACHE")

    # find the number of law cases
##    cursor.execute('select count(*) from divorce_data')
##    tmp = cursor.fetchone()
##    num = tmp[0]    # number of law cases

    # ID's are not consecutive!!!
    num = 740000    # exact count is 739019

    # Match patterns:
    patterns1 = [u"暴力", u"重婚", u"虐待", u"遗弃",
                 u"同居", u"隐藏财产", u"转移财产", u"变卖财产",
                 u"毁损财产", u"伪造债务", u"彩礼返还", u"艾滋病",
                 u"赌博", u"吸毒", u"残疾", u"房产",
                 u"福利房", u"商品房", u"房屋产权", u"住房公积金",
                 u"终审"]
    patterns2 = [u"精神分裂", u"军人", u"下落不明", u"外籍|外国人"]
    pat2Name = ["mental_pros", "soldier_pros", "missing_pros", "foreign_pros",
                "mental_def", "soldier_def", "missing_def", "foreign_def"]

    # just to show progress
    old1000 = 0;
    
    for i in range(num):        
        # get the path of law case i+1
        cursor.execute('select content from divorce_data where id = (%d)' % (i+1))
        tmp = cursor.fetchone()
        if tmp is None: # if the entry is empty
            continue
        text = tmp[0]
        # print text

        # match patterns1
        for idx in range(len(patterns1)):
            pat = patterns1[idx]
            mch = list(set(re.findall(pat, text)))
            try:
                if len(mch) > 0:
                    cursor.execute("UPDATE divorce_data SET lb%d = true WHERE id = '%d'" % (idx + 1, i + 1))
                else:
                    cursor.execute("UPDATE divorce_data SET lb%d = false WHERE id = '%d'" % (idx + 1, i + 1))
            except :
                wrong_id.append(i + 1)
        
        # match patterns2
        for idx in range(len(patterns2)):
            pat = patterns2[idx]
            mch = list(set(re.findall(pat, text)))

            if len(mch) > 0:    # pattern found
                # go on to find prosecutor or defender
                flag = False
                sents = cutSent(text)
                for j in range(len(sents)):
                    mch1 = list(set(re.findall(pat, sents[j])))
                    if len(mch1) > 0:
                        cur = j
                        wordCnt = 0
                        mchYuan = list(set(re.findall(u"原告", sents[j])))
                        mchBei = list(set(re.findall(u"被告", sents[j])))

                        # if not found in current sentence, search backward within 30 words
                        while len(mchYuan) == 0 and len(mchBei) == 0 and cur >= 0 and wordCnt <= 30:
                            cur -= 1
                            wordCnt += len(sents[cur])
                            mchYuan = list(set(re.findall(u"原告", sents[cur])))
                            mchBei = list(set(re.findall(u"被告", sents[cur])))

                        # find prosecutor and/or defender
                        if len(mchYuan) > 0 or len(mchBei) > 0:
                            flag = True
                            try:
                                if len(mchYuan) > 0:
                                    cursor.execute("UPDATE divorce_data SET " + pat2Name[idx] + " = true WHERE id = '%d'" % (i + 1))
                                else:
                                    cursor.execute("UPDATE divorce_data SET " + pat2Name[idx] + " = false WHERE id = '%d'" % (i + 1))
                                if len(mchBei) > 0:
                                    cursor.execute("UPDATE divorce_data SET " + pat2Name[idx + 4] + " = true WHERE id = '%d'" % (i + 1))
                                else:
                                    cursor.execute("UPDATE divorce_data SET " + pat2Name[idx + 4] + " = false WHERE id = '%d'" % (i + 1))
                            except:
                                wrong_id.append(i + 1)
                            break

                # for-j-loop end

                # pattern not found within 30 words
                if not flag:
                    try:
                        cursor.execute("UPDATE divorce_data SET " + pat2Name[idx] + " = false WHERE id = '%d'" % (i + 1))
                        cursor.execute("UPDATE divorce_data SET " + pat2Name[idx + 4] + " = false WHERE id = '%d'" % (i + 1))
                    except:
                        wrong_id.append(i + 1)

            else:   # pattern not found
                try:
                    cursor.execute("UPDATE divorce_data SET " + pat2Name[idx] + " = false WHERE id = '%d'" % (i + 1))
                    cursor.execute("UPDATE divorce_data SET " + pat2Name[idx + 4] + " = false WHERE id = '%d'" % (i + 1))
                except:
                    wrong_id.append(i + 1)

        # for-idx-loop end

        # just to show progress
        if i / 1000 <> old1000:
            old1000 += 1
            print "%d completed" % (old1000 * 1000)

    # outmost for-loop end

    # write the error id to the output file
    wrong_id_out = open('wrongIDLabel.txt', 'w')

    for items in wrong_id:
        wrong_id_out.write(str(items) + ' ')

    wrong_id_out.close()
    
    print "Process Completed"

    # commit the modification
    # disconnect the database
    con.commit()
    cursor.close()
    con.close()

def cutSent(text):
    cutList = u"。，,！……!《》<>\"':：？\?、\|“”‘’；]{}（）{}【】()｛｝（）：？！。，;、~——+％%`:“”＂'‘\n\r"
    l = []
    line = []
        
    for i in text:
        if i in cutList:   
            l.append(u"".join(line))   
            l.append(i)
            line = []   
        else:   
            line.append(i)   
    return l

time1 = clock()
attachLabel()
time2 = clock()
print "Time used: %.3fs" % (time2 - time1)
