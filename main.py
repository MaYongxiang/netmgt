import mysql.connector
from Function import function
##
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
    cursor_write = conn.cursor()

    cursor_branch.execute('select * from t_branch')
    branch_list = cursor_branch.fetchall()
    cursor_branch.close()

    for branch in branch_list:
        cursor_device.execute('select dev_name,dev_ip,dev_brand,dev_type,dev_local_admin,use_aaa from t_device where dev_branch = %s', [branch[1]])
        dev_list = cursor_device.fetchall()
        devices = []
        t_arp = []
        t_mac = []
        t_int_mac_ip = []

        for dev in dev_list:
            devices.append({
                'dev_name':dev[0],
                'dev_ip':dev[1],
                'dev_brand':dev[2],
                'dev_type':dev[3],
                'dev_local_admin':dev[4],
                'use_aaa':dev[5]
            })


        for device in devices:
            if device['dev_type'] == 'l3_switch' :
                device_int = function.make_device_intstance(**device)
                device_int.connect()
                t_arp += device_int.get_arp_table()
                device_int.disconnect()

            if device['dev_type'] == 'l2_switch' :
                device_int = function.make_device_intstance(**device)
                device_int.connect()
                t_mac += device_int.get_mac_address_table()
                device_int.disconnect()

        for host_mac in t_mac:
            for host_ip in t_arp:
                if host_mac['mac'] == host_ip['mac']:
                    t_int_mac_ip.append({
                        "devint_name":host_mac['hostname']+'_'+host_mac['interface'],
                        'mac': host_mac['mac'],
                        'ip': host_ip['ip'],
                    }
                    )

    for item in t_int_mac_ip :
        cursor_write.execute('insert into ip_mac_cache (devint_name,mac_add,ip_add,time) values (%s,%s,%s,NOW())',[item['devint_name'],item['mac'],item['ip']])

    conn.commit()
    cursor_device.close()
    cursor_write.close()
    conn.close()
