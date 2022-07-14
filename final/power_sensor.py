
import datetime

from pyemvue.pyemvue import PyEmVue
from pyemvue.enums import Scale, Unit

def get_power(usage_dict, info, depth=0):
    for gid, device in usage_dict.items():
        for channelnum, channel in device.channels.items():
            name = channel.name
            if name == 'Main':
                name = info[gid].device_name
    return channel.usage*1000

def power():

    vue = PyEmVue()
    vue.login(username='diogvargas@gmail.com', password='Sancochos1')

    devices = vue.get_devices()
    device_gids = []
    info = {}
    for device in devices:
        if not device.device_gid in device_gids:
            device_gids.append(device.device_gid)
            info[device.device_gid] = device

    device_usage_dict = vue.get_device_list_usage(deviceGids=device_gids, instant = datetime.datetime.now(datetime.timezone.utc), scale=Scale.MINUTE.value, unit=Unit.KWH.value)
    
    return get_power(device_usage_dict,info) * 60 