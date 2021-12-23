import time
import sys
import os
import reset_lib
import requests

no_conn_counter = 0
consecutive_active_reports = 0
config_hash = reset_lib.config_file_hash()

# If auto_config is set to 0 in /etc/raspiwifi/raspiwifi.conf exit this script
if config_hash['auto_config'] == "0":
    sys.exit()
else:
    # Main connection monitoring loop at 10 second interval
    while True:
        time.sleep(10)

        # If iwconfig report no association with an AP add 10 to the "No
        # Connection Couter"
        if reset_lib.is_wifi_active() == False:
            no_conn_counter += 10
            consecutive_active_reports = 0
        # If iwconfig report association with an AP add 1 to the
        # consecutive_active_reports counter and 10 to the no_conn_counter
        else:
            consecutive_active_reports += 1
            no_conn_counter += 10
            # Since wpa_supplicant seems to breifly associate with an AP for
            # 6-8 seconds to check the network key the below will reset the
            # no_conn_counter to 0 only if two 10 second checks have come up active.
            if consecutive_active_reports >= 2:
                no_conn_counter = 0
                consecutive_active_reports = 0

        # If the number of seconds not associated with an AP is greater or
        # equal to the auto_config_delay specified in the /etc/raspiwifi/raspiwifi.conf
        # and octoprint is not currently printing trigger a reset into AP Host
        # (Configuration) mode.
        if no_conn_counter >= int(config_hash['auto_config_delay']):
            check_reboot = requests.get("http://localhost:5000/plugin/raspiwifi/can_reboot")
            if check_reboot.json().get("can_reboot", False) is True:
                reset_lib.reset_to_host_mode()
            else:
                no_conn_counter = 0
