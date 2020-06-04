# OctoPrint-Pushover
This project is a Pushover plugin for OctoPrint, I wanted to receive notifications on my phone when [Octoprint](https://octoprint.org) finished, paused or gives an error while printing, and e-mail just isn't good enough. So I build a plugin for the app/service that I use, [Pushover](https://pushover.net).

## Installing

Install it trought the bundled [Plugin manager](http://docs.octoprint.org/en/master/bundledplugins/pluginmanager.html) or manually by using this url
```
https://github.com/thijsbekke/OctoPrint-Pushover/archive/master.zip
```
## Configuration

Obtain an API key through the following [Link](https://pushover.net/apps/clone/octoprint), this is not necessary for this plugin to work. 

You also have to enter your user key. You can find your own user key on your [Pushover](https://pushover.net) page. Copy and paste it to the "user key" field in the settings dialog of the Octoprint-Pushover plugin. And then you are done. 

Additional you can set a priority for each event you want to be notified of. 

## Features

This plugin supports the following features

- Send notifications on an interval (percent or time)
- Include a capture of your camera with your notifications
- Temperature reached
- Print done
- After first couple of layer
- Print Failed
- Print Started
- Printer is Waiting
- Printer Shutdown
- Print Paused
- Alert Event (M300)
- Panic Event (M112)
- Error Event
- Limit to specific devices 

This plugin will also append an url to your OctoPrint instance with the notification. If you are missing a feature you can create an [issue](https://github.com/thijsbekke/OctoPrint-Pushover/issues) or you are welcome to contributing by creating a pull request. 


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

You can enter the name of your device to send the message directly to that device, rather than all of your devices. An alternative option is to [create](https://pushover.net/groups/build) a delivery group where you can specify your devices and enter that group key as an user key in this plugin.

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



### Support my efforts

This is a fun project for me, and I do my best to support those that have issues with this plugin. If you want you can return the favor and leave me a tip trough [paypal](https://paypal.me/thijsbekke) ! 

[![paypal](https://www.paypalobjects.com/webstatic/mktg/logo/pp_cc_mark_37x23.jpg)](https://paypal.me/thijsbekke)
