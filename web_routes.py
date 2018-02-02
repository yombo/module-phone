import json

from twisted.internet.defer import inlineCallbacks

from yombo.core.exceptions import YomboWarning
from yombo.lib.webinterface.routes.api_v1.__init__ import return_good, return_not_found, return_error, return_unauthorized
from yombo.core.log import get_logger
from yombo.lib.webinterface.auth import require_auth

logger = get_logger("modules.phone.web_routes")

def module_phone_routes(webapp):
    """
    Adds routes to the webinterface module.

    :param webapp: A pointer to the webapp, it's used to setup routes.
    :return:
    """
    with webapp.subroute("/modules_settings") as webapp:

        def root_breadcrumb(webinterface, request):
            webinterface.add_breadcrumb(request, "/?", "Home")
            webinterface.add_breadcrumb(request, "/modules/index", "Modules")
            webinterface.add_breadcrumb(request, "/modules_settings/phone/index", "Phone")

        @webapp.route("/phone", methods=['GET'])
        @require_auth()
        def page_module_phone_get(webinterface, request, session):
            return webinterface.redirect(request, '/modules/phone/index')

        @webapp.route("/phone/index", methods=['GET'])
        @require_auth()
        def page_module_index_get(webinterface, request, session):
            phone = webinterface._Modules['Phone']
            if phone.node is None:
                page = webinterface.webapp.templates.get_template(webinterface._dir + '/pages/misc/stillbooting.html')
                root_breadcrumb(webinterface, request)
                return page.render(alerts=webinterface.get_alerts())

            page = webinterface.webapp.templates.get_template('modules/phone/web/index.html')
            root_breadcrumb(webinterface, request)

            return page.render(alerts=webinterface.get_alerts(),
                               phone=phone,
                               )

        @webapp.route("/phone/index", methods=['POST'])
        @require_auth()
        def page_module_phone_index_post(webinterface, request, session):
            phone = webinterface._Modules['Phone']
            if phone.node is None:
                page = webinterface.webapp.templates.get_template(webinterface._dir + '/pages/misc/stillbooting.html')
                root_breadcrumb(webinterface, request)
                return page.render(alerts=webinterface.get_alerts())

            if 'json_output' in request.args:
                json_output = request.args.get('json_output', [{}])[0]
                json_output = json.loads(json_output)
                # print("json_out: %s" % json_output)
                allowed = []
                for device_id, value in json_output.items():
                    if value == '1':
                        if device_id.startswith("devid_"):
                            parts = device_id.split('_')
                            device_id = parts[1]
                            if device_id in phone._Devices:
                                allowed.append(parts[1])

                if 'devices' not in phone.node.data:
                    phone.node.data['devices'] = {}
                # if 'allowed' not in phone.node.data:
                #     phone.node.data['devices']['allowed'] = {}
                phone.node.data['devices']['allowed'] = allowed
                phone.discovery(save=False)

            page = webinterface.webapp.templates.get_template('modules/phone/web/index.html')
            root_breadcrumb(webinterface, request)

            return page.render(alerts=webinterface.get_alerts(),
                               phone=phone,
                               )


    with webapp.subroute("/api/v1/extended") as webapp:

        @webapp.route("/alexa/control", methods=['POST'])
        @require_auth(api=True)
        @inlineCallbacks
        def page_module_phone_control_post(webinterface, request, session):
            phone = webinterface._Modules['Phone']
            try:
                data = json.loads(request.content.read())
            except:
                return return_error(message="invalid JSON sent", code=400)

            enc = yield webinterface._GPG.encrypt(data['request'])
            results = "testing: %s" % enc
            return results

    # def _device_command_(self, **kwargs):
    #     """
    #     Discovers all device within the current cluster and sends them to Yombo. Alexa will periodically fetch from
    #     Yombo servers, even if this gateway is offline or not accessible when Alexa asks for devices.
    #
    #     This doesn't build the entire response struture, only the endpoint sections. Yombo will
    #     combine multiple master nodes and create a single response to Alexa.
    #
    #     If for some reason someone decides to mangle this, Alexa will get a managed response and not smart home
    #     devices will work through Alexa.
    #
    #     :return:
    #     """
    #     device = kwargs['device']
    #     if device_id not in self.node.data['devices']['allowed'] or device.enabled_status != 1:
    #
    #     endpoints = {}
    #     for device_id, device in self._Devices.devices.items():
    #         # print("alexa: doing device: %s - %s" % (device.label, device.enabled_status))
    #
    #         continue
    #         # print("alexa device has good status: %s" % device.label)
    #     try:
    #         endpoints[device_id] = self.generate_endpoints(device)
    #     except YomboWarning as e:
    #         logger.warn("{e}", e=e)
    #
    #     # print("alexa endpoints: %s" % json.dumps(endpoints))
    #     self.node.data['alexa'] = endpoints
    #     if save is not False:
    #         self.node.save()
