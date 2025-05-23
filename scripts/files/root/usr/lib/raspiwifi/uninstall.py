import os
import sys

print()
print()
print("#################################")
print("##### RaspiWiFi Uninstaller #####")
print("#################################")
print()
print()
uninstall_answer = input("Would you like to uninstall RaspiWiFi? [y/N]: ")
print()

if (uninstall_answer.lower() == "y"):
    print('Uninstalling RaspiWiFi from your system...')

    os.system('nmcli con delete wifi-hotspot')

    os.system('rm -rf /etc/raspiwifi')
    os.system('rm -rf /usr/lib/raspiwifi')
    os.system('rm -rf /etc/cron.raspiwifi')
    os.system('sed -i \'s/# RaspiWiFi Startup//\' /etc/crontab')
    os.system('sed -i \'s/@reboot root run-parts \/etc\/cron.raspiwifi\///\' /etc/crontab')
    
# TODO(kem): re-enable/activate dnsmasq?

    print()
    print()
    reboot_answer = input('Uninstallation is complete. Would you like to reboot the system now?: ')

    if(reboot_answer.lower() == "y"):
        os.system('reboot')
else:
    print()
    print('No changes made. Exiting unistaller...')
