# coding=utf-8
from __future__ import absolute_import

import os
import PIL
import StringIO
import flask
import httplib
import json
import octoprint.plugin
import octoprint.plugin
import requests
import sys
import datetime
import urllib
import octoprint.util
from PIL import Image
from flask.ext.login import current_user
from octoprint.events import Events

__author__ = "Thijs Bekke <thijsbekke@gmail.com>"
__license__ = 'GNU Affero General Public License http://www.gnu.org/licenses/agpl.html'
__copyright__ = "Released under terms of the AGPLv3 License"
__plugin_name__ = "Pushover"

class SkipEvent(Exception):
	pass

class PushoverPlugin(octoprint.plugin.EventHandlerPlugin,
					 octoprint.plugin.SettingsPlugin,
					 octoprint.plugin.StartupPlugin,
					 octoprint.plugin.SimpleApiPlugin,
					 octoprint.plugin.TemplatePlugin,
					 octoprint.plugin.AssetPlugin,
					 octoprint.plugin.OctoPrintPlugin):
	api_url = "https://api.pushover.net/1"
	m70_cmd = ""
	printing = False
	startTime = 0
	lastMinute = 0

	def get_assets(self):
		return {
			"js": ["js/pushover.js"]
		}

	def get_api_commands(self):
		return dict(
			test=["api_key", "user_key"]
		)

	def on_api_command(self, command, data):
		if command == "test":

			if not data["api_key"]:
				data["api_key"] = self.get_token()

			# When we are testing the token, create a test notification
			payload = {
				"message": "pewpewpew!! OctoPrint works.",
				"token": data["api_key"],
				"user": data["user_key"],
			}

			# If there is a sound, include it in the payload
			if "sound" in data:
				payload["sound"] = data["sound"]

			if "image" in data:
				payload["image"] = data["image"]

			# Validate the user key and send a message
			try:
				self.validate_pushover(data["api_key"], data["user_key"])
				self.event_message(payload)
				return flask.jsonify(dict(success=True))
			except Exception as e:
				return flask.jsonify(dict(success=False, msg=str(e.message)))
		return flask.make_response("Unknown command", 400)

	def validate_pushover(self, api_key, user_key):
		"""
		Validate settings, this will do a post request to users/validate.json
		:param user_key: 
		:return: 
		"""
		if not api_key:
			raise ValueError("No api key provided")
		if not user_key:
			raise ValueError("No user key provided")

		try:
			r = requests.post(self.api_url + "/users/validate.json", data={
				"token": api_key,
				"user": user_key,
			})

			if r is not None and not r.status_code == 200:
				raise ValueError("error while instantiating Pushover, header %s" % r.status_code)

			response = json.loads(r.content)

			if response["status"] == 1:
				self._logger.info("Connected to Pushover")

				return True

		except Exception, e:
			raise ValueError("error while instantiating Pushover: %s" % str(e))

		return False

	def image(self):
		"""
		Create an image by getting an image form the setting webcam-snapshot. 
		Transpose this image according the settings and returns it 
		:return: 
		"""
		snapshot_url = self._settings.global_get(["webcam", "snapshot"])
		if not snapshot_url:
			return None

		self._logger.debug("Snapshot URL: %s " % str(snapshot_url))
		image = requests.get(snapshot_url, stream=True).content

		hflip = self._settings.global_get(["webcam", "flipH"])
		vflip = self._settings.global_get(["webcam", "flipV"])
		rotate = self._settings.global_get(["webcam", "rotate90"])

		if hflip or vflip or rotate:
			# https://www.blog.pythonlibrary.org/2017/10/05/how-to-rotate-mirror-photos-with-python/
			image_obj = Image.open(StringIO.StringIO(image))
			if hflip:
				image_obj = image_obj.transpose(Image.FLIP_LEFT_RIGHT)
			if vflip:
				image_obj = image_obj.transpose(Image.FLIP_TOP_BOTTOM)
			if rotate:
				image_obj = image_obj.rotate(90)

			# https://stackoverflow.com/questions/646286/python-pil-how-to-write-png-image-to-string/5504072
			output = StringIO.StringIO()
			image_obj.save(output, format="JPEG")
			image = output.getvalue()
			output.close()
		return image

	def getMinsSinceStarted(self):
		return int(round((datetime.datetime.now() - self.startTime).total_seconds() / 60, 0))

	def checkSchedule(self):
		"""
			Check the scheduler
			Send a notification
		"""
		scheduleMod = self._settings.get(["scheduleMod"])


		if self.printing and scheduleMod and self.lastMinute % int(scheduleMod) == 0:
			self.event_message({
				"message": 'Scheduled notification'
			})

	def sent_gcode(self, comm_instance, phase, cmd, cmd_type, gcode, *args, **kwargs):
		"""
		M70 Gcode commands are used for sending a text when print is paused
		:param comm_instance: 
		:param phase: 
		:param cmd: 
		:param cmd_type: 
		:param gcode: 
		:param args: 
		:param kwargs: 
		:return: 
		"""
		if gcode and gcode != "G1":
			mss = self.getMinsSinceStarted()

			if self.lastMinute != mss:
				self.lastMinute = mss
				self.checkSchedule()
		
		
		if gcode and gcode == "M70":
			self.m70_cmd = cmd[3:]

	# Start with event handling: http://docs.octoprint.org/en/master/events/index.html

	def PrintDone(self, payload):
		"""
		When the print is done, enhance the payload with the filename and the elased time and returns it 
		:param payload: 
		:return: 
		"""
		self.printing = False
		self.lastMinute = 0
		file = os.path.basename(payload["name"])
		elapsed_time_in_seconds = payload["time"]

		elapsed_time = octoprint.util.get_formatted_timedelta(datetime.timedelta(seconds=elapsed_time_in_seconds))

		# Create the message
		return self._settings.get(["events", "PrintDone", "message"]).format(**locals())

	def PrintFailed(self, payload):
		"""
		When the print is failed, enhance the payload with the filename and returns it 
		:param payload: 
		:return: 
		"""
		self.printing = False
		if "name" in payload:
			file = os.path.basename(payload["name"])
		return self._settings.get(["events", "PrintFailed", "message"]).format(**locals())

	def PrintPaused(self, payload):
		"""
		When the print is paused check if there is a m70 command, and replace that in the message.
		:param payload: 
		:return: 
		"""
		m70_cmd = ""
		if (self.m70_cmd != ""):
			m70_cmd = self.m70_cmd

		return self._settings.get(["events", "PrintPaused", "message"]).format(**locals())

	def Waiting(self, payload):
		"""
		Alias for PrintPaused
		:param payload: 
		:return: 
		"""
		return self.PrintPaused(payload)

	def PrintStarted(self, payload):
		"""
		Reset value's
		:param payload: 
		:return: 
		"""
		self.printing = True
		self.startTime = datetime.datetime.now()
		self.m70_cmd = ""

	def Error(self, payload):
		"""
		Only continue when the current state is printing
		:param payload: 
		:return: 
		"""
		if(self.printing):
			error = payload["error"]
			return self._settings.get(["events", "Error", "message"]).format(**locals())
		raise SkipEvent()


	def on_event(self, event, payload):

		if payload is None:
			payload = {}

		# It's easier to ask forgiveness than to ask permission.
		try:
			# Method exists, and was used.
			payload["message"] = getattr(self, event)(payload)

			self._logger.info("Event triggered: %s " % str(event))
		except AttributeError:
			# By default the message is simple and does not need any formatting
			payload["message"] = self._settings.get(["events", event, "message"])
		except SkipEvent:
			# Return when we can skip this event
			return

		# Does the event exists in the settings ? if not we don't want it
		if not event in self.get_settings_defaults()["events"]:
			return

		# Only continue when there is a priority
		priority = self._settings.get(["events", event, "priority"])

		# By default, messages have normal priority (a priority of 0).
		# We do not support the Emergency Priority (2) because there is no way of canceling it here,
		if priority:
			payload["priority"] = priority
			self.event_message(payload)

	def event_message(self, payload):
		"""
		Do send the notification to the cloud :)
		:param payload: 
		:return: 
		"""
		# Create an url, if the fqdn is not correct you can manually set it at your config.yaml
		url = self._settings.get(["url"])
		if (url):
			payload["url"] = url
		else:
			# Create an url
			import socket
			payload["url"] = "http://%s" % socket.getfqdn()

		if "token" not in payload:
			payload["token"] = self.get_token()

		if "user" not in payload:
			payload["user"] = self._settings.get(["user_key"])

		if "sound" not in payload:
			# If no sound parameter is specified, the user"s default tone will play.
			# If the user has not chosen a custom sound, the standard Pushover sound will play.
			sound = self._settings.get(["sound"])
			if sound:
				payload["sound"] = sound

		if "device" not in payload:
			# If no device parameter is specified, get it from the settings.
			device = self._settings.get(["device"])
			if device:
				payload["device"] = device

		if self._printer_profile_manager is not None and "name" in self._printer_profile_manager.get_current_or_default():
			payload["title"] = "Octoprint: %s" % self._printer_profile_manager.get_current_or_default()["name"]

		files = {}
		try:
			if self._settings.get(["image"]) or ("image" in payload and payload["image"]):
				files['attachment'] = ("image.jpg", self.image())
		except Exception, e:
			self._logger.info("Could not load image from url")

		# Multiple try catches so it will always send a message if the image raises an Exception
		try:
			r = requests.post(self.api_url + "/messages.json", files=files, data=payload)
			self._logger.debug("Response: %s" % str(r.content))
		except Exception, e:
			self._logger.info("Could not send message: %s" % str(e))

	def on_after_startup(self):
		"""
		Valide settings on startup
		:return: 
		"""
		try:
			self.validate_pushover(self.get_token(), self._settings.get(["user_key"]))
		except Exception, e:
			self._logger.info(str(e))

	def get_settings_version(self):
		return 1

	def on_settings_migrate(self, target, current=None):
		if current is None:
			# If you have the default token, remove it so users will be more triggered to obtain their own.
			if self._settings.get(["token"]) == self._settings.get(["default_token"]):
				self._settings.set(["token"], None)

	def on_settings_save(self, data):
		"""
		Valide settings onm save
		:param data: 
		:return: 
		"""
		octoprint.plugin.SettingsPlugin.on_settings_save(self, data)
		try:
			import threading
			thread = threading.Thread(target=self.validate_pushover, args=(self.get_token(), self._settings.get(["user_key"]),))
			thread.daemon = True
			thread.start()
		except Exception, e:
			self._logger.info(str(e))

	def on_settings_load(self):
		data = octoprint.plugin.SettingsPlugin.on_settings_load(self)

		# only return our restricted settings to admin users - this is only needed for OctoPrint <= 1.2.16
		restricted = ("default_token", "token", "user_key")
		for r in restricted:
			if r in data and (current_user is None or current_user.is_anonymous() or not current_user.is_admin()):
				data[r] = None

		return data

	def get_settings_restricted_paths(self):
		# only used in OctoPrint versions > 1.2.16
		return dict(admin=[["default_token"], ["token"], ["user_key"]])

	def get_token(self):
		if self._settings.get(["token"]) is None:
			# If an users don't want an own API key, it is ok, you can use mine.
			return self._settings.get(["default_token"])
		return self._settings.get(["token"])

	def get_settings_defaults(self):
		return dict(
			default_token ="apWqpdodabxA5Uw11rY4g4gC1Vbbrs",
			token=None,
			user_key=None,
			sound=None,
			device=None,
			image=True,
			scheduleMod=None,
			events=dict(
				PrintDone=dict(
					name="Print done",
					message="Print job finished: {file}, finished printing in {elapsed_time}",
					priority="0"
				),
				PrintFailed=dict(
					name="Print failed",
					message="Print job failed: {file}",
					priority=0
				),
				PrintPaused=dict(
					name="Print paused",
					help="Send a notification when a Pause event is received. When a <code>m70</code> was sent "
						 "to the printer, the message will be appended to the notification.",
					message="Print job paused {m70_cmd}",
					priority=0
				),
				Waiting=dict(
					name="Printer is waiting",
					help="Send a notification when a Waiting event is received. When a <code>m70</code> was sent "
						 "to the printer, the message will be appended to the notification.",
					message="Printer is waiting {m70_cmd}",
					priority=0
				),
				Alert=dict(
					name="Alert event (M300)",
					message="Alert, The printer issued a alert (beep) via M300",
					priority=1,
					hidden=True
				),
				EStop=dict(
					name="Panic event (M112)",
					message="Panic!! The printer issued a panic stop (M112)",
					priority=1,
					hidden=True
				),
				# See: src/octoprint/util/comm.py:2009
				Error=dict(
					name="Error event",
					help="This event occurs when for example your temperature sensor disconnects.",
					message="Error!! An error has occurred in the printer communication. {error}",
					priority=1,
					hidden=True
				),

			)
		)

	def get_template_vars(self):
		return dict(
			sounds=self.get_sounds(),
			events=self.get_settings_defaults()["events"]
		)

	def get_sounds(self):
		try:
			r = requests.get(self.api_url + "/sounds.json?token="+ self.get_token())
			return json.loads(r.content)["sounds"]
		except Exception, e:
			self._logger.debug(str(e))
			return {}

	def get_template_configs(self):
		return [
			dict(type="settings", name="Pushover", custom_bindings=True)
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
		"octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information,
		"octoprint.comm.protocol.gcode.sent": __plugin_implementation__.sent_gcode
	}
