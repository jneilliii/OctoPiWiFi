# coding=utf-8
from __future__ import absolute_import

import octoprint.plugin
import flask


class RaspiWiFi(octoprint.plugin.BlueprintPlugin, octoprint.plugin.RestartNeedingPlugin):
    @octoprint.plugin.BlueprintPlugin.route("/can_reboot", methods=["GET"])
    def can_reboot_route(self):
        can_reboot = self._printer.get_state_id() not in ["PRINTING", "PAUSED", "PAUSING"]
        self._logger.debug("Is it ok to reboot? {}".format(can_reboot))
        return flask.jsonify({"can_reboot": can_reboot})

    def is_blueprint_protected(self):
        return False


__plugin_name__ = "RaspiWiFi"
__plugin_description__ = "Verify ability to reboot pi based on printer status."
__plugin_author__ = "jneilliii"
__plugin_license__ = "MIT"
__plugin_pythoncompat__ = ">=3,<4"
__plugin_version__ = "0.1.0"
__plugin_implementation__ = RaspiWiFi()
