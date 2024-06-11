from __future__ import absolute_import, division, print_function
__metaclass__ = type
ANSIBLE_METADATA = {'metadata_version': '1.1', 'status': ['preview'], 'supported_by': 'community'}
DOCUMENTATION = '\n---\nmodule: vmware_guest_custom_attributes\nshort_description: Manage custom attributes from VMware for the given virtual machine\ndescription:\n    - This module can be used to add, remove and update custom attributes for the given virtual machine.\nversion_added: 2.7\nauthor:\n    - Jimmy Conner (@cigamit)\n    - Abhijeet Kasurde (@Akasurde)\nnotes:\n    - Tested on vSphere 6.5\nrequirements:\n    - "python >= 2.6"\n    - PyVmomi\noptions:\n   name:\n     description:\n     - Name of the virtual machine to work with.\n     - This is required parameter, if C(uuid) or C(moid) is not supplied.\n     type: str\n   state:\n     description:\n     - The action to take.\n     - If set to C(present), then custom attribute is added or updated.\n     - If set to C(absent), then custom attribute is removed.\n     default: \'present\'\n     choices: [\'present\', \'absent\']\n     type: str\n   uuid:\n     description:\n     - UUID of the virtual machine to manage if known. This is VMware\'s unique identifier.\n     - This is required parameter, if C(name) or C(moid) is not supplied.\n     type: str\n   moid:\n     description:\n     - Managed Object ID of the instance to manage if known, this is a unique identifier only within a single vCenter instance.\n     - This is required if C(name) or C(uuid) is not supplied.\n     version_added: \'2.9\'\n     type: str\n   use_instance_uuid:\n     description:\n     - Whether to use the VMware instance UUID rather than the BIOS UUID.\n     default: no\n     type: bool\n     version_added: \'2.8\'\n   folder:\n     description:\n     - Absolute path to find an existing guest.\n     - This is required parameter, if C(name) is supplied and multiple virtual machines with same name are found.\n     type: str\n   datacenter:\n     description:\n     - Datacenter name where the virtual machine is located in.\n     required: True\n     type: str\n   attributes:\n     description:\n     - A list of name and value of custom attributes that needs to be manage.\n     - Value of custom attribute is not required and will be ignored, if C(state) is set to C(absent).\n     default: []\n     type: list\nextends_documentation_fragment: vmware.documentation\n'
EXAMPLES = '\n- name: Add virtual machine custom attributes\n  vmware_guest_custom_attributes:\n    hostname: "{{ vcenter_hostname }}"\n    username: "{{ vcenter_username }}"\n    password: "{{ vcenter_password }}"\n    uuid: 421e4592-c069-924d-ce20-7e7533fab926\n    state: present\n    attributes:\n      - name: MyAttribute\n        value: MyValue\n  delegate_to: localhost\n  register: attributes\n\n- name: Add multiple virtual machine custom attributes\n  vmware_guest_custom_attributes:\n    hostname: "{{ vcenter_hostname }}"\n    username: "{{ vcenter_username }}"\n    password: "{{ vcenter_password }}"\n    uuid: 421e4592-c069-924d-ce20-7e7533fab926\n    state: present\n    attributes:\n      - name: MyAttribute\n        value: MyValue\n      - name: MyAttribute2\n        value: MyValue2\n  delegate_to: localhost\n  register: attributes\n\n- name: Remove virtual machine Attribute\n  vmware_guest_custom_attributes:\n    hostname: "{{ vcenter_hostname }}"\n    username: "{{ vcenter_username }}"\n    password: "{{ vcenter_password }}"\n    uuid: 421e4592-c069-924d-ce20-7e7533fab926\n    state: absent\n    attributes:\n      - name: MyAttribute\n  delegate_to: localhost\n  register: attributes\n\n- name: Remove virtual machine Attribute using Virtual Machine MoID\n  vmware_guest_custom_attributes:\n    hostname: "{{ vcenter_hostname }}"\n    username: "{{ vcenter_username }}"\n    password: "{{ vcenter_password }}"\n    moid: vm-42\n    state: absent\n    attributes:\n      - name: MyAttribute\n  delegate_to: localhost\n  register: attributes\n'
RETURN = '\ncustom_attributes:\n    description: metadata about the virtual machine attributes\n    returned: always\n    type: dict\n    sample: {\n        "mycustom": "my_custom_value",\n        "mycustom_2": "my_custom_value_2",\n        "sample_1": "sample_1_value",\n        "sample_2": "sample_2_value",\n        "sample_3": "sample_3_value"\n    }\n'
try:
    from pyVmomi import vim
except ImportError:
    pass
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.vmware import PyVmomi, vmware_argument_spec

class VmAttributeManager(PyVmomi):

    def __init__(self, module):
        super(VmAttributeManager, self).__init__(module)

    def set_custom_field(self, vm, user_fields):
        result_fields = dict()
        change_list = list()
        changed = False
        for field in user_fields:
            field_key = self.check_exists(field['name'])
            found = False
            field_value = field.get('value', '')
            for (k, v) in [(x.name, v.value) for x in self.custom_field_mgr for v in vm.customValue if x.key == v.key]:
                if k == field['name']:
                    found = True
                    if v != field_value:
                        if not self.module.check_mode:
                            self.content.customFieldsManager.SetField(entity=vm, key=field_key.key, value=field_value)
                            result_fields[k] = field_value
                        change_list.append(True)
            if not found and field_value != '':
                if not field_key and (not self.module.check_mode):
                    field_key = self.content.customFieldsManager.AddFieldDefinition(name=field['name'], moType=vim.VirtualMachine)
                change_list.append(True)
                if not self.module.check_mode:
                    self.content.customFieldsManager.SetField(entity=vm, key=field_key.key, value=field_value)
                result_fields[field['name']] = field_value
        if any(change_list):
            changed = True
        return {'changed': changed, 'failed': False, 'custom_attributes': result_fields}

    def check_exists(self, field):
        for x in self.custom_field_mgr:
            if x.name == field:
                return x
        return False

def main():
    argument_spec = vmware_argument_spec()
    argument_spec.update(datacenter=dict(type='str'), name=dict(type='str'), folder=dict(type='str'), uuid=dict(type='str'), moid=dict(type='str'), use_instance_uuid=dict(type='bool', default=False), state=dict(type='str', default='present', choices=['absent', 'present']), attributes=dict(type='list', default=[], options=dict(name=dict(type='str', required=True), value=dict(type='str'))))
    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True, required_one_of=[['name', 'uuid', 'moid']])
    if module.params.get('folder'):
        module.params['folder'] = module.params['folder'].rstrip('/')
    pyv = VmAttributeManager(module)
    results = {'changed': False, 'failed': False, 'instance': dict()}
    vm = pyv.get_vm()
    if vm:
        if module.params['state'] == 'present':
            results = pyv.set_custom_field(vm, module.params['attributes'])
        elif module.params['state'] == 'absent':
            results = pyv.set_custom_field(vm, module.params['attributes'])
        module.exit_json(**results)
    else:
        vm_id = module.params.get('name') or module.params.get('uuid') or module.params.get('moid')
        module.fail_json(msg='Unable to manage custom attributes for non-existing virtual machine %s' % vm_id)
if __name__ == '__main__':
    main()

def test_VmAttributeManager_set_custom_field():
    ret = VmAttributeManager().set_custom_field()

def test_VmAttributeManager_check_exists():
    ret = VmAttributeManager().check_exists()