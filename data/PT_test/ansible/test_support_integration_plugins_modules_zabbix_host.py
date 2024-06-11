from __future__ import absolute_import, division, print_function
__metaclass__ = type
ANSIBLE_METADATA = {'metadata_version': '1.1', 'status': ['preview'], 'supported_by': 'community'}
DOCUMENTATION = '\n---\nmodule: zabbix_host\nshort_description: Create/update/delete Zabbix hosts\ndescription:\n   - This module allows you to create, modify and delete Zabbix host entries and associated group and template data.\nversion_added: "2.0"\nauthor:\n    - "Cove (@cove)"\n    - Tony Minfei Ding (!UNKNOWN)\n    - Harrison Gu (@harrisongu)\n    - Werner Dijkerman (@dj-wasabi)\n    - Eike Frost (@eikef)\nrequirements:\n    - "python >= 2.6"\n    - "zabbix-api >= 0.5.4"\noptions:\n    host_name:\n        description:\n            - Name of the host in Zabbix.\n            - I(host_name) is the unique identifier used and cannot be updated using this module.\n        required: true\n        type: str\n    visible_name:\n        description:\n            - Visible name of the host in Zabbix.\n        version_added: \'2.3\'\n        type: str\n    description:\n        description:\n            - Description of the host in Zabbix.\n        version_added: \'2.5\'\n        type: str\n    host_groups:\n        description:\n            - List of host groups the host is part of.\n        type: list\n        elements: str\n    link_templates:\n        description:\n            - List of templates linked to the host.\n        type: list\n        elements: str\n    inventory_mode:\n        description:\n            - Configure the inventory mode.\n        choices: [\'automatic\', \'manual\', \'disabled\']\n        version_added: \'2.1\'\n        type: str\n    inventory_zabbix:\n        description:\n            - Add Facts for a zabbix inventory (e.g. Tag) (see example below).\n            - Please review the interface documentation for more information on the supported properties\n            - U(https://www.zabbix.com/documentation/3.2/manual/api/reference/host/object#host_inventory)\n        version_added: \'2.5\'\n        type: dict\n    status:\n        description:\n            - Monitoring status of the host.\n        choices: [\'enabled\', \'disabled\']\n        default: \'enabled\'\n        type: str\n    state:\n        description:\n            - State of the host.\n            - On C(present), it will create if host does not exist or update the host if the associated data is different.\n            - On C(absent) will remove a host if it exists.\n        choices: [\'present\', \'absent\']\n        default: \'present\'\n        type: str\n    proxy:\n        description:\n            - The name of the Zabbix proxy to be used.\n        type: str\n    interfaces:\n        type: list\n        elements: dict\n        description:\n            - List of interfaces to be created for the host (see example below).\n            - For more information, review host interface documentation at\n            - U(https://www.zabbix.com/documentation/4.0/manual/api/reference/hostinterface/object)\n        suboptions:\n            type:\n                description:\n                    - Interface type to add\n                    - Numerical values are also accepted for interface type\n                    - 1 = agent\n                    - 2 = snmp\n                    - 3 = ipmi\n                    - 4 = jmx\n                choices: [\'agent\', \'snmp\', \'ipmi\', \'jmx\']\n                required: true\n            main:\n                type: int\n                description:\n                    - Whether the interface is used as default.\n                    - If multiple interfaces with the same type are provided, only one can be default.\n                    - 0 (not default), 1 (default)\n                default: 0\n                choices: [0, 1]\n            useip:\n                type: int\n                description:\n                    - Connect to host interface with IP address instead of DNS name.\n                    - 0 (don\'t use ip), 1 (use ip)\n                default: 0\n                choices: [0, 1]\n            ip:\n                type: str\n                description:\n                    - IP address used by host interface.\n                    - Required if I(useip=1).\n                default: \'\'\n            dns:\n                type: str\n                description:\n                    - DNS name of the host interface.\n                    - Required if I(useip=0).\n                default: \'\'\n            port:\n                type: str\n                description:\n                    - Port used by host interface.\n                    - If not specified, default port for each type of interface is used\n                    - 10050 if I(type=\'agent\')\n                    - 161 if I(type=\'snmp\')\n                    - 623 if I(type=\'ipmi\')\n                    - 12345 if I(type=\'jmx\')\n            bulk:\n                type: int\n                description:\n                    - Whether to use bulk SNMP requests.\n                    - 0 (don\'t use bulk requests), 1 (use bulk requests)\n                choices: [0, 1]\n                default: 1\n        default: []\n    tls_connect:\n        description:\n            - Specifies what encryption to use for outgoing connections.\n            - Possible values, 1 (no encryption), 2 (PSK), 4 (certificate).\n            - Works only with >= Zabbix 3.0\n        default: 1\n        version_added: \'2.5\'\n        type: int\n    tls_accept:\n        description:\n            - Specifies what types of connections are allowed for incoming connections.\n            - The tls_accept parameter accepts values of 1 to 7\n            - Possible values, 1 (no encryption), 2 (PSK), 4 (certificate).\n            - Values can be combined.\n            - Works only with >= Zabbix 3.0\n        default: 1\n        version_added: \'2.5\'\n        type: int\n    tls_psk_identity:\n        description:\n            - It is a unique name by which this specific PSK is referred to by Zabbix components\n            - Do not put sensitive information in the PSK identity string, it is transmitted over the network unencrypted.\n            - Works only with >= Zabbix 3.0\n        version_added: \'2.5\'\n        type: str\n    tls_psk:\n        description:\n            - PSK value is a hard to guess string of hexadecimal digits.\n            - The preshared key, at least 32 hex digits. Required if either I(tls_connect) or I(tls_accept) has PSK enabled.\n            - Works only with >= Zabbix 3.0\n        version_added: \'2.5\'\n        type: str\n    ca_cert:\n        description:\n            - Required certificate issuer.\n            - Works only with >= Zabbix 3.0\n        version_added: \'2.5\'\n        aliases: [ tls_issuer ]\n        type: str\n    tls_subject:\n        description:\n            - Required certificate subject.\n            - Works only with >= Zabbix 3.0\n        version_added: \'2.5\'\n        type: str\n    ipmi_authtype:\n        description:\n            - IPMI authentication algorithm.\n            - Please review the Host object documentation for more information on the supported properties\n            - \'https://www.zabbix.com/documentation/3.4/manual/api/reference/host/object\'\n            - Possible values are, C(0) (none), C(1) (MD2), C(2) (MD5), C(4) (straight), C(5) (OEM), C(6) (RMCP+),\n              with -1 being the API default.\n            - Please note that the Zabbix API will treat absent settings as default when updating\n              any of the I(ipmi_)-options; this means that if you attempt to set any of the four\n              options individually, the rest will be reset to default values.\n        version_added: \'2.5\'\n        type: int\n    ipmi_privilege:\n        description:\n            - IPMI privilege level.\n            - Please review the Host object documentation for more information on the supported properties\n            - \'https://www.zabbix.com/documentation/3.4/manual/api/reference/host/object\'\n            - Possible values are C(1) (callback), C(2) (user), C(3) (operator), C(4) (admin), C(5) (OEM), with C(2)\n              being the API default.\n            - also see the last note in the I(ipmi_authtype) documentation\n        version_added: \'2.5\'\n        type: int\n    ipmi_username:\n        description:\n            - IPMI username.\n            - also see the last note in the I(ipmi_authtype) documentation\n        version_added: \'2.5\'\n        type: str\n    ipmi_password:\n        description:\n            - IPMI password.\n            - also see the last note in the I(ipmi_authtype) documentation\n        version_added: \'2.5\'\n        type: str\n    force:\n        description:\n            - Overwrite the host configuration, even if already present.\n        type: bool\n        default: \'yes\'\n        version_added: \'2.0\'\n    macros:\n        description:\n            - List of user macros to assign to the zabbix host.\n            - Providing I(macros=[]) with I(force=yes) will clean all of the existing user macros from the host.\n        type: list\n        elements: dict\n        version_added: \'2.10\'\n        suboptions:\n            macro:\n                description:\n                    - Name of the user macro.\n                    - Can be in zabbix native format "{$MACRO}" or short format "MACRO".\n                type: str\n                required: true\n            value:\n                description:\n                    - Value of the user macro.\n                type: str\n                required: true\n            description:\n                description:\n                    - Description of the user macro.\n                    - Works only with >= Zabbix 4.4.\n                type: str\n                required: false\n                default: \'\'\n        aliases: [ user_macros ]\n    tags:\n        description:\n            - List of host tags to assign to the zabbix host.\n            - Works only with >= Zabbix 4.2.\n            - Providing I(tags=[]) with I(force=yes) will clean all of the tags from the host.\n        type: list\n        elements: dict\n        version_added: \'2.10\'\n        suboptions:\n            tag:\n                description:\n                    - Name of the host tag.\n                type: str\n                required: true\n            value:\n                description:\n                    - Value of the host tag.\n                type: str\n                default: \'\'\n        aliases: [ host_tags ]\n\nextends_documentation_fragment:\n    - zabbix\n'
EXAMPLES = '\n- name: Create a new host or update an existing host\'s info\n  local_action:\n    module: zabbix_host\n    server_url: http://monitor.example.com\n    login_user: username\n    login_password: password\n    host_name: ExampleHost\n    visible_name: ExampleName\n    description: My ExampleHost Description\n    host_groups:\n      - Example group1\n      - Example group2\n    link_templates:\n      - Example template1\n      - Example template2\n    status: enabled\n    state: present\n    inventory_mode: manual\n    inventory_zabbix:\n      tag: "{{ your_tag }}"\n      alias: "{{ your_alias }}"\n      notes: "Special Informations: {{ your_informations | default(\'None\') }}"\n      location: "{{ your_location }}"\n      site_rack: "{{ your_site_rack }}"\n      os: "{{ your_os }}"\n      hardware: "{{ your_hardware }}"\n    ipmi_authtype: 2\n    ipmi_privilege: 4\n    ipmi_username: username\n    ipmi_password: password\n    interfaces:\n      - type: 1\n        main: 1\n        useip: 1\n        ip: 10.xx.xx.xx\n        dns: ""\n        port: "10050"\n      - type: 4\n        main: 1\n        useip: 1\n        ip: 10.xx.xx.xx\n        dns: ""\n        port: "12345"\n    proxy: a.zabbix.proxy\n    macros:\n      - macro: \'{$EXAMPLEMACRO}\'\n        value: ExampleMacroValue\n      - macro: EXAMPLEMACRO2\n        value: ExampleMacroValue2\n        description: Example desc that work only with Zabbix 4.4 and higher\n    tags:\n      - tag: ExampleHostsTag\n      - tag: ExampleHostsTag2\n        value: ExampleTagValue\n\n- name: Update an existing host\'s TLS settings\n  local_action:\n    module: zabbix_host\n    server_url: http://monitor.example.com\n    login_user: username\n    login_password: password\n    host_name: ExampleHost\n    visible_name: ExampleName\n    host_groups:\n      - Example group1\n    tls_psk_identity: test\n    tls_connect: 2\n    tls_psk: 123456789abcdef123456789abcdef12\n'
import atexit
import copy
import traceback
try:
    from zabbix_api import ZabbixAPI
    HAS_ZABBIX_API = True
except ImportError:
    ZBX_IMP_ERR = traceback.format_exc()
    HAS_ZABBIX_API = False
from distutils.version import LooseVersion
from ansible.module_utils.basic import AnsibleModule, missing_required_lib

class Host(object):

    def __init__(self, module, zbx):
        self._module = module
        self._zapi = zbx
        self._zbx_api_version = zbx.api_version()[:5]

    def is_host_exist(self, host_name):
        result = self._zapi.host.get({'filter': {'host': host_name}})
        return result

    def check_host_group_exist(self, group_names):
        for group_name in group_names:
            result = self._zapi.hostgroup.get({'filter': {'name': group_name}})
            if not result:
                self._module.fail_json(msg='Hostgroup not found: %s' % group_name)
        return True

    def get_template_ids(self, template_list):
        template_ids = []
        if template_list is None or len(template_list) == 0:
            return template_ids
        for template in template_list:
            template_list = self._zapi.template.get({'output': 'extend', 'filter': {'host': template}})
            if len(template_list) < 1:
                self._module.fail_json(msg='Template not found: %s' % template)
            else:
                template_id = template_list[0]['templateid']
                template_ids.append(template_id)
        return template_ids

    def add_host(self, host_name, group_ids, status, interfaces, proxy_id, visible_name, description, tls_connect, tls_accept, tls_psk_identity, tls_psk, tls_issuer, tls_subject, ipmi_authtype, ipmi_privilege, ipmi_username, ipmi_password, macros, tags):
        try:
            if self._module.check_mode:
                self._module.exit_json(changed=True)
            parameters = {'host': host_name, 'interfaces': interfaces, 'groups': group_ids, 'status': status, 'tls_connect': tls_connect, 'tls_accept': tls_accept}
            if proxy_id:
                parameters['proxy_hostid'] = proxy_id
            if visible_name:
                parameters['name'] = visible_name
            if tls_psk_identity is not None:
                parameters['tls_psk_identity'] = tls_psk_identity
            if tls_psk is not None:
                parameters['tls_psk'] = tls_psk
            if tls_issuer is not None:
                parameters['tls_issuer'] = tls_issuer
            if tls_subject is not None:
                parameters['tls_subject'] = tls_subject
            if description:
                parameters['description'] = description
            if ipmi_authtype is not None:
                parameters['ipmi_authtype'] = ipmi_authtype
            if ipmi_privilege is not None:
                parameters['ipmi_privilege'] = ipmi_privilege
            if ipmi_username is not None:
                parameters['ipmi_username'] = ipmi_username
            if ipmi_password is not None:
                parameters['ipmi_password'] = ipmi_password
            if macros is not None:
                parameters['macros'] = macros
            if tags is not None:
                parameters['tags'] = tags
            host_list = self._zapi.host.create(parameters)
            if len(host_list) >= 1:
                return host_list['hostids'][0]
        except Exception as e:
            self._module.fail_json(msg='Failed to create host %s: %s' % (host_name, e))

    def update_host(self, host_name, group_ids, status, host_id, interfaces, exist_interface_list, proxy_id, visible_name, description, tls_connect, tls_accept, tls_psk_identity, tls_psk, tls_issuer, tls_subject, ipmi_authtype, ipmi_privilege, ipmi_username, ipmi_password, macros, tags):
        try:
            if self._module.check_mode:
                self._module.exit_json(changed=True)
            parameters = {'hostid': host_id, 'groups': group_ids, 'status': status, 'tls_connect': tls_connect, 'tls_accept': tls_accept}
            if proxy_id >= 0:
                parameters['proxy_hostid'] = proxy_id
            if visible_name:
                parameters['name'] = visible_name
            if tls_psk_identity:
                parameters['tls_psk_identity'] = tls_psk_identity
            if tls_psk:
                parameters['tls_psk'] = tls_psk
            if tls_issuer:
                parameters['tls_issuer'] = tls_issuer
            if tls_subject:
                parameters['tls_subject'] = tls_subject
            if description:
                parameters['description'] = description
            if ipmi_authtype:
                parameters['ipmi_authtype'] = ipmi_authtype
            if ipmi_privilege:
                parameters['ipmi_privilege'] = ipmi_privilege
            if ipmi_username:
                parameters['ipmi_username'] = ipmi_username
            if ipmi_password:
                parameters['ipmi_password'] = ipmi_password
            if macros is not None:
                parameters['macros'] = macros
            if tags is not None:
                parameters['tags'] = tags
            self._zapi.host.update(parameters)
            interface_list_copy = exist_interface_list
            if interfaces:
                for interface in interfaces:
                    flag = False
                    interface_str = interface
                    for exist_interface in exist_interface_list:
                        interface_type = int(interface['type'])
                        exist_interface_type = int(exist_interface['type'])
                        if interface_type == exist_interface_type:
                            interface_str['interfaceid'] = exist_interface['interfaceid']
                            self._zapi.hostinterface.update(interface_str)
                            flag = True
                            interface_list_copy.remove(exist_interface)
                            break
                    if not flag:
                        interface_str['hostid'] = host_id
                        self._zapi.hostinterface.create(interface_str)
                remove_interface_ids = []
                for remove_interface in interface_list_copy:
                    interface_id = remove_interface['interfaceid']
                    remove_interface_ids.append(interface_id)
                if len(remove_interface_ids) > 0:
                    self._zapi.hostinterface.delete(remove_interface_ids)
        except Exception as e:
            self._module.fail_json(msg='Failed to update host %s: %s' % (host_name, e))

    def delete_host(self, host_id, host_name):
        try:
            if self._module.check_mode:
                self._module.exit_json(changed=True)
            self._zapi.host.delete([host_id])
        except Exception as e:
            self._module.fail_json(msg='Failed to delete host %s: %s' % (host_name, e))

    def get_host_by_host_name(self, host_name):
        params = {'output': 'extend', 'selectInventory': 'extend', 'selectMacros': 'extend', 'filter': {'host': [host_name]}}
        if LooseVersion(self._zbx_api_version) >= LooseVersion('4.2.0'):
            params.update({'selectTags': 'extend'})
        host_list = self._zapi.host.get(params)
        if len(host_list) < 1:
            self._module.fail_json(msg='Host not found: %s' % host_name)
        else:
            return host_list[0]

    def get_proxyid_by_proxy_name(self, proxy_name):
        proxy_list = self._zapi.proxy.get({'output': 'extend', 'filter': {'host': [proxy_name]}})
        if len(proxy_list) < 1:
            self._module.fail_json(msg='Proxy not found: %s' % proxy_name)
        else:
            return int(proxy_list[0]['proxyid'])

    def get_group_ids_by_group_names(self, group_names):
        if self.check_host_group_exist(group_names):
            return self._zapi.hostgroup.get({'output': 'groupid', 'filter': {'name': group_names}})

    def get_group_ids_by_host_id(self, host_id):
        return self._zapi.hostgroup.get({'output': 'groupid', 'hostids': host_id})

    def get_host_templates_by_host_id(self, host_id):
        template_ids = []
        template_list = self._zapi.template.get({'output': 'extend', 'hostids': host_id})
        for template in template_list:
            template_ids.append(template['templateid'])
        return template_ids

    def check_interface_properties(self, exist_interface_list, interfaces):
        interfaces_port_list = []
        if interfaces is not None:
            if len(interfaces) >= 1:
                for interface in interfaces:
                    interfaces_port_list.append(str(interface['port']))
        exist_interface_ports = []
        if len(exist_interface_list) >= 1:
            for exist_interface in exist_interface_list:
                exist_interface_ports.append(str(exist_interface['port']))
        if set(interfaces_port_list) != set(exist_interface_ports):
            return True
        for exist_interface in exist_interface_list:
            exit_interface_port = str(exist_interface['port'])
            for interface in interfaces:
                interface_port = str(interface['port'])
                if interface_port == exit_interface_port:
                    for key in interface.keys():
                        if str(exist_interface[key]) != str(interface[key]):
                            return True
        return False

    def get_host_status_by_host(self, host):
        return host['status']

    def check_all_properties(self, host_id, group_ids, status, interfaces, template_ids, exist_interfaces, host, proxy_id, visible_name, description, host_name, inventory_mode, inventory_zabbix, tls_accept, tls_psk_identity, tls_psk, tls_issuer, tls_subject, tls_connect, ipmi_authtype, ipmi_privilege, ipmi_username, ipmi_password, macros, tags):
        exist_host_groups = sorted(self.get_group_ids_by_host_id(host_id), key=lambda k: k['groupid'])
        if sorted(group_ids, key=lambda k: k['groupid']) != exist_host_groups:
            return True
        exist_status = self.get_host_status_by_host(host)
        if int(status) != int(exist_status):
            return True
        if self.check_interface_properties(exist_interfaces, interfaces):
            return True
        exist_template_ids = self.get_host_templates_by_host_id(host_id)
        if set(list(template_ids)) != set(exist_template_ids):
            return True
        if int(host['proxy_hostid']) != int(proxy_id):
            return True
        if visible_name:
            if host['name'] != visible_name:
                return True
        if description:
            if host['description'] != description:
                return True
        if inventory_mode:
            if LooseVersion(self._zbx_api_version) <= LooseVersion('4.4.0'):
                if host['inventory']:
                    if int(host['inventory']['inventory_mode']) != self.inventory_mode_numeric(inventory_mode):
                        return True
                elif inventory_mode != 'disabled':
                    return True
            elif int(host['inventory_mode']) != self.inventory_mode_numeric(inventory_mode):
                return True
        if inventory_zabbix:
            proposed_inventory = copy.deepcopy(host['inventory'])
            proposed_inventory.update(inventory_zabbix)
            if proposed_inventory != host['inventory']:
                return True
        if tls_accept is not None and 'tls_accept' in host:
            if int(host['tls_accept']) != tls_accept:
                return True
        if tls_psk_identity is not None and 'tls_psk_identity' in host:
            if host['tls_psk_identity'] != tls_psk_identity:
                return True
        if tls_psk is not None and 'tls_psk' in host:
            if host['tls_psk'] != tls_psk:
                return True
        if tls_issuer is not None and 'tls_issuer' in host:
            if host['tls_issuer'] != tls_issuer:
                return True
        if tls_subject is not None and 'tls_subject' in host:
            if host['tls_subject'] != tls_subject:
                return True
        if tls_connect is not None and 'tls_connect' in host:
            if int(host['tls_connect']) != tls_connect:
                return True
        if ipmi_authtype is not None:
            if int(host['ipmi_authtype']) != ipmi_authtype:
                return True
        if ipmi_privilege is not None:
            if int(host['ipmi_privilege']) != ipmi_privilege:
                return True
        if ipmi_username is not None:
            if host['ipmi_username'] != ipmi_username:
                return True
        if ipmi_password is not None:
            if host['ipmi_password'] != ipmi_password:
                return True
        if macros is not None and 'macros' in host:
            existing_macros = sorted(host['macros'], key=lambda k: k['macro'])
            for macro in existing_macros:
                macro.pop('hostid', False)
                macro.pop('hostmacroid', False)
            if sorted(macros, key=lambda k: k['macro']) != existing_macros:
                return True
        if tags is not None and 'tags' in host:
            if sorted(tags, key=lambda k: k['tag']) != sorted(host['tags'], key=lambda k: k['tag']):
                return True
        return False

    def link_or_clear_template(self, host_id, template_id_list, tls_connect, tls_accept, tls_psk_identity, tls_psk, tls_issuer, tls_subject, ipmi_authtype, ipmi_privilege, ipmi_username, ipmi_password):
        exist_template_id_list = self.get_host_templates_by_host_id(host_id)
        exist_template_ids = set(exist_template_id_list)
        template_ids = set(template_id_list)
        template_id_list = list(template_ids)
        templates_clear = exist_template_ids.difference(template_ids)
        templates_clear_list = list(templates_clear)
        request_str = {'hostid': host_id, 'templates': template_id_list, 'templates_clear': templates_clear_list, 'tls_connect': tls_connect, 'tls_accept': tls_accept, 'ipmi_authtype': ipmi_authtype, 'ipmi_privilege': ipmi_privilege, 'ipmi_username': ipmi_username, 'ipmi_password': ipmi_password}
        if tls_psk_identity is not None:
            request_str['tls_psk_identity'] = tls_psk_identity
        if tls_psk is not None:
            request_str['tls_psk'] = tls_psk
        if tls_issuer is not None:
            request_str['tls_issuer'] = tls_issuer
        if tls_subject is not None:
            request_str['tls_subject'] = tls_subject
        try:
            if self._module.check_mode:
                self._module.exit_json(changed=True)
            self._zapi.host.update(request_str)
        except Exception as e:
            self._module.fail_json(msg='Failed to link template to host: %s' % e)

    def inventory_mode_numeric(self, inventory_mode):
        if inventory_mode == 'automatic':
            return int(1)
        elif inventory_mode == 'manual':
            return int(0)
        elif inventory_mode == 'disabled':
            return int(-1)
        return inventory_mode

    def update_inventory_mode(self, host_id, inventory_mode):
        if not inventory_mode:
            return
        inventory_mode = self.inventory_mode_numeric(inventory_mode)
        request_str = {'hostid': host_id, 'inventory_mode': inventory_mode}
        try:
            if self._module.check_mode:
                self._module.exit_json(changed=True)
            self._zapi.host.update(request_str)
        except Exception as e:
            self._module.fail_json(msg='Failed to set inventory_mode to host: %s' % e)

    def update_inventory_zabbix(self, host_id, inventory):
        if not inventory:
            return
        request_str = {'hostid': host_id, 'inventory': inventory}
        try:
            if self._module.check_mode:
                self._module.exit_json(changed=True)
            self._zapi.host.update(request_str)
        except Exception as e:
            self._module.fail_json(msg='Failed to set inventory to host: %s' % e)

def main():
    module = AnsibleModule(argument_spec=dict(server_url=dict(type='str', required=True, aliases=['url']), login_user=dict(type='str', required=True), login_password=dict(type='str', required=True, no_log=True), host_name=dict(type='str', required=True), http_login_user=dict(type='str', required=False, default=None), http_login_password=dict(type='str', required=False, default=None, no_log=True), validate_certs=dict(type='bool', required=False, default=True), host_groups=dict(type='list', required=False), link_templates=dict(type='list', required=False), status=dict(type='str', default='enabled', choices=['enabled', 'disabled']), state=dict(type='str', default='present', choices=['present', 'absent']), inventory_mode=dict(type='str', required=False, choices=['automatic', 'manual', 'disabled']), ipmi_authtype=dict(type='int', default=None), ipmi_privilege=dict(type='int', default=None), ipmi_username=dict(type='str', required=False, default=None), ipmi_password=dict(type='str', required=False, default=None, no_log=True), tls_connect=dict(type='int', default=1), tls_accept=dict(type='int', default=1), tls_psk_identity=dict(type='str', required=False), tls_psk=dict(type='str', required=False), ca_cert=dict(type='str', required=False, aliases=['tls_issuer']), tls_subject=dict(type='str', required=False), inventory_zabbix=dict(type='dict', required=False), timeout=dict(type='int', default=10), interfaces=dict(type='list', required=False), force=dict(type='bool', default=True), proxy=dict(type='str', required=False), visible_name=dict(type='str', required=False), description=dict(type='str', required=False), macros=dict(type='list', elements='dict', aliases=['user_macros'], options=dict(macro=dict(type='str', required=True), value=dict(type='str', required=True), description=dict(type='str', required=False, default=''))), tags=dict(type='list', elements='dict', aliases=['host_tags'], options=dict(tag=dict(type='str', required=True), value=dict(type='str', default='')))), supports_check_mode=True)
    if not HAS_ZABBIX_API:
        module.fail_json(msg=missing_required_lib('zabbix-api', url='https://pypi.org/project/zabbix-api/'), exception=ZBX_IMP_ERR)
    server_url = module.params['server_url']
    login_user = module.params['login_user']
    login_password = module.params['login_password']
    http_login_user = module.params['http_login_user']
    http_login_password = module.params['http_login_password']
    validate_certs = module.params['validate_certs']
    host_name = module.params['host_name']
    visible_name = module.params['visible_name']
    description = module.params['description']
    host_groups = module.params['host_groups']
    link_templates = module.params['link_templates']
    inventory_mode = module.params['inventory_mode']
    ipmi_authtype = module.params['ipmi_authtype']
    ipmi_privilege = module.params['ipmi_privilege']
    ipmi_username = module.params['ipmi_username']
    ipmi_password = module.params['ipmi_password']
    tls_connect = module.params['tls_connect']
    tls_accept = module.params['tls_accept']
    tls_psk_identity = module.params['tls_psk_identity']
    tls_psk = module.params['tls_psk']
    tls_issuer = module.params['ca_cert']
    tls_subject = module.params['tls_subject']
    inventory_zabbix = module.params['inventory_zabbix']
    status = module.params['status']
    state = module.params['state']
    timeout = module.params['timeout']
    interfaces = module.params['interfaces']
    force = module.params['force']
    proxy = module.params['proxy']
    macros = module.params['macros']
    tags = module.params['tags']
    status = 1 if status == 'disabled' else 0
    zbx = None
    try:
        zbx = ZabbixAPI(server_url, timeout=timeout, user=http_login_user, passwd=http_login_password, validate_certs=validate_certs)
        zbx.login(login_user, login_password)
        atexit.register(zbx.logout)
    except Exception as e:
        module.fail_json(msg='Failed to connect to Zabbix server: %s' % e)
    host = Host(module, zbx)
    template_ids = []
    if link_templates:
        template_ids = host.get_template_ids(link_templates)
    group_ids = []
    if host_groups:
        group_ids = host.get_group_ids_by_group_names(host_groups)
    ip = ''
    if interfaces:
        for interface in interfaces:
            if 'type' not in interface:
                module.fail_json(msg="(interface) type needs to be specified for interface '%s'." % interface)
            interfacetypes = {'agent': 1, 'snmp': 2, 'ipmi': 3, 'jmx': 4}
            if interface['type'] in interfacetypes.keys():
                interface['type'] = interfacetypes[interface['type']]
            if interface['type'] < 1 or interface['type'] > 4:
                module.fail_json(msg="Interface type can only be 1-4 for interface '%s'." % interface)
            if 'useip' not in interface:
                interface['useip'] = 0
            if 'dns' not in interface:
                if interface['useip'] == 0:
                    module.fail_json(msg="dns needs to be set if useip is 0 on interface '%s'." % interface)
                interface['dns'] = ''
            if 'ip' not in interface:
                if interface['useip'] == 1:
                    module.fail_json(msg="ip needs to be set if useip is 1 on interface '%s'." % interface)
                interface['ip'] = ''
            if 'main' not in interface:
                interface['main'] = 0
            if 'port' in interface and (not isinstance(interface['port'], str)):
                try:
                    interface['port'] = str(interface['port'])
                except ValueError:
                    module.fail_json(msg="port should be convertable to string on interface '%s'." % interface)
            if 'port' not in interface:
                if interface['type'] == 1:
                    interface['port'] = '10050'
                elif interface['type'] == 2:
                    interface['port'] = '161'
                elif interface['type'] == 3:
                    interface['port'] = '623'
                elif interface['type'] == 4:
                    interface['port'] = '12345'
            if interface['type'] == 1:
                ip = interface['ip']
    if macros:
        for macro in macros:
            macro['macro'] = macro['macro'].upper()
            if not macro['macro'].startswith('{$'):
                macro['macro'] = '{$' + macro['macro']
            if not macro['macro'].endswith('}'):
                macro['macro'] = macro['macro'] + '}'
            if LooseVersion(zbx.api_version()[:5]) <= LooseVersion('4.4.0'):
                if 'description' in macro:
                    macro.pop('description', False)
    if proxy:
        proxy_id = host.get_proxyid_by_proxy_name(proxy)
    else:
        proxy_id = 0
    is_host_exist = host.is_host_exist(host_name)
    if is_host_exist:
        zabbix_host_obj = host.get_host_by_host_name(host_name)
        host_id = zabbix_host_obj['hostid']
        if proxy is None:
            proxy_id = int(zabbix_host_obj['proxy_hostid'])
        if state == 'absent':
            host.delete_host(host_id, host_name)
            module.exit_json(changed=True, result='Successfully delete host %s' % host_name)
        else:
            if not host_groups:
                group_ids = host.get_group_ids_by_host_id(host_id)
            exist_interfaces = host._zapi.hostinterface.get({'output': 'extend', 'hostids': host_id})
            if not interfaces:
                interfaces = []
            if not force or not interfaces:
                for interface in copy.deepcopy(exist_interfaces):
                    for key in tuple(interface.keys()):
                        if key in ['interfaceid', 'hostid', 'bulk']:
                            interface.pop(key, None)
                    for index in interface.keys():
                        if index in ['useip', 'main', 'type']:
                            interface[index] = int(interface[index])
                    if interface not in interfaces:
                        interfaces.append(interface)
            if not force or link_templates is None:
                template_ids = list(set(template_ids + host.get_host_templates_by_host_id(host_id)))
            if not force:
                for group_id in host.get_group_ids_by_host_id(host_id):
                    if group_id not in group_ids:
                        group_ids.append(group_id)
                if macros is not None and 'macros' in zabbix_host_obj.keys():
                    provided_macros = [m['macro'] for m in macros]
                    existing_macros = zabbix_host_obj['macros']
                    for macro in existing_macros:
                        if macro['macro'] not in provided_macros:
                            macros.append(macro)
                if tags is not None and 'tags' in zabbix_host_obj.keys():
                    provided_tags = [t['tag'] for t in tags]
                    existing_tags = zabbix_host_obj['tags']
                    for tag in existing_tags:
                        if tag['tag'] not in provided_tags:
                            tags.append(tag)
            if host.check_all_properties(host_id, group_ids, status, interfaces, template_ids, exist_interfaces, zabbix_host_obj, proxy_id, visible_name, description, host_name, inventory_mode, inventory_zabbix, tls_accept, tls_psk_identity, tls_psk, tls_issuer, tls_subject, tls_connect, ipmi_authtype, ipmi_privilege, ipmi_username, ipmi_password, macros, tags):
                host.update_host(host_name, group_ids, status, host_id, interfaces, exist_interfaces, proxy_id, visible_name, description, tls_connect, tls_accept, tls_psk_identity, tls_psk, tls_issuer, tls_subject, ipmi_authtype, ipmi_privilege, ipmi_username, ipmi_password, macros, tags)
                host.link_or_clear_template(host_id, template_ids, tls_connect, tls_accept, tls_psk_identity, tls_psk, tls_issuer, tls_subject, ipmi_authtype, ipmi_privilege, ipmi_username, ipmi_password)
                host.update_inventory_mode(host_id, inventory_mode)
                host.update_inventory_zabbix(host_id, inventory_zabbix)
                module.exit_json(changed=True, result="Successfully update host %s (%s) and linked with template '%s'" % (host_name, ip, link_templates))
            else:
                module.exit_json(changed=False)
    else:
        if state == 'absent':
            module.exit_json(changed=False)
        if not group_ids:
            module.fail_json(msg="Specify at least one group for creating host '%s'." % host_name)
        if not interfaces or (interfaces and len(interfaces) == 0):
            module.fail_json(msg="Specify at least one interface for creating host '%s'." % host_name)
        host_id = host.add_host(host_name, group_ids, status, interfaces, proxy_id, visible_name, description, tls_connect, tls_accept, tls_psk_identity, tls_psk, tls_issuer, tls_subject, ipmi_authtype, ipmi_privilege, ipmi_username, ipmi_password, macros, tags)
        host.link_or_clear_template(host_id, template_ids, tls_connect, tls_accept, tls_psk_identity, tls_psk, tls_issuer, tls_subject, ipmi_authtype, ipmi_privilege, ipmi_username, ipmi_password)
        host.update_inventory_mode(host_id, inventory_mode)
        host.update_inventory_zabbix(host_id, inventory_zabbix)
        module.exit_json(changed=True, result="Successfully added host %s (%s) and linked with template '%s'" % (host_name, ip, link_templates))
if __name__ == '__main__':
    main()

def test_Host_is_host_exist():
    ret = Host().is_host_exist()

def test_Host_check_host_group_exist():
    ret = Host().check_host_group_exist()

def test_Host_get_template_ids():
    ret = Host().get_template_ids()

def test_Host_add_host():
    ret = Host().add_host()

def test_Host_update_host():
    ret = Host().update_host()

def test_Host_delete_host():
    ret = Host().delete_host()

def test_Host_get_host_by_host_name():
    ret = Host().get_host_by_host_name()

def test_Host_get_proxyid_by_proxy_name():
    ret = Host().get_proxyid_by_proxy_name()

def test_Host_get_group_ids_by_group_names():
    ret = Host().get_group_ids_by_group_names()

def test_Host_get_group_ids_by_host_id():
    ret = Host().get_group_ids_by_host_id()

def test_Host_get_host_templates_by_host_id():
    ret = Host().get_host_templates_by_host_id()

def test_Host_check_interface_properties():
    ret = Host().check_interface_properties()

def test_Host_get_host_status_by_host():
    ret = Host().get_host_status_by_host()

def test_Host_check_all_properties():
    ret = Host().check_all_properties()

def test_Host_link_or_clear_template():
    ret = Host().link_or_clear_template()

def test_Host_inventory_mode_numeric():
    ret = Host().inventory_mode_numeric()

def test_Host_update_inventory_mode():
    ret = Host().update_inventory_mode()

def test_Host_update_inventory_zabbix():
    ret = Host().update_inventory_zabbix()