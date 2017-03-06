#!/usr/bin/env python
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
Module name: findLaw

Purpose: use RE to find the law in the cases
         modified to fit mysql

Parameter:
string row - the article to be searched

Return value: [Possibly change in the future]
int total - total number of matches

Author: Ruxuan Zhang

Tester: Zian Zhao

Version: 0.5.2 Beta 10.19.2016
'''

'''
Module name: findLaw

Purpose: use RE to find the law in the cases
         read and write back to mysql

Parameter:
[in] string text - the content of the lawcase
[in] unsigned int id - id of the lawcase
[out] string laws- laws found in the lawcase

Return value: 
int 0 - if succeed
    1 - if error occurs

Author: Zhao Zian

Version: 1.0 10.28.2016
'''

'''
Module name: findLaw

Revision:
    write back to mysql when laws is proper
    record the id for files with no-law found or files rise errors
    record id for files with potiential error (laws longer than 100 charactor)

Parameter:
[in] string text - the content of the lawcase
[in] unsigned int id - id of the lawcase
[out] string laws- laws found in the lawcase
[out] file wrongID - id for unqualified cases

Return value: 
int count_law total laws found in the cases

Author: Zhao Zian

Version: 1.1 11.2.2016
'''


def findLaw():
    count_law = 0
    wrong_id = []
    
    # connect the mysql database
    con = pymysql.connect(user = 'root', passwd = '12345678', db = 'lawcase', charset = 'utf8')
    cursor = con.cursor()
    cursor.execute("SET NAMES utf8")
    cursor.execute("FLUSH QUERY CACHE")

    # find the number of law cases
    cursor.execute('select count(*) from divorce_data')
    tmp = cursor.fetchone()
    num = tmp[0]    # number of law cases


    # Match pattern(s):
    #《xxx法》第xxx条(第xxx款(、第xxx款)*)(、第xxx条(第xxx款(、第xxx款)*))*
    pat = u"((《[^》]+?》第.{1,10}?条(第.{1,10}?款(、第.{1,10}?款)*)*)(、第.{1,10}?条(第.{1,10}?款(、第.{1,10}?款)*)*)*)"

    for i in range(num):
    # for k in range(1):
        # i = 14082
        laws = u""  # variable storing laws found in the case
                    # type unicode

            # get the content of law case i+1
        cursor.execute('select content from divorce_data where id = (%d)' % (i+1))
        tmp = cursor.fetchone()
        text = tmp[0]
            
        mch = list(set(re.findall(pat,text)))
        for rr in mch:
            count_law += 1
            if type(rr) == type(u""):
                laws += (rr + '\n')
            else:
                laws += (rr[0] + '\n')

        # deal with error cases
        if laws == u"":
            wrong_id.append(i+1)
        # write to mysql
        else:
            try:
                cursor.execute("UPDATE divorce_data SET laws = '" + laws + "' WHERE id = '%d'" % (i+1))
            except :
                wrong_id.append(i+1)

    # write the error id to the output file
    wrong_id_out = open('/users/zw/desktop/wrongID.txt', 'w')

    for items in wrong_id:
        wrong_id_out.write(str(items) + ' ')

    wrong_id_out.close()

    print "Process Completed"

    # commit the modification
    # disconnect the database
    con.commit()
    cursor.close()
    con.close()
    
    return count_law

findLaw()



