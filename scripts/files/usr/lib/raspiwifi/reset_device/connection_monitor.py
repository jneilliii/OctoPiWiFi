import time
import sys
import os
import reset_lib
import logging

no_conn_counter = 0
consecutive_active_reports = 0
config_hash = reset_lib.config_file_hash()
logger = logging.getLogger('raspiwifi')
f_handler = logging.FileHandler('raspiwifi.log')
f_handler.setLevel(logging.DEBUG)
f_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
f_handler.setFormatter(f_format)
logger.addHandler(f_handler)

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
            printer_status = subprocess.check_output(['/home/pi/oprint/bin/octoprint', 'client', 'get', '/api/printer?exclude=temperature,sd']).decode('utf-8').split('\n')[1]
            printer_status_match = re.search(r'"text":"(.+)"', printer_status)
            logger.debug(printer_status)
            logger.debug(printer_status_match)
            if printer_status_match:
                printer_state = printer_status_match.group(1)
            else:
                printer_state = "unknown"
            logger.debug(printer_state)
            # if printer_state not in ["Printing", "Paused", "Pausing"]:
            reset_lib.reset_to_host_mode()
