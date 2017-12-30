import mysql.connector

db_ip = '192.168.11.3'
db_user = 'mayx'
db_pass = 'bianfuxia'


if __name__ == '__main__':
    conn = mysql.connector.connect(user=db_user ,host = db_ip , password = db_pass , database = 'netmgt' , use_unicode = True)
    cursor = conn.cursor()
    cursor.execute('select * from t_branch')
    values = cursor.fetchall()
    cursor.close()
    conn.close()

    for item in values:
        print "inx_num: %s , build_name: %s , location: %s" % (item[0],item[1],item[2])
    print 'DONE!'