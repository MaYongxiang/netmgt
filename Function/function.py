from Huawei.device import *
import re


def _get_password(**device):
    """
    input {'dev_name':'name' ,'dev_ip':'ip address','dev_brand':'Huawei or Cisco','dev_type':'type','dev_local_admin'='name','use_aaa':'o or 1'}

    """
    user_pass = {}
    if device['use_aaa'] == 1 :
        user_pass = {'username':'checklist','password':'checklist','super':'checklist','enable':'checklist'}
    elif device['use_aaa']  == 0 and device['dev_brand'] == 'huawei' and (device['dev_type'] == 'l2_switch' or 'l3_switch'):
        user_pass = {'username':device['dev_local_admin'],'password':'wlkjhj2016','super':'huaweijhj2016'}
    else:
        user_pass = {'username': 'checklist', 'password': 'checklist', 'super': 'checklist', 'enable': 'checklist'}

    return user_pass



def make_device_intstance(**device):
    user_pass = _get_password(**device)
    intstance = None
    if device['dev_brand'] == 'huawei' and (device['dev_type'] == 'l2_switch' or 'l3_switch'):
        if user_pass is not None:
            intstance = HuaweiSwitch(host=device['dev_ip'], password=user_pass['password'], username=user_pass['username'], super_password=user_pass['super'])
    return intstance


def change_int_name(str):
    re_text = '^(\w+)(\d+.+)'
    name = re.match(re_text,str)
    if name == None:
        return str
    elif name.group(1) == "GE" :
        return "GigabitEthernet"+name.group(2)
    else:
        return str