from __future__ import absolute_import, division, print_function
__metaclass__ = type
DOCUMENTATION = 'author: Ansible Networking Team\nnetconf: default\nshort_description: Use default netconf plugin to run standard netconf commands as\n  per RFC\ndescription:\n- This default plugin provides low level abstraction apis for sending and receiving\n  netconf commands as per Netconf RFC specification.\noptions:\n  ncclient_device_handler:\n    type: str\n    default: default\n    description:\n    - Specifies the ncclient device handler name for network os that support default\n      netconf implementation as per Netconf RFC specification. To identify the ncclient\n      device handler name refer ncclient library documentation.\n'
import json
from ansible.module_utils._text import to_text
from ansible.plugins.netconf import NetconfBase

class Netconf(NetconfBase):

    def get_text(self, ele, tag):
        try:
            return to_text(ele.find(tag).text, errors='surrogate_then_replace').strip()
        except AttributeError:
            pass

    def get_device_info(self):
        device_info = dict()
        device_info['network_os'] = 'default'
        return device_info

    def get_capabilities(self):
        result = dict()
        result['rpc'] = self.get_base_rpc()
        result['network_api'] = 'netconf'
        result['device_info'] = self.get_device_info()
        result['server_capabilities'] = [c for c in self.m.server_capabilities]
        result['client_capabilities'] = [c for c in self.m.client_capabilities]
        result['session_id'] = self.m.session_id
        result['device_operations'] = self.get_device_operations(result['server_capabilities'])
        return json.dumps(result)

def test_Netconf_get_text():
    ret = Netconf().get_text()

def test_Netconf_get_device_info():
    ret = Netconf().get_device_info()

def test_Netconf_get_capabilities():
    ret = Netconf().get_capabilities()