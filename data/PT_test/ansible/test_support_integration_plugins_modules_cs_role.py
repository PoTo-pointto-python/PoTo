from __future__ import absolute_import, division, print_function
__metaclass__ = type
ANSIBLE_METADATA = {'metadata_version': '1.1', 'status': ['preview'], 'supported_by': 'community'}
DOCUMENTATION = "\n---\nmodule: cs_role\nshort_description: Manages user roles on Apache CloudStack based clouds.\ndescription:\n  - Create, update, delete user roles.\nversion_added: '2.3'\nauthor: René Moser (@resmo)\noptions:\n  name:\n    description:\n      - Name of the role.\n    type: str\n    required: true\n  uuid:\n    description:\n      - ID of the role.\n      - If provided, I(uuid) is used as key.\n    type: str\n    aliases: [ id ]\n  role_type:\n    description:\n      - Type of the role.\n      - Only considered for creation.\n    type: str\n    default: User\n    choices: [ User, DomainAdmin, ResourceAdmin, Admin ]\n  description:\n    description:\n      - Description of the role.\n    type: str\n  state:\n    description:\n      - State of the role.\n    type: str\n    default: present\n    choices: [ present, absent ]\nextends_documentation_fragment: cloudstack\n"
EXAMPLES = '\n- name: Ensure an user role is present\n  cs_role:\n    name: myrole_user\n  delegate_to: localhost\n\n- name: Ensure a role having particular ID is named as myrole_user\n  cs_role:\n    name: myrole_user\n    id: 04589590-ac63-4ffc-93f5-b698b8ac38b6\n  delegate_to: localhost\n\n- name: Ensure a role is absent\n  cs_role:\n    name: myrole_user\n    state: absent\n  delegate_to: localhost\n'
RETURN = '\n---\nid:\n  description: UUID of the role.\n  returned: success\n  type: str\n  sample: 04589590-ac63-4ffc-93f5-b698b8ac38b6\nname:\n  description: Name of the role.\n  returned: success\n  type: str\n  sample: myrole\ndescription:\n  description: Description of the role.\n  returned: success\n  type: str\n  sample: "This is my role description"\nrole_type:\n  description: Type of the role.\n  returned: success\n  type: str\n  sample: User\n'
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.cloudstack import AnsibleCloudStack, cs_argument_spec, cs_required_together

class AnsibleCloudStackRole(AnsibleCloudStack):

    def __init__(self, module):
        super(AnsibleCloudStackRole, self).__init__(module)
        self.returns = {'type': 'role_type'}

    def get_role(self):
        uuid = self.module.params.get('uuid')
        if uuid:
            args = {'id': uuid}
            roles = self.query_api('listRoles', **args)
            if roles:
                return roles['role'][0]
        else:
            args = {'name': self.module.params.get('name')}
            roles = self.query_api('listRoles', **args)
            if roles:
                return roles['role'][0]
        return None

    def present_role(self):
        role = self.get_role()
        if role:
            role = self._update_role(role)
        else:
            role = self._create_role(role)
        return role

    def _create_role(self, role):
        self.result['changed'] = True
        args = {'name': self.module.params.get('name'), 'type': self.module.params.get('role_type'), 'description': self.module.params.get('description')}
        if not self.module.check_mode:
            res = self.query_api('createRole', **args)
            role = res['role']
        return role

    def _update_role(self, role):
        args = {'id': role['id'], 'name': self.module.params.get('name'), 'description': self.module.params.get('description')}
        if self.has_changed(args, role):
            self.result['changed'] = True
            if not self.module.check_mode:
                res = self.query_api('updateRole', **args)
                if 'role' not in res:
                    role = self.get_role()
                else:
                    role = res['role']
        return role

    def absent_role(self):
        role = self.get_role()
        if role:
            self.result['changed'] = True
            args = {'id': role['id']}
            if not self.module.check_mode:
                self.query_api('deleteRole', **args)
        return role

def main():
    argument_spec = cs_argument_spec()
    argument_spec.update(dict(uuid=dict(aliases=['id']), name=dict(required=True), description=dict(), role_type=dict(choices=['User', 'DomainAdmin', 'ResourceAdmin', 'Admin'], default='User'), state=dict(choices=['present', 'absent'], default='present')))
    module = AnsibleModule(argument_spec=argument_spec, required_together=cs_required_together(), supports_check_mode=True)
    acs_role = AnsibleCloudStackRole(module)
    state = module.params.get('state')
    if state == 'absent':
        role = acs_role.absent_role()
    else:
        role = acs_role.present_role()
    result = acs_role.get_result(role)
    module.exit_json(**result)
if __name__ == '__main__':
    main()

def test_AnsibleCloudStackRole_get_role():
    ret = AnsibleCloudStackRole().get_role()

def test_AnsibleCloudStackRole_present_role():
    ret = AnsibleCloudStackRole().present_role()

def test_AnsibleCloudStackRole__create_role():
    ret = AnsibleCloudStackRole()._create_role()

def test_AnsibleCloudStackRole__update_role():
    ret = AnsibleCloudStackRole()._update_role()

def test_AnsibleCloudStackRole_absent_role():
    ret = AnsibleCloudStackRole().absent_role()