import os
import re
import time
import subprocess
import reset_lib

counter = 0
cpuinfo = subprocess.check_output(['cat', '/proc/cpuinfo']).decode('utf-8')

serial_match = re.search(r"Serial\s+:\s(\S+)$", cpuinfo, re.MULTILINE)
if serial_match:
    serial_last_four = serial_match.group(1)[-4:]
else:
    serial_last_four = '0000'

serial_last_four = subprocess.check_output(['cat', '/proc/cpuinfo'])[-5:-1].decode('utf-8')
config_hash = reset_lib.config_file_hash()
ssid_prefix = config_hash['ssid_prefix']
reboot_required = False


reboot_required = reset_lib.wpa_check_activate(config_hash['wpa_enabled'], config_hash['wpa_key'])

reboot_required = reset_lib.update_ssid(ssid_prefix, serial_last_four)

if reboot_required == True:
    os.system('reboot')

