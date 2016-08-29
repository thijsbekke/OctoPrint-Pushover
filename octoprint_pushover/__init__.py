# coding=utf-8
from __future__ import absolute_import
import os
import sys

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
	user_key = ""
	api_url = "api.pushover.net:443"

	def validate_pushover(self, user_key):
		if not user_key:
			self._logger.exception("No user key provided")
			return False

		self.user_key = user_key
		try:
			HTTPResponse = self.post("users/validate.json", self.create_payload({}))

			if not HTTPResponse:
				self._logger.exception("HTTPResponse is false")

			status = HTTPResponse.getheader('status')
			if status is not None and status.startswith('40'):
				self._logger.exception("Error while instantiating Pushover, header %s" % HTTPResponse.getheader("status"))
				return False
			elif status is not None and not status.startswith('200'):
				self._logger.exception(
					"error while instantiating Pushover, header %s" % HTTPResponse.getheader("status"))
				return False

			response = json.loads(HTTPResponse.read())

			if response["status"] == 1:
				self._logger.info("Connected to Pushover")
				return True

		except Exception, e:
			self._logger.exception("error while instantiating Pushover: %s" % str(e))

		return False

	def PrintDone(self, payload):
		file = os.path.basename(payload["file"])
		elapsed_time_in_seconds = payload["time"]

		import datetime
		import octoprint.util
		elapsed_time = octoprint.util.get_formatted_timedelta(datetime.timedelta(seconds=elapsed_time_in_seconds))

		# Create the message
		return self._settings.get(["events", "PrintDone", "message"]).format(**locals())

	def PrintStarted(self, payload):
		file = os.path.basename(payload["file"])
		return self._settings.get(["events", "PrintStarted", "message"]).format(**locals())

	def PrintFailed(self, payload):
		file = os.path.basename(payload["file"])
		return self._settings.get(["events", "PrintFailed", "message"]).format(**locals())

	def Error(self, payload):
		error = payload["error"]
		return self._settings.get(["events", "Error", "message"]).format(**locals())


	def on_event(self, event, payload):
		# Does the event exists in the settings ?
		if not event in self.get_settings_defaults()["events"]:
			return False

		# Only continue when there is a priority
		priority = self._settings.get(["events", event, "priority"])
		if priority == "":
			return

		self._logger.info("Event triggered: %s " % str(event))

		# It's easier to ask forgiveness than to ask permission.
		try:
			payload["message"] = getattr(self, event)(payload)
			# Method exists, and was used.
		except AttributeError:
			self._logger.info("not found")
			# By default the message is simple and does not need any formatting
			payload["message"] = self._settings.get(["events", event, "message"])

		# By default, messages have normal priority (a priority of 0).
		# We do not support the Emergency Priority (2) because there is no way of canceling it here,
		if priority:
			payload["priority"] = priority

		self.event_message(payload)

	def event_message(self, payload):
		# Create an url, if the fqdn is not correct you can manually set it at your config.yaml
		url = self._settings.get(["url"])
		if (url):
			payload["url"] = url
		else:
			# Create an url
			import socket
			payload["url"] = "http://%s" % socket.getfqdn()

		# If no sound parameter is specified, the user"s default tone will play.
		# If the user has not chosen a custom sound, the standard Pushover sound will play.
		sound = self._settings.get(["sound"])
		if sound:
			payload["sound"] = sound

		self.post("messages.json", self.create_payload(payload))

	def on_after_startup(self):
		self.validate_pushover(self._settings.get(["user_key"]))

	def on_settings_save(self, data):
		octoprint.plugin.SettingsPlugin.on_settings_save(self, data)

		import threading
		thread = threading.Thread(target=self.validate_pushover, args=(self._settings.get(["user_key"]),))
		thread.daemon = True
		thread.start()

	def create_payload(self, create_payload):
		x = {
			"token": self._settings.get(["api_token"]),
			"user": self.user_key
		}

		new_payload = x.copy()
		new_payload.update(create_payload)

		return urllib.urlencode(new_payload)

	def post(self, uri, payload):
		try:
			conn = httplib.HTTPSConnection(self.api_url)
			conn.request("POST", "/1/" + uri, payload, {"Content-type": "application/x-www-form-urlencoded"})
			return conn.getresponse()
		except Exception, e:
			self._logger.exception("error while instantiating Pushover: %s" % str(e))
			return False

	def get(self, uri):
		try:
			conn = httplib.HTTPSConnection(self.api_url)
			conn.request("GET", "/1/" + uri + "?token=" + self._settings.get(["api_token"]))

			return conn.getresponse()

		except Exception, e:
			self._logger.exception("error while getting data from Pushover: %s" % str(e))
			return False

	def get_settings_defaults(self):
		return dict(
			api_token="aY8c1fWze8A2USNavDeZLDEERCwVNn",
			user_key=None,
			sound=None,
			events = dict(
				PrintStarted=dict(
					name="Print started",
					message="Print job started: {file}",
					priority=0
				),
				PrintDone=dict(
					name="Print done",
					message="Print job finished: {file}, finished printing in {elapsed_time}",
					priority = 0
				),
				PrintFailed=dict(
					name="Print failed",
					message="Print job failed: {file}",
					priority=0
				),
				Error=dict(
					name="Error",
					message="Error: {error}",
					priority=0
				),
				PowerOff=dict(
					name="GCode event power off",
					message="The GCODE has turned on the printer power via M81",
					priority=0
				),
				Waiting=dict(
					name="GCode event waiting",
					message="The print is paused due to a gcode wait command",
					priority=0
				),
				Alert=dict(
					name="GCode event alert",
					message="The GCODE has issued a user alert (beep) via M300",
					priority=0
				),
				Home=dict(
					name="GCode event home",
					message="The head has gone home via G28",
					priority=0
				),
				EStop=dict(
					name="GCode event estop",
					message="The GCODE has issued a panic stop via M112",
					priority=0
				),
				MovieDone=dict(
					name="Movie done",
					message="The timelapse movie is completed",
					priority=0
				),
				MovieFailed=dict(
					name="Movie failed",
					message="There was an error while rendering the timelapse movie.",
					priority=0
				),
				SlicingStarted=dict(
					name="Slicing started",
					message="The slicing has been started.",
					priority=0
				),
				SlicingDone=dict(
					name="Slicing done",
					message="The slicing is completed.",
					priority=0
				),
				SlicingFailed=dict(
					name="Slicing failed",
					message="The slicing is failed.",
					priority=0
				)
			)
		)

	def get_template_vars(self):
		return dict(
			sounds=self.get_sounds(),
			# Makes an array containing the event key and a human readable name
			events=dict((key, value["name"]) for key, value in self.get_settings_defaults()["events"].iteritems())
		)

	def get_sounds(self):
		# Make a call too the sounds API
		HTTPResponse = self.get("sounds.json")

		if not HTTPResponse:
			return

		return json.loads(HTTPResponse.read())["sounds"]

	def get_template_configs(self):
		return [
			dict(type="settings", name="Pushover", custom_bindings=False)
		]


	def get_update_information(self):
		return dict(
			pushover=dict(
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
