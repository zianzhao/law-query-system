# -*- coding: utf-8 -*-

import sys
import pymysql
import re

# Set the default code
stdout = sys.stdout
reload(sys)
sys.stdout = stdout
sys.setdefaultencoding('utf-8')

'''
Module name: findYearPlace

Purpose: use RE to find the year and place in the cases (if provided)
         modified to fit mysql

Parameter:
None

Return value:
None

Author: Ruxuan Zhang (reflexit)

Version: 1.0 on 2017/3/6
'''

def findYearPlace():
    abnormal_id = []
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
    patPlace = u"(?<=\\\\)\W{1,10}?(?=\\\\\d)"
    patYear = u"(?<=（)\d\d\d\d(?=）)"

    # just to show progress
    old10000 = 0;
    
    for i in range(num):
        place = u"" # variable storing place found in the case
        year = u""  # variable storing year found in the case
                    # type unicode
        
        # get the path of law case i+1
        cursor.execute('select path from divorce_data where id = (%d)' % (i+1))
        tmp = cursor.fetchone()
        if tmp is None: # if the entry is empty
            continue
        text = tmp[0]
        # print text

        # match place
        mch = list(set(re.findall(patPlace,text)))
        if len(mch) >= 1:
            rr = mch[0];
            if type(rr) == type(u""):
                place += rr
            else:
                place += rr[0]

        # match year
        mch = list(set(re.findall(patYear,text)))
        if len(mch) >= 1:
            rr = mch[0];
            if type(rr) == type(u""):
                year += rr
            else:
                year += rr[0]
                
        # print place, year
        
        # write to mysql
        if place == u"":
            abnormal_id.append(i+1)
            # print "No place in id=%d" % (i+1)
            try:
                cursor.execute("UPDATE divorce_data SET place = null WHERE id = '%d'" % (i+1))
            except :
                wrong_id.append(i+1)
        else:
            try:
                cursor.execute("UPDATE divorce_data SET place = '" + place + "' WHERE id = '%d'" % (i+1))
            except :
                wrong_id.append(i+1)
        
        if year == u"":
            abnormal_id.append(i+1)
            # print "No year in id=%d" % (i+1)
            try:
                cursor.execute("UPDATE divorce_data SET year = null WHERE id = '%d'" % (i+1))
            except :
                wrong_id.append(i+1)
        else:
            try:
                cursor.execute("UPDATE divorce_data SET year = '" + year + "' WHERE id = '%d'" % (i+1))
            except :
                wrong_id.append(i+1)

        # just to show progress
        if i / 10000 <> old10000:
            print "%d completed" % i
            old10000 += 1

    # for-loop end

    # write the error id to the output file
    wrong_id_out = open('wrongID.txt', 'w')
    abnormal_id_out = open('abnormalID.txt', 'w')

    for items in wrong_id:
        wrong_id_out.write(str(items) + ' ')
    for items in abnormal_id:
        abnormal_id_out.write(str(items) + ' ')

    wrong_id_out.close()
    abnormal_id_out.close()
    
    print "Process Completed"

    # commit the modification
    # disconnect the database
    con.commit()
    cursor.close()
    con.close()

findYearPlace()
