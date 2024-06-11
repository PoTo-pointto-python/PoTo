from __future__ import absolute_import, division, print_function
__metaclass__ = type
ANSIBLE_METADATA = {'metadata_version': '1.1', 'status': ['preview'], 'supported_by': 'community'}
DOCUMENTATION = '\n---\nmodule: zabbix_proxy\nshort_description: Create/delete/get/update Zabbix proxies\ndescription:\n   - This module allows you to create, modify, get and delete Zabbix proxy entries.\nversion_added: "2.5"\nauthor:\n    - "Alen Komic (@akomic)"\nrequirements:\n    - "python >= 2.6"\n    - "zabbix-api >= 0.5.4"\noptions:\n    proxy_name:\n        description:\n            - Name of the proxy in Zabbix.\n        required: true\n        type: str\n    proxy_address:\n        description:\n            - Comma-delimited list of IP/CIDR addresses or DNS names to accept active proxy requests from.\n            - Requires I(status=active).\n            - Works only with >= Zabbix 4.0. ( remove option for <= 4.0 )\n        required: false\n        version_added: \'2.10\'\n        type: str\n    description:\n        description:\n            - Description of the proxy.\n        required: false\n        type: str\n    status:\n        description:\n            - Type of proxy. (4 - active, 5 - passive)\n        required: false\n        choices: [\'active\', \'passive\']\n        default: "active"\n        type: str\n    tls_connect:\n        description:\n            - Connections to proxy.\n        required: false\n        choices: [\'no_encryption\',\'PSK\',\'certificate\']\n        default: \'no_encryption\'\n        type: str\n    tls_accept:\n        description:\n            - Connections from proxy.\n        required: false\n        choices: [\'no_encryption\',\'PSK\',\'certificate\']\n        default: \'no_encryption\'\n        type: str\n    ca_cert:\n        description:\n            - Certificate issuer.\n        required: false\n        aliases: [ tls_issuer ]\n        type: str\n    tls_subject:\n        description:\n            - Certificate subject.\n        required: false\n        type: str\n    tls_psk_identity:\n        description:\n            - PSK identity. Required if either I(tls_connect) or I(tls_accept) has PSK enabled.\n        required: false\n        type: str\n    tls_psk:\n        description:\n            - The preshared key, at least 32 hex digits. Required if either I(tls_connect) or I(tls_accept) has PSK enabled.\n        required: false\n        type: str\n    state:\n        description:\n            - State of the proxy.\n            - On C(present), it will create if proxy does not exist or update the proxy if the associated data is different.\n            - On C(absent) will remove a proxy if it exists.\n        required: false\n        choices: [\'present\', \'absent\']\n        default: "present"\n        type: str\n    interface:\n        description:\n            - Dictionary with params for the interface when proxy is in passive mode.\n            - For more information, review proxy interface documentation at\n            - U(https://www.zabbix.com/documentation/4.0/manual/api/reference/proxy/object#proxy_interface).\n        required: false\n        suboptions:\n            useip:\n                type: int\n                description:\n                    - Connect to proxy interface with IP address instead of DNS name.\n                    - 0 (don\'t use ip), 1 (use ip).\n                default: 0\n                choices: [0, 1]\n            ip:\n                type: str\n                description:\n                    - IP address used by proxy interface.\n                    - Required if I(useip=1).\n                default: \'\'\n            dns:\n                type: str\n                description:\n                    - DNS name of the proxy interface.\n                    - Required if I(useip=0).\n                default: \'\'\n            port:\n                type: str\n                description:\n                    - Port used by proxy interface.\n                default: \'10051\'\n            type:\n                type: int\n                description:\n                    - Interface type to add.\n                    - This suboption is currently ignored for Zabbix proxy.\n                    - This suboption is deprecated since Ansible 2.10 and will eventually be removed in 2.14.\n                required: false\n                default: 0\n            main:\n                type: int\n                description:\n                    - Whether the interface is used as default.\n                    - This suboption is currently ignored for Zabbix proxy.\n                    - This suboption is deprecated since Ansible 2.10 and will eventually be removed in 2.14.\n                required: false\n                default: 0\n        default: {}\n        type: dict\n\nextends_documentation_fragment:\n    - zabbix\n'
EXAMPLES = "\n- name: Create or update a proxy with proxy type active\n  local_action:\n    module: zabbix_proxy\n    server_url: http://monitor.example.com\n    login_user: username\n    login_password: password\n    proxy_name: ExampleProxy\n    description: ExampleProxy\n    status: active\n    state: present\n    proxy_address: ExampleProxy.local\n\n- name: Create a new passive proxy using only it's IP\n  local_action:\n    module: zabbix_proxy\n    server_url: http://monitor.example.com\n    login_user: username\n    login_password: password\n    proxy_name: ExampleProxy\n    description: ExampleProxy\n    status: passive\n    state: present\n    interface:\n      useip: 1\n      ip: 10.1.1.2\n      port: 10051\n\n- name: Create a new passive proxy using only it's DNS\n  local_action:\n    module: zabbix_proxy\n    server_url: http://monitor.example.com\n    login_user: username\n    login_password: password\n    proxy_name: ExampleProxy\n    description: ExampleProxy\n    status: passive\n    state: present\n    interface:\n      dns: proxy.example.com\n      port: 10051\n"
RETURN = ' # '
import traceback
import atexit
from ansible.module_utils.basic import AnsibleModule, missing_required_lib
try:
    from zabbix_api import ZabbixAPI
    HAS_ZABBIX_API = True
except ImportError:
    ZBX_IMP_ERR = traceback.format_exc()
    HAS_ZABBIX_API = False

class Proxy(object):

    def __init__(self, module, zbx):
        self._module = module
        self._zapi = zbx
        self.existing_data = None

    def proxy_exists(self, proxy_name):
        result = self._zapi.proxy.get({'output': 'extend', 'selectInterface': 'extend', 'filter': {'host': proxy_name}})
        if len(result) > 0 and 'proxyid' in result[0]:
            self.existing_data = result[0]
            return result[0]['proxyid']
        else:
            return result

    def add_proxy(self, data):
        try:
            if self._module.check_mode:
                self._module.exit_json(changed=True)
            parameters = {}
            for item in data:
                if data[item]:
                    parameters[item] = data[item]
            if 'proxy_address' in data and data['status'] != '5':
                parameters.pop('proxy_address', False)
            if 'interface' in data and data['status'] != '6':
                parameters.pop('interface', False)
            proxy_ids_list = self._zapi.proxy.create(parameters)
            self._module.exit_json(changed=True, result='Successfully added proxy %s (%s)' % (data['host'], data['status']))
            if len(proxy_ids_list) >= 1:
                return proxy_ids_list['proxyids'][0]
        except Exception as e:
            self._module.fail_json(msg='Failed to create proxy %s: %s' % (data['host'], e))

    def delete_proxy(self, proxy_id, proxy_name):
        try:
            if self._module.check_mode:
                self._module.exit_json(changed=True)
            self._zapi.proxy.delete([proxy_id])
            self._module.exit_json(changed=True, result='Successfully deleted' + ' proxy %s' % proxy_name)
        except Exception as e:
            self._module.fail_json(msg='Failed to delete proxy %s: %s' % (proxy_name, str(e)))

    def compile_interface_params(self, new_interface):
        old_interface = {}
        if 'interface' in self.existing_data and len(self.existing_data['interface']) > 0:
            old_interface = self.existing_data['interface']
        for item in ['type', 'main']:
            new_interface.pop(item, False)
        final_interface = old_interface.copy()
        final_interface.update(new_interface)
        final_interface = dict(((k, str(v)) for (k, v) in final_interface.items()))
        if final_interface != old_interface:
            return final_interface
        else:
            return {}

    def update_proxy(self, proxy_id, data):
        try:
            if self._module.check_mode:
                self._module.exit_json(changed=True)
            parameters = {'proxyid': proxy_id}
            for item in data:
                if data[item] and item in self.existing_data and (self.existing_data[item] != data[item]):
                    parameters[item] = data[item]
            if 'interface' in parameters:
                parameters.pop('interface')
            if 'proxy_address' in data and data['status'] != '5':
                parameters.pop('proxy_address', False)
            if 'interface' in data and data['status'] != '6':
                parameters.pop('interface', False)
            if 'interface' in data and data['status'] == '6':
                new_interface = self.compile_interface_params(data['interface'])
                if len(new_interface) > 0:
                    parameters['interface'] = new_interface
            if len(parameters) > 1:
                self._zapi.proxy.update(parameters)
                self._module.exit_json(changed=True, result='Successfully updated proxy %s (%s)' % (data['host'], proxy_id))
            else:
                self._module.exit_json(changed=False)
        except Exception as e:
            self._module.fail_json(msg='Failed to update proxy %s: %s' % (data['host'], e))

def main():
    module = AnsibleModule(argument_spec=dict(server_url=dict(type='str', required=True, aliases=['url']), login_user=dict(type='str', required=True), login_password=dict(type='str', required=True, no_log=True), proxy_name=dict(type='str', required=True), proxy_address=dict(type='str', required=False), http_login_user=dict(type='str', required=False, default=None), http_login_password=dict(type='str', required=False, default=None, no_log=True), validate_certs=dict(type='bool', required=False, default=True), status=dict(type='str', default='active', choices=['active', 'passive']), state=dict(type='str', default='present', choices=['present', 'absent']), description=dict(type='str', required=False), tls_connect=dict(type='str', default='no_encryption', choices=['no_encryption', 'PSK', 'certificate']), tls_accept=dict(type='str', default='no_encryption', choices=['no_encryption', 'PSK', 'certificate']), ca_cert=dict(type='str', required=False, default=None, aliases=['tls_issuer']), tls_subject=dict(type='str', required=False, default=None), tls_psk_identity=dict(type='str', required=False, default=None), tls_psk=dict(type='str', required=False, default=None), timeout=dict(type='int', default=10), interface=dict(type='dict', required=False, default={}, options=dict(useip=dict(type='int', choices=[0, 1], default=0), ip=dict(type='str', default=''), dns=dict(type='str', default=''), port=dict(type='str', default='10051'), type=dict(type='int', default=0, removed_in_version='2.14'), main=dict(type='int', default=0, removed_in_version='2.14')))), supports_check_mode=True)
    if not HAS_ZABBIX_API:
        module.fail_json(msg=missing_required_lib('zabbix-api', url='https://pypi.org/project/zabbix-api/'), exception=ZBX_IMP_ERR)
    server_url = module.params['server_url']
    login_user = module.params['login_user']
    login_password = module.params['login_password']
    http_login_user = module.params['http_login_user']
    http_login_password = module.params['http_login_password']
    validate_certs = module.params['validate_certs']
    proxy_name = module.params['proxy_name']
    proxy_address = module.params['proxy_address']
    description = module.params['description']
    status = module.params['status']
    tls_connect = module.params['tls_connect']
    tls_accept = module.params['tls_accept']
    tls_issuer = module.params['ca_cert']
    tls_subject = module.params['tls_subject']
    tls_psk_identity = module.params['tls_psk_identity']
    tls_psk = module.params['tls_psk']
    state = module.params['state']
    timeout = module.params['timeout']
    interface = module.params['interface']
    status = 6 if status == 'passive' else 5
    if tls_connect == 'certificate':
        tls_connect = 4
    elif tls_connect == 'PSK':
        tls_connect = 2
    else:
        tls_connect = 1
    if tls_accept == 'certificate':
        tls_accept = 4
    elif tls_accept == 'PSK':
        tls_accept = 2
    else:
        tls_accept = 1
    zbx = None
    try:
        zbx = ZabbixAPI(server_url, timeout=timeout, user=http_login_user, passwd=http_login_password, validate_certs=validate_certs)
        zbx.login(login_user, login_password)
        atexit.register(zbx.logout)
    except Exception as e:
        module.fail_json(msg='Failed to connect to Zabbix server: %s' % e)
    proxy = Proxy(module, zbx)
    proxy_id = proxy.proxy_exists(proxy_name)
    if proxy_id:
        if state == 'absent':
            proxy.delete_proxy(proxy_id, proxy_name)
        else:
            proxy.update_proxy(proxy_id, {'host': proxy_name, 'description': description, 'status': str(status), 'tls_connect': str(tls_connect), 'tls_accept': str(tls_accept), 'tls_issuer': tls_issuer, 'tls_subject': tls_subject, 'tls_psk_identity': tls_psk_identity, 'tls_psk': tls_psk, 'interface': interface, 'proxy_address': proxy_address})
    else:
        if state == 'absent':
            module.exit_json(changed=False)
        proxy_id = proxy.add_proxy(data={'host': proxy_name, 'description': description, 'status': str(status), 'tls_connect': str(tls_connect), 'tls_accept': str(tls_accept), 'tls_issuer': tls_issuer, 'tls_subject': tls_subject, 'tls_psk_identity': tls_psk_identity, 'tls_psk': tls_psk, 'interface': interface, 'proxy_address': proxy_address})
if __name__ == '__main__':
    main()

def test_Proxy_proxy_exists():
    ret = Proxy().proxy_exists()

def test_Proxy_add_proxy():
    ret = Proxy().add_proxy()

def test_Proxy_delete_proxy():
    ret = Proxy().delete_proxy()

def test_Proxy_compile_interface_params():
    ret = Proxy().compile_interface_params()

def test_Proxy_update_proxy():
    ret = Proxy().update_proxy()