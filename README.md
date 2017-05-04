# OctoPrint-Pushover
Pushover plugin for octoprint, I wanted too receive notifications on my phone when [Octoprint](octoprint.org) finished a job, and e-mail just isn't good enough. So I build a plugin for the app/service that I use, [Pushover](https://pushover.net).

## Installing

Install it trought the bundled [Plugin manager](https://github.com/foosel/OctoPrint/wiki/Plugin:-Plugin-Manager) or manually by using this url
```
https://github.com/thijsbekke/OctoPrint-Pushover/archive/master.zip
```
## Configuration

The only thing you have too configure is the user key and set a priority for which event you want too be notified. You can find your own user key on your [Pushover](https://pushover.net) page. Copy and paste it too the "user key" field in the settings dialog of the Octoprint-Pushover plugin. And then you are done, the rest of the settings are optional.

## Features

This plugin can send a notification with Pushover on the following events; Print done, Print failed and Print paused. In the settings dialog beside the user key you can specify the devices, priority of the notifications and a sound.

This plugin will also append an url too your octoprint instance with the notification.


### Priority

- Lowest Priority

When this priority is set, messages will be considered lowest priority and will not generate any notification. On iOS, the application badge number will be increased.

- Low Priority

Messages with this priority will not generate any sound or vibration, but will still generate a popup/scrolling notification depending on the client operating system.

- Normal Priority

Messages with the normal priority trigger sound, vibration, and display an alert according to the user's device settings. On iOS, the message will display at the top of the screen or as a modal dialog, as well as in the notification center. On Android, the message will scroll at the top of the screen and appear in the notification center.

If a user has quiet hours set and your message is received during those times, your message will be delivered as though it had a priority of Low priority

- High Priority

Messages sent with this priority bypasses a user's quiet hours. These messages will always play a sound and vibrate (if the user's device is configured to) regardless of the delivery time.

### Sound

You can specify a custom sound, your device will play this sound when receiving a message. You can specify one of [these sounds](https://pushover.net/api#sounds)

### Devices

You can enter the name of your device to send the message directly to that device, rather than all of your devices. An alternative option is to create a delivery group where you can specify your devices on [pushover.net](https://pushover.net/groups/build) and enter that group key as an user key in this plugin.

### Pause/Waiting Event

When for example a ```M0``` or a ```M226``` command is received and the settings are complied. This plugin will send a notification. And as bonus it will append any ```M70``` message to the notification, so you can remind yourself which colour you need to switch.

For example
```GCODE
G1 X109.071 Y96.268 E3.54401
G1 X109.186 Y97.500 E3.63927
M70 Sleep Message
M0
G1 X109.186 Y102.500 E4.02408
G1 X108.789 Y104.770 E4.20140
```

### API Key

Under advanced options you can specify your own API key, this is not necessary for this plugin too work. But when you want it, you can do it.

### Url

If the automatic created url is not correct you can overrule this by edit the config.yaml

example:
```JSON
plugins:
  pushover:
    priority: '0'
    sound: intermission
    url: 192.168.1.24
```
