"""
For details about this module visit:
https://yombo.net/modules/phone

Learn about at: https://yombo.net/
Get started today: https://yg2.in/start

.. moduleauthor:: Mitch Schwenk <mitch-gw@yombo.net>

:copyright: 2018 Yombo
:license: YRPL 1.6
"""
import traceback

from twisted.internet.defer import inlineCallbacks

from yombo.core.log import get_logger
from yombo.core.module import YomboModule
from yombo.utils import global_invoke_all

from yombo.modules.phone.web_routes import module_phone_routes

logger = get_logger('modules.phone')

class Phone(YomboModule):
    """
    Adds the concept of phones to the gateway. Allows users to add phone device types.
    """
    def _init_(self, **kwargs):
        """
        Only allow the module to run if it's on the master gateway for a cluster.

        :param kwargs:
        :return:
        """
        self.is_master = self._Configs.get('core', 'is_master', True, False)
        if self.is_master is False:
            logger.warn("Phone module disabled, only works on the master gateway of a cluster.")
            self._Notifications.add({'title': 'Phone module not started',
                                     'message': 'The phone module can only be used on a master gateway node.',
                                     'source': 'Phone Module',
                                     'persist': False,
                                     'priority': 'high',
                                     'always_show': True,
                                     'always_show_allow_clear': False,
                                     })
            return

        self.gwid = self._Gateways.get_local_id()

        self.phone_types = {
            'phone': {'device_type': self._DeviceTypes['phone']},
            'fax': {'device_type': self._DeviceTypes['fax_phone']},
            'mobile': {'device_type': self._DeviceTypes['mobile_phone']},
            'android': {'device_type': self._DeviceTypes['android_phone']},
            'apple': {'device_type': self._DeviceTypes['apple_phone']},
        }
        self.node = None

    @inlineCallbacks
    def _start_(self, **kwargs):
        """
        Load the configuration node, otherwise create a new node if required.

        :param kwargs:
        :return:
        """
        if self.is_master is False:
            return

        nodes = self._Nodes.search({'node_type': 'module_phone'})
        if len(nodes) == 0:
            logger.info("Phone creating new node...")
            self.node = yield self._Nodes.create(label='Module Phone',
                                                 machine_label='module_phone',
                                                 node_type='module_phone',
                                                 data={'phones': {}, 'configs': {}},
                                                 data_content_type='json',
                                                 gateway_id=self.gwid,
                                                 destination='gw')
        elif nodes is not None and len(nodes) > 1:
            logger.warn("Too many node instances. Taking the first one and dropping old ones.")

        for node_id, node in nodes.items():
            self.node = node
            if 'phones' not in self.node.data:
                self.node.data['phones'] = {}
            if 'configs' not in self.node.data:
                self.node.data['configs'] = {}
            break

        module_devices = yield self._module_devices()
        for device_id, device in module_devices.items():
            if device_id not in self.node.data['phones']:
                self.node.data['phones'][device_id] = {
                    'targets': [],
                }

        print("phone data: %s" % self.node.data)
        for device_id in self.node.data['phones'].keys():
            if device_id not in module_devices:
                del self.node.data['phones'][device_id]

    def _webinterface_add_routes_(self, **kwargs):
        """
        Add web hooks for module configuration

        :param kwargs:
        :return:
        """
        if self.is_master is True and self._States['loader.operating_mode'] == 'run':
            return {
                'nav_side': [
                    {
                        'label1': 'Module Settings',
                        'label2': 'Phones',
                        'priority1': 820,  # Even with a value, 'Tools' is already defined and will be ignored.
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

    @inlineCallbacks
    def _notification_target_(self, **kwargs):
        """
        Relays notification targets to sub-modules so they can optionally send
        them to phones.

        :param kwargs:
        :return:
        """
        # print("phone got _notification_target_")
        target = kwargs['target']
        # print("phone got _notification_target_ 2")
        event = kwargs['event']
        # print("got _notification_target_ in phone: %s" % event)
        if 'image_uri' in event['meta']:
            image_uri = event['meta']['image_uri']
        else:
            image_uri = None
        # print("got _notification_target_ in image: %s " % image_uri)
        for phone_id, data in self.node.data['phones'].items():
            # print("phone id: %s" % phone_id)
            # print("phone data: %s" % self.node.data['phones'][phone_id])
            if target in self.node.data['phones'][phone_id]['targets']:
                # print("phone is about to call it's own hook...")
                yield global_invoke_all('phone_target',
                                        called_by=self,
                                        message=event['message'],
                                        phone=self._Devices[phone_id],
                                        )
