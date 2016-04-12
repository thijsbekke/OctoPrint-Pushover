# coding=utf-8
from __future__ import absolute_import
import os

import octoprint.plugin
from octoprint.events import Events

import httplib, urllib, json

__author__ = "Thijs Bekke <thijsbekke@gmail.com>"
__license__ = 'GNU Affero General Public License http://www.gnu.org/licenses/agpl.html'
__copyright__ = "Released under terms of the AGPLv3 License"
__plugin_name__ = "Pushover"


class PushoverPlugin(octoprint.plugin.EventHandlerPlugin,
                     octoprint.plugin.SettingsPlugin,
                     octoprint.plugin.StartupPlugin,
                     octoprint.plugin.TemplatePlugin):

	api_token = ""
	user_key = ""

	def _validate_pushover(self, api_token, user_key):
		if api_token and user_key:
			self.api_token = api_token
			self.user_key = user_key

			try:
				self._conn = httplib.HTTPSConnection("api.pushover.net:443")
				self._conn.request("POST", "/1/users/validate.json",
					self._create_payload({}), {"Content-type": "application/x-www-form-urlencoded"})
				HTTPResponse = self._conn.getresponse()

				response = json.loads(HTTPResponse.read())

				if HTTPResponse.getheader('status').startswith('400'):
					self._logger.exception("Error while instantiating Pushover, %s" % response['errors'])
					return False
				elif not HTTPResponse.getheader('status').startswith('200'):
					self._logger.exception("Error while instantiating Pushover, header %s" % HTTPResponse.getheader('status'))
					return False

				if response['status'] == 1:
					self._logger.info("Connected to Pushover")
					return True

			except Exception, e:
				self._logger.exception("Error while instantiating Pushover: %s" % str(e))
				return False

		return False

	def on_after_startup(self):
		self._validate_pushover(self._settings.get(["api_token"]), self._settings.get(["user_key"]))

	def on_settings_save(self, data):
		octoprint.plugin.SettingsPlugin.on_settings_save(self, data)

		import threading
		thread = threading.Thread(target=self._validate_pushover, args=(
			self._settings.get(["api_token"]), self._settings.get(["user_key"]),))
		thread.daemon = True
		thread.start()

	def get_settings_defaults(self):
		return dict(
			api_token=None,
			user_key=None,
			printDone=dict(
				title="Print job finished ",
				body="{file} finished printing in {elapsed_time}"
			)
		)

	def get_template_configs(self):
		return [
			dict(type="settings", name="Pushover", custom_bindings=False)
		]

	# ~~ EventHandlerPlugin

	def on_event(self, event, payload):
		if event == Events.PRINT_DONE:
			file = os.path.basename(payload["file"])
			elapsed_time_in_seconds = payload["time"]

			import datetime
			import octoprint.util
			elapsed_time = octoprint.util.get_formatted_timedelta(datetime.timedelta(seconds=elapsed_time_in_seconds))

			title = self._settings.get(["printDone", "title"]).format(**locals())
			body = self._settings.get(["printDone", "body"]).format(**locals())

			self._send_note(title + body)

	def _create_payload(self, create_payload):
		x = {
			"token": self.api_token,
			"user": self.user_key
		}

		new_payload = x.copy()
		new_payload.update(create_payload)

		return urllib.urlencode(new_payload)

	def _send_note(self, message):
		if not self._conn:
			return
		try:
			self._conn = httplib.HTTPSConnection("api.pushover.net:443")
			self._conn.request("POST", "/1/messages.json",
				self._create_payload({
					"message": message,
				}), {"Content-type": "application/x-www-form-urlencoded"})
			self._conn.getresponse()

		except Exception, e:
			self._logger.exception("Error while instantiating Pushover: %s" % str(e))
			return False
		return True

	##~~ Softwareupdate hook
	def get_update_information(self):
		return dict(
			octobullet=dict(
				displayName="Pushover Plugin",
				displayVersion=self._plugin_version,

				# version check: github repository
				type="github_release",
				user="thijsbekke",
				repo="OctoPrint-Pushover",
				current=self._plugin_version,

				# update method: pip
				pip="https://github.com/thijsbekke/OctoPrint-Pushover/archive/{target_version}.zip"
			)
		)


__plugin_name__ = "Pushover"
def __plugin_load__():
	global __plugin_implementation__
	__plugin_implementation__ = PushoverPlugin()

	global __plugin_hooks__
	__plugin_hooks__ = {
		"octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information
	}

