from yombo.lib.devices._device import Device


class Phone(Device):
    """
    A generic
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.PLATFORM = "phone"
        self.TOGGLE_COMMANDS = []

        self.FEATURES.update({
            'has_bluetooth': False,
            'has_wifi': False,
            'receives_sms': False,
            'receives_images': False,
            'receives_calls': True,
            'makes_sms': True,
            'makes_images': True,
            'makes_calls': True,
        })

    def can_toggle(self):
        return False

    def toggle(self):
        return False

    def turn_on(self, cmd, **kwargs):
        return False

    def turn_off(self, cmd, **kwargs):
        return False

    def generate_human_status(self, machine_status, machine_status_extra):
        return None

    def generate_human_message(self, machine_status, machine_status_extra):
        return None

    @property
    def phone_number(self):
        if 'phone_number' in self.device_variables_cached:
            return self.device_variables_cached['phone_number']['values'][0]
        return None

    @property
    def phone_user(self):
        if 'phone_number' in self.device_variables_cached:
            return self.device_variables_cached['phone_user']['values'][0]
        return None

    @property
    def bluetooth_address(self):
        return None

    @property
    def wifi_address(self):
        return None


class FaxPhone(Phone):
    """
    A fax based phone number.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.SUB_PLATFORM = "mobile"
        self.FEATURES.update({
            'receives_images': True,
            'makes_images': True,
        })


class MobilePhone(Phone):
    """
    A generic
    """
    @property
    def bluetooth_address(self):
        if 'bluetooth_address' in self.device_variables_cached:
            return self.device_variables_cached['bluetooth_address']['values'][0]
        return None

    @property
    def wifi_address(self):
        if 'wifi_address' in self.device_variables_cached:
            return self.device_variables_cached['wifi_address']['values'][0]
        return None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.SUB_PLATFORM = "mobile"
        self.FEATURES.update({
            'has_bluetooth': True,
            'has_wifi': True,
            'has_nfc': True,
            'receives_sms': True,
            'receives_images': True,
            'receives_calls': True,
            'makes_sms': True,
            'makes_images': True,
            'makes_calls': True,
        })


class AndroidPhone(MobilePhone):
    """
    An Android device.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.SUB_PLATFORM = "android"


class ApplePhone(MobilePhone):
    """
    Apple Phone.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.SUB_PLATFORM = "apple"
        self.FEATURES['has_nfc'] = False
