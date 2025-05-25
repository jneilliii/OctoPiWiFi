from flask import Flask, render_template, request
import subprocess
import os
import os.path

app = Flask(__name__)
app.debug = True


@app.route('/')
def index():
    wifi_ap_array = scan_wifi_networks()
    config_hash = config_file_hash()

    return render_template('app.html', wifi_ap_array = wifi_ap_array, config_hash = config_hash)


@app.route('/manual_ssid_entry')
def manual_ssid_entry():
    return render_template('manual_ssid_entry.html')


@app.route('/wpa_settings')
def wpa_settings():
    config_hash = config_file_hash()
    return render_template('wpa_settings.html', wpa_enabled = config_hash['wpa_enabled'], wpa_key = config_hash['wpa_key'])


@app.route('/save_credentials', methods = ['GET', 'POST'])
def save_credentials():
    ssid = request.form['ssid']
    wifi_key = request.form['wifi_key']

    if ssid == 'AP mode':
        set_ap_host_mode()
    else:
        create_nm_connection(ssid, wifi_key)
        set_ap_client_mode(ssid)

    return render_template('save_credentials.html', ssid = ssid)


@app.route('/save_wpa_credentials', methods = ['GET', 'POST'])
def save_wpa_credentials():
    config_hash = config_file_hash()
    wpa_enabled = request.form.get('wpa_enabled')
    wpa_key = request.form['wpa_key']

    if str(wpa_enabled) == '1':
        update_wpa(1, wpa_key)
    else:
        update_wpa(0, wpa_key)

    config_hash = config_file_hash()
    return render_template('save_wpa_credentials.html', wpa_enabled = config_hash['wpa_enabled'], wpa_key = config_hash['wpa_key'])




######## FUNCTIONS ##########

def scan_wifi_networks():
    iwlist_raw = subprocess.Popen(['iwlist', 'scan'], stdout=subprocess.PIPE)
    ap_list, err = iwlist_raw.communicate()
    ap_array = []

    for line in ap_list.decode('utf-8').rsplit('\n'):
        if 'ESSID' in line:
            ap_ssid = line[27:-1]
            if ap_ssid != '':
                ap_array.append(ap_ssid)

    ap_array.append("AP mode")

    return ap_array

def create_nm_connection(ssid, wifi_key):
    if os.path.exists('/etc/NetworkManager/system-connections/' + ssid + '.nmconnection'):
      os.system('nmcli con delete ' + ssid)

    os.system('nmcli con add type wifi ifname wlan0 mode infrastructure con-name ' + ssid + ' ssid ' + ssid + ' autoconnect true')

    if wifi_key == '':
        os.system('nmcli con modify ' + ssid + ' wifi-sec.key-mgmt none')
    else:
        os.system('nmcli con modify ' + ssid + ' wifi-sec.key-mgmt wpa-psk')
        os.system('nmcli con modify ' + ssid + ' wifi-sec.psk ' + wifi_key)

def set_ap_host_mode():
    os.system('nmcli con up OctoPiWiFi')

def set_ap_client_mode(ssid):
    os.system('nmcli con up ' + ssid)

def update_wpa(wpa_enabled, wpa_key):
    if wpa_enabled:
        os.system('nmcli con modify OctoPiWiFi wifi-sec.key-mgmt wpa-psk')
        os.system('nmcli con modify OctoPiWiFi wifi-sec.psk "' + wpa_key + '"')
    else:
        os.system('nmcli con modify OctoPiWiFi wifi-sec.key-mgmt none')


def config_file_hash():
    config_file = open('/etc/raspiwifi/raspiwifi.conf')
    config_hash = {}

    for line in config_file:
        line_key = line.split("=")[0]
        line_value = line.split("=")[1].rstrip()
        config_hash[line_key] = line_value

    return config_hash


if __name__ == '__main__':
    config_hash = config_file_hash()

    if config_hash['ssl_enabled'] == "1":
        app.run(host = '0.0.0.0', port = int(config_hash['server_port']), ssl_context='adhoc')
    else:
        app.run(host = '0.0.0.0', port = int(config_hash['server_port']))
