from Huawei.device import HuaweiSwitch
import mysql.connector

db_ip = '192.168.11.3'
db_user = 'mayx'
db_pass = 'bianfuxia'

aaa_user = 'checklist'
aaa_passwd = 'checklist'
aaa_super_pass = 'checklist'

l2_pass = 'wlkjhj2016'
l2_super = 'huaweijhj2016'

t_int_mac_ip = []

if __name__ == '__main__':

    conn = mysql.connector.connect(user=db_user, host=db_ip, password=db_pass, database='netmgt', use_unicode=True)
    cursor_branch = conn.cursor()
    cursor_device = conn.cursor()
    cursor_branch.execute('select * from t_branch')
    branch_list = cursor_branch.fetchall()
    cursor_branch.close()

    for branch in branch_list:
        cursor_device.execute('select dev_name,dev_ip,dev_brand,dev_type,dev_local_admin,use_aaa from t_device where dev_branch = %s', [branch[1]])
        dev_list = cursor_device.fetchall()

        for device in dev_list:
            if device[2] == 'huawei' and device[5] == 1 :



    cursor_device.close()
    conn.close()
