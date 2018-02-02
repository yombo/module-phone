"""
For details about this module visit:
https://yombo.net/modules/twilio

Learn about at: https://yombo.net/
Get started today: https://yg2.in/start

.. moduleauthor:: Mitch Schwenk <mitch-gw@yombo.net>

:copyright: 2018 Yombo
:license: YRPL 1.6
"""
import traceback

from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks

from yombo.core.log import get_logger
from yombo.core.module import YomboModule
from yombo.utils.maxdict import MaxDict

from yombo.modules.phone.web_routes import module_phone_routes

logger = get_logger('modules.phone')

class Phone(YomboModule):
    """
    Adds the concept of phones to the gateway.
    """
    def _init_(self, **kwargs):
        """

        :param kwargs:
        :return:
        """
        self.phone_types = {
            'phone': {'device_type': self._DeviceTypes['phone']},
            'fax_phone': {'device_type': self._DeviceTypes['fax_phone']},
            'mobile_phone': {'device_type': self._DeviceTypes['mobile_phone']},
            'android_phone': {'device_type': self._DeviceTypes['android_phone']},
            'apple_phone': {'device_type': self._DeviceTypes['apple_phone']},
        }

    def _webinterface_add_routes_(self, **kwargs):
        """
        Add web hooks for module configuration

        :param kwargs:
        :return:
        """
        if self._States['loader.operating_mode'] == 'run':
            return {
                'nav_side': [
                    {
                        'label1': 'Module Settings',
                        'label2': 'Phones',
                        'priority1': 3400,  # Even with a value, 'Tools' is already defined and will be ignored.
                        'priority2': 100,
                        'icon': 'fa fa-phone',
                        'url': '/modules_settings/phone/index',
                        'tooltip': '',
                        'opmode': 'run',
                    },
                ],
                'routes': [
                    module_phone_routes,
                ],
                'configs': {
                    'settings_link': '/modules_settings/phone/index',
                },
            }

