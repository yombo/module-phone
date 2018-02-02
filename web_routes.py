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
        def page_module_phone_index_get(webinterface, request, session):
            phonemodule = webinterface._Modules['Phone']
            page = webinterface.webapp.templates.get_template('modules/phone/web/index.html')
            root_breadcrumb(webinterface, request)

            return page.render(alerts=webinterface.get_alerts(),
                               phonemodule=phonemodule,
                               )

        @webapp.route("/phone/<string:device_id>/details", methods=['GET'])
        @require_auth()
        def page_module_phone_details_get(webinterface, request, session, device_id):
            phonemodule = webinterface._Modules['Phone']
            if phonemodule.node is None:
                page = webinterface.webapp.templates.get_template(webinterface._dir + '/pages/misc/stillbooting.html')
                root_breadcrumb(webinterface, request)
                return page.render(alerts=webinterface.get_alerts())

            try:
                device = webinterface._Devices[device_id]
            except Exception as e:
                webinterface.add_alert('Device ID was not found.  %s' % e, 'warning')
                return webinterface.redirect(request, '/module_settings/phone')
            page = webinterface.webapp.templates.get_template('modules/phone/web/details.html')
            root_breadcrumb(webinterface, request)
            webinterface.add_breadcrumb(request,
                                        "/module_settings/phone/%s/details" % device_id,
                                        "%s details" % device.label)
            return page.render(alerts=webinterface.get_alerts(),
                               phone=device,
                               phonemodule=phonemodule,
                               targets=webinterface._Notifications.notification_targets,
                               # module_devices=phonemodule._module_devices_cached
                               )

        @webapp.route("/phone/<string:device_id>/edit", methods=['GET'])
        @require_auth()
        def page_module_phone_edit_get(webinterface, request, session, device_id):
            phonemodule = webinterface._Modules['Phone']
            if phonemodule.node is None:
                page = webinterface.webapp.templates.get_template(webinterface._dir + '/pages/misc/stillbooting.html')
                root_breadcrumb(webinterface, request)
                return page.render(alerts=webinterface.get_alerts())

            try:
                device = webinterface._Devices[device_id]
            except Exception as e:
                webinterface.add_alert('Device ID was not found.  %s' % e, 'warning')
                return webinterface.redirect(request, '/module_settings/phone')
            page = webinterface.webapp.templates.get_template('modules/phone/web/edit.html')
            root_breadcrumb(webinterface, request)
            webinterface.add_breadcrumb(request,
                                        "/module_settings/phone/%s/details" % device_id,
                                        "%s details" % device.label)
            webinterface.add_breadcrumb(request,
                                        "/module_settings/phone/%s/edit" % device_id,
                                        "Edit")
            return page.render(alerts=webinterface.get_alerts(),
                               phone=device,
                               phonemodule=phonemodule,
                               targets=webinterface._Notifications.notification_targets,
                               nodedata=phonemodule.node.data
                               # module_devices=phonemodule._module_devices_cached
                               )

        @webapp.route("/phone/<string:device_id>/edit", methods=['POST'])
        @require_auth()
        def page_module_phone_edit_post(webinterface, request, session, device_id):
            phonemodule = webinterface._Modules['Phone']
            if phonemodule.node is None:
                page = webinterface.webapp.templates.get_template(webinterface._dir + '/pages/misc/stillbooting.html')
                root_breadcrumb(webinterface, request)
                return page.render(alerts=webinterface.get_alerts())

            try:
                device = webinterface._Devices[device_id]
            except Exception as e:
                webinterface.add_alert('Device ID was not found.  %s' % e, 'warning')
                return webinterface.redirect(request, '/module_settings/phone')

            if 'json_output' in request.args:
                json_output = request.args.get('json_output', [{}])[0]
                json_output = json.loads(json_output)
                print("json_output: %s" % json_output)
                phonemodule.node.data['phones'][device_id]['targets'] = []
                for input, value in json_output.items():
                    print("got input: %s = %s" % (input, value))
                    if input.startswith('target__'):
                        items = input.split('__')
                        print("New phone target: %s" % items[1])
                        print("Phone data before: %s" % phonemodule.node.data['phones'])
                        phonemodule.node.data['phones'][device_id]['targets'].append(items[1])
                        print("Phone data after: %s" % phonemodule.node.data['phones'])
                print("Phone data: %s" % phonemodule.node.data['phones'])
                print("node data typoe: %s" % type(phonemodule.node.data))
                phonemodule.node.save()

            page = webinterface.webapp.templates.get_template('modules/phone/web/index.html')
            root_breadcrumb(webinterface, request)
            return page.render(alerts=webinterface.get_alerts(),
                               phonemodule=phonemodule,
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
