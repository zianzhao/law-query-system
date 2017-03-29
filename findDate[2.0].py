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
Module name: findDate

Purpose: use RE to find the date of the cases (if provided)
         modified to fit mysql

Parameter:
None

Return value:
None

Author: Ruxuan Zhang (reflexit)

Version: 2.0 on 2017/3/29
'''

def findDate():
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

    # Match pattern:
    pat = u"二.{3}年\W{1,3}?月\W{1,3}?日"

    # just to show progress
    old10000 = 0;
    
    for i in range(num):
        date = u""  # variable storing date found in the case
                    # type unicode
        
        # get the path of law case i+1
        cursor.execute('select content from divorce_data where id = (%d)' % (i+1))
        tmp = cursor.fetchone()
        if tmp is None: # if the entry is empty
            continue
        text = tmp[0]
        # print text

        # match date and write to mysql
        mch = list(set(re.findall(pat, text)))
        #print len(mch)
        
        if len(mch) >= 1:   # find date
            for idx in range(len(mch)):
                rr = mch[idx]
                if type(rr) == type(u""):
                    date = rr
                else:
                    date = rr[0]
                #print date

                # convert to timestamp format
                newDate = convertDate(date)
                #print newDate
                if newDate <> "-1":
                    break
                
            if newDate == "-1": # wrong date
                wrong_id.append(i + 1)
                #print "Error in id = %d" % (i + 1)
                try:
                    cursor.execute("UPDATE divorce_data SET casedate = null WHERE id = '%d'" % (i + 1))
                except:
                    wrong_id.append(i + 1)
            else:
                try:
                    cursor.execute("UPDATE divorce_data SET casedate = '" + newDate + "' WHERE id = '%d'" % (i + 1))
                except :
                    wrong_id.append(i + 1)
            
        else:   # no date found
            wrong_id.append(i+1)
            #print "No date in id=%d" % (i+1)
            try:
                cursor.execute("UPDATE divorce_data SET casedate = null WHERE id = '%d'" % (i+1))
            except :
                wrong_id.append(i+1)

        #print i + 1

        # just to show progress
        if i / 10000 <> old10000:
            print "%d completed" % i
            old10000 += 1

    # for-loop end

    # write the error id to the output file
    wrong_id_out = open('wrongDateID.txt', 'w')

    for items in wrong_id:
        wrong_id_out.write(str(items) + ' ')

    wrong_id_out.close()
    
    print "Process Completed"

    # commit the modification
    # disconnect the database
    con.commit()
    cursor.close()
    con.close()

def convertDate(date):
    year = u""
    month = u""
    day = u""
    table = [u"〇", u"一", u"二", u"三", u"四", u"五", u"六", u"七", u"八", u"九",
             u"十", u"十一", u"十二", u"十三", u"十四", u"十五", u"十六", u"十七", u"十八", u"十九",
             u"二十", u"二十一", u"二十二", u"二十三", u"二十四", u"二十五", u"二十六", u"二十七", u"二十八", u"二十九",
             u"三十", u"三十一"]
    newDate = "20"  # assume every case is in 21st century!

    i = 0
    while (date[i] <> u"年"):
        year += date[i]
        i += 1
    i += 1
    while (date[i] <> u"月"):
        month += date[i]
        i += 1
    i += 1
    while (date[i] <> u"日"):
        day += date[i]
        i += 1
    #print year, month, day
    if len(year) <> 4:
        return "-1"

    for k in range(2):
        for idx in range(10):
            if year[k - 2] == table[idx]:
                newDate += str(idx)
                break
    if len(newDate) <> 4:
        return "-1"

    for idx in range(1, 13):
        if month == table[idx]:
            if idx < 10:
                newDate += "0"
            newDate += str(idx)
            break
    
    # some special formats
    if len(newDate) <> 6:
        if month == u"元":
            newDate += "01"
        elif len(month) == 3 and month[0] == u"一":
            for idx in range(10, 13):
                if month[1:] == table[idx]:
                    newDate += str(idx)
                    break
    if len(newDate) <> 6:
        return "-1"

    for idx in range(1, len(table)):
        if day == table[idx]:
            if idx < 10:
                newDate += "0"
            newDate += str(idx)
            break

    # some special formats
    if len(newDate) <> 8:
        if len(day) == 3 and day[0] == u"一":
            for idx in range(10, len(table)):
                if day[1:] == table[idx]:
                    newDate += str(idx)
                    break
    if len(newDate) <> 8:
        return "-1"
    
    return newDate

time1 = clock()
findDate()
time2 = clock()
print "Time used: %.3fs" % (time2 - time1)
