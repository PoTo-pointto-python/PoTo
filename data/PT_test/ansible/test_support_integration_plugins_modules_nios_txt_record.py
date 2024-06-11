from __future__ import absolute_import, division, print_function
__metaclass__ = type
ANSIBLE_METADATA = {'metadata_version': '1.1', 'status': ['preview'], 'supported_by': 'certified'}
DOCUMENTATION = '\n---\nmodule: nios_txt_record\nversion_added: "2.7"\nauthor: "Corey Wanless (@coreywan)"\nshort_description: Configure Infoblox NIOS txt records\ndescription:\n  - Adds and/or removes instances of txt record objects from\n    Infoblox NIOS servers.  This module manages NIOS C(record:txt) objects\n    using the Infoblox WAPI interface over REST.\nrequirements:\n  - infoblox_client\nextends_documentation_fragment: nios\noptions:\n  name:\n    description:\n      - Specifies the fully qualified hostname to add or remove from\n        the system\n    required: true\n  view:\n    description:\n      - Sets the DNS view to associate this tst record with.  The DNS\n        view must already be configured on the system\n    required: true\n    default: default\n    aliases:\n      - dns_view\n  text:\n    description:\n      - Text associated with the record. It can contain up to 255 bytes\n        per substring, up to a total of 512 bytes. To enter leading,\n        trailing, or embedded spaces in the text, add quotes around the\n        text to preserve the spaces.\n    required: true\n  ttl:\n    description:\n      - Configures the TTL to be associated with this tst record\n  extattrs:\n    description:\n      - Allows for the configuration of Extensible Attributes on the\n        instance of the object.  This argument accepts a set of key / value\n        pairs for configuration.\n  comment:\n    description:\n      - Configures a text string comment to be associated with the instance\n        of this object.  The provided text string will be configured on the\n        object instance.\n  state:\n    description:\n      - Configures the intended state of the instance of the object on\n        the NIOS server.  When this value is set to C(present), the object\n        is configured on the device and when this value is set to C(absent)\n        the value is removed (if necessary) from the device.\n    default: present\n    choices:\n      - present\n      - absent\n'
EXAMPLES = '\n    - name: Ensure a text Record Exists\n      nios_txt_record:\n        name: fqdn.txt.record.com\n        text: mytext\n        state: present\n        view: External\n        provider:\n          host: "{{ inventory_hostname_short }}"\n          username: admin\n          password: admin\n\n    - name: Ensure a text Record does not exist\n      nios_txt_record:\n        name: fqdn.txt.record.com\n        text: mytext\n        state: absent\n        view: External\n        provider:\n          host: "{{ inventory_hostname_short }}"\n          username: admin\n          password: admin\n'
RETURN = ' # '
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.six import iteritems
from ansible.module_utils.net_tools.nios.api import WapiModule

def main():
    """ Main entry point for module execution
    """
    ib_spec = dict(name=dict(required=True, ib_req=True), view=dict(default='default', aliases=['dns_view'], ib_req=True), text=dict(ib_req=True), ttl=dict(type='int'), extattrs=dict(type='dict'), comment=dict())
    argument_spec = dict(provider=dict(required=True), state=dict(default='present', choices=['present', 'absent']))
    argument_spec.update(ib_spec)
    argument_spec.update(WapiModule.provider_spec)
    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    wapi = WapiModule(module)
    result = wapi.run('record:txt', ib_spec)
    module.exit_json(**result)
if __name__ == '__main__':
    main()