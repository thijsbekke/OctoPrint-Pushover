$(function() {
    function PushoverViewModel(parameters) {
        var self = this;

        self.settingsViewModel = parameters[1];

        self.testActive = ko.observable(false);
        self.testResult = ko.observable(false);
        self.testSuccessful = ko.observable(false);
        self.testMessage = ko.observable();

        self.testNotification  = function() {
            self.testActive(true);
            self.testResult(false);
            self.testSuccessful(false);
            self.testMessage("");

            var apikey = $('#apikey').val();
            var userkey = $('#userkey').val();
            var sound = $('#pushover-sound option:selected').text();
            var device = $('#device').val();
            var image = $('#image').is(':checked');
            var lighting_pin = $('#lighting_pin').val();
            var lighting_pin_low = $('#lighting_pin_low').is(':checked');

            var payload = {
                command: "test",
                api_key: apikey,
                user_key: userkey,
                sound: sound,
                device: device,
                image: image,
                lighting_pin: lighting_pin,
                lighting_pin_low: lighting_pin_low,
            };

            $.ajax({
                url: API_BASEURL + "plugin/pushover",
                type: "POST",
                dataType: "json",
                data: JSON.stringify(payload),
                contentType: "application/json; charset=UTF-8",
                success: function(response) {
                    self.testResult(true);
                    self.testSuccessful(response.success);
                    if (!response.success && response.hasOwnProperty("msg")) {
                        self.testMessage(response.msg);
                    } else {
                        self.testMessage(undefined);
                    }
                },
                complete: function() {
                    self.testActive(false);
                }
            });
        };

        self.onBeforeBinding = function() {
            self.settings = self.settingsViewModel.settings;
        };

        self.has_own_token = function() {
            return self.settings.plugins.pushover.token() != '' && self.settings.plugins.pushover.token() != self.settings.plugins.pushover.default_token();
        };

    }

    // view model class, parameters for constructor, container to bind to
    ADDITIONAL_VIEWMODELS.push([PushoverViewModel, ["loginStateViewModel", "settingsViewModel"], document.getElementById("settings_plugin_pushover")]);
});
