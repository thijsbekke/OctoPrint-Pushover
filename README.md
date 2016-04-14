# OctoPrint-Pushover
Pushover plugin for octoprint, I wanted too receive notifications on my phone when [Octoprint](octoprint.org) finished a job, and e-mail just isn't good enough. So I build a plugin for the app that I use, [Pushover](https://pushover.net).

## Installing

Install it trought the bundled [Plugin manager](https://github.com/foosel/OctoPrint/wiki/Plugin:-Plugin-Manager) or manually by using this url
```
https://github.com/thijsbekke/OctoPrint-Pushover/archive/master.zip
```
## Configuration

The only thing you have too configure is the user key. You can find your own user key on your [Pushover](https://pushover.net) page. Copy and paste it too the "user key" field in the settings dialog of the Octoprint-Pushover plugin. And then you are done.

## Features

In the settings dialog beside the user key you can specify the priority of the notifications and a sound.

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
