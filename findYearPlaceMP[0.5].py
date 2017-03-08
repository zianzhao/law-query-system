# -*- coding: utf-8 -*-

import sys
import pymysql
import re
import multiprocessing  # for multiprocess
from time import clock  # for timing

# Set the default code
stdout = sys.stdout
reload(sys)
sys.stdout = stdout
sys.setdefaultencoding('utf-8')

'''
Module name: findYearPlaceMP

Purpose: use RE to find the year and place in the cases (if provided)
         *** use multiple processes to accelerate ***
         *** BETA version, locks not implemented ***

Parameter:
None

Return value:
None

Author: Ruxuan Zhang (reflexit)

Version: 0.5 on 2017/3/8
'''

def findYearPlaceMP():
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

    if __name__ == '__main__':
        # create processes
        time1 = clock()
        cpuNum = multiprocessing.cpu_count()
        pool = multiprocessing.Pool(processes = cpuNum)
        interval = num / cpuNum
        for i in range(cpuNum - 1):
            low = interval * i
            high = interval * (i + 1)
            pool.apply_async(worker, (low, high))

        # deal with the last process
        pool.apply_async(worker, (interval * (cpuNum - 1), num))

        # wait processes to join
        pool.close()
        pool.join()
        time2 = clock()
        print "All child processes done"
        print "Time used: %.3fs" % (time2 - time1)
    
    # commit the modification
    # disconnect the database
    con.commit()
    cursor.close()
    con.close()

def worker(low, high):
    # connect the mysql database
    con = pymysql.connect(user = 'root', passwd = '12345678', db = 'lawcase', charset = 'utf8')
    cursor = con.cursor()
    cursor.execute("SET NAMES utf8")
    cursor.execute("FLUSH QUERY CACHE")

    # Match patterns:
    patPlace = u"(?<=\\\\)\W{1,10}?(?=\\\\\d)"
    patYear = u"(?<=（)\d\d\d\d(?=）)"
    
    for i in range(low, high):
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
            rr = mch[0]
            if type(rr) == type(u""):
                place += rr
            else:
                place += rr[0]

        # match year
        mch = list(set(re.findall(patYear,text)))
        if len(mch) >= 1:
            rr = mch[0]
            if type(rr) == type(u""):
                year += rr
            else:
                year += rr[0]
                
        # print place, year
        
        # write to mysql
        if place == u"":
            # print "No place in id=%d" % (i+1)
            try:
                cursor.execute("UPDATE divorce_data SET place = null WHERE id = '%d'" % (i+1))
            except:
                print "ERROR in id = %d" % (i + 1)
        else:
            try:
                cursor.execute("UPDATE divorce_data SET place = '" + place + "' WHERE id = '%d'" % (i+1))
            except:
                print "ERROR in id = %d" % (i + 1)
        
        if year == u"":
            # print "No year in id=%d" % (i+1)
            try:
                cursor.execute("UPDATE divorce_data SET year = null WHERE id = '%d'" % (i+1))
            except:
                print "ERROR in id = %d" % (i + 1)
        else:
            try:
                cursor.execute("UPDATE divorce_data SET year = '" + year + "' WHERE id = '%d'" % (i+1))
            except:
                print "ERROR in id = %d" % (i + 1)
                
    # for-loop end

    print "Child process (%d, %d) completed" % (low, high - 1)
    
    # commit the modification
    # disconnect the database
    con.commit()
    cursor.close()
    con.close()

findYearPlaceMP()
