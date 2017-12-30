import Huawei.device as deivce


l3_s_ip = '10.242.255.51'
aaa_user = 'checklist'
aaa_passwd = 'checklist'
aaa_super_pass = 'checklist'

l2_s_ip = '10.242.143.22'
l2_user = 'localadmin'
l2_pass = 'wlkjhj2016'
l2_super = 'huaweijhj2016'

t_int_mac_ip = []

if __name__ == '__main__':
    l3_s = deivce.HuaweiSwitch(host = l3_s_ip, password = aaa_passwd, username = aaa_user, super_password = aaa_super_pass)
    l3_s.connect()
    t_arp = l3_s.get_arp_table()
    l3_s.disconnect()
    #print t_arp

    l2_s = deivce.HuaweiSwitch(host = l2_s_ip, password = l2_pass, username = l2_user, super_password = l2_super)
    l2_s.connect()
    t_mac = l2_s.get_mac_address_table()
    l2_s.disconnect()
    #print t_mac

    for host_mac in t_mac :
        for host_ip in t_arp:
            if host_mac['mac'] == host_ip['mac']:
                t_int_mac_ip.append({
                    'interface':host_mac['interface'],
                    'mac':host_mac['mac'],
                    'ip':host_ip['ip'],
                }
                )

    for item in t_int_mac_ip :
        print item






