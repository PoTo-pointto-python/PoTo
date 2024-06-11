from __future__ import absolute_import, division, print_function
__metaclass__ = type
ANSIBLE_METADATA = {'metadata_version': '1.1', 'status': ['preview'], 'supported_by': 'community'}
DOCUMENTATION = "\n---\nmodule: cs_role_permission\nshort_description: Manages role permissions on Apache CloudStack based clouds.\ndescription:\n    - Create, update and remove CloudStack role permissions.\n    - Managing role permissions only supported in CloudStack >= 4.9.\nversion_added: '2.6'\nauthor: David Passante (@dpassante)\noptions:\n  name:\n    description:\n      - The API name of the permission.\n    type: str\n    required: true\n  role:\n    description:\n      - Name or ID of the role.\n    type: str\n    required: true\n  permission:\n    description:\n      - The rule permission, allow or deny. Defaulted to deny.\n    type: str\n    choices: [ allow, deny ]\n    default: deny\n  state:\n    description:\n      - State of the role permission.\n    type: str\n    choices: [ present, absent ]\n    default: present\n  description:\n    description:\n      - The description of the role permission.\n    type: str\n  parent:\n    description:\n      - The parent role permission uuid. use 0 to move this rule at the top of the list.\n    type: str\nextends_documentation_fragment: cloudstack\n"
EXAMPLES = '\n- name: Create a role permission\n  cs_role_permission:\n    role: My_Custom_role\n    name: createVPC\n    permission: allow\n    description: My comments\n  delegate_to: localhost\n\n- name: Remove a role permission\n  cs_role_permission:\n    state: absent\n    role: My_Custom_role\n    name: createVPC\n  delegate_to: localhost\n\n- name: Update a system role permission\n  cs_role_permission:\n    role: Domain Admin\n    name: createVPC\n    permission: deny\n  delegate_to: localhost\n\n- name: Update rules order. Move the rule at the top of list\n  cs_role_permission:\n    role: Domain Admin\n    name: createVPC\n    parent: 0\n  delegate_to: localhost\n'
RETURN = '\n---\nid:\n  description: The ID of the role permission.\n  returned: success\n  type: str\n  sample: a6f7a5fc-43f8-11e5-a151-feff819cdc9f\nname:\n  description: The API name of the permission.\n  returned: success\n  type: str\n  sample: createVPC\npermission:\n  description: The permission type of the api name.\n  returned: success\n  type: str\n  sample: allow\nrole_id:\n  description: The ID of the role to which the role permission belongs.\n  returned: success\n  type: str\n  sample: c6f7a5fc-43f8-11e5-a151-feff819cdc7f\ndescription:\n  description: The description of the role permission\n  returned: success\n  type: str\n  sample: Deny createVPC for users\n'
from distutils.version import LooseVersion
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.cloudstack import AnsibleCloudStack, cs_argument_spec, cs_required_together

class AnsibleCloudStackRolePermission(AnsibleCloudStack):

    def __init__(self, module):
        super(AnsibleCloudStackRolePermission, self).__init__(module)
        cloudstack_min_version = LooseVersion('4.9.2')
        self.returns = {'id': 'id', 'roleid': 'role_id', 'rule': 'name', 'permission': 'permission', 'description': 'description'}
        self.role_permission = None
        self.cloudstack_version = self._cloudstack_ver()
        if self.cloudstack_version < cloudstack_min_version:
            self.fail_json(msg='This module requires CloudStack >= %s.' % cloudstack_min_version)

    def _cloudstack_ver(self):
        capabilities = self.get_capabilities()
        return LooseVersion(capabilities['cloudstackversion'])

    def _get_role_id(self):
        role = self.module.params.get('role')
        if not role:
            return None
        res = self.query_api('listRoles')
        roles = res['role']
        if roles:
            for r in roles:
                if role in [r['name'], r['id']]:
                    return r['id']
        self.fail_json(msg="Role '%s' not found" % role)

    def _get_role_perm(self):
        role_permission = self.role_permission
        args = {'roleid': self._get_role_id()}
        rp = self.query_api('listRolePermissions', **args)
        if rp:
            role_permission = rp['rolepermission']
        return role_permission

    def _get_rule(self, rule=None):
        if not rule:
            rule = self.module.params.get('name')
        if self._get_role_perm():
            for _rule in self._get_role_perm():
                if rule == _rule['rule'] or rule == _rule['id']:
                    return _rule
        return None

    def _get_rule_order(self):
        perms = self._get_role_perm()
        rules = []
        if perms:
            for (i, rule) in enumerate(perms):
                rules.append(rule['id'])
        return rules

    def replace_rule(self):
        old_rule = self._get_rule()
        if old_rule:
            rules_order = self._get_rule_order()
            old_pos = rules_order.index(old_rule['id'])
            self.remove_role_perm()
            new_rule = self.create_role_perm()
            if new_rule:
                perm_order = self.order_permissions(int(old_pos - 1), new_rule['id'])
                return perm_order
        return None

    def order_permissions(self, parent, rule_id):
        rules = self._get_rule_order()
        if isinstance(parent, int):
            parent_pos = parent
        elif parent == '0':
            parent_pos = -1
        else:
            parent_rule = self._get_rule(parent)
            if not parent_rule:
                self.fail_json(msg="Parent rule '%s' not found" % parent)
            parent_pos = rules.index(parent_rule['id'])
        r_id = rules.pop(rules.index(rule_id))
        rules.insert(parent_pos + 1, r_id)
        rules = ','.join(map(str, rules))
        return rules

    def create_or_update_role_perm(self):
        role_permission = self._get_rule()
        if not role_permission:
            role_permission = self.create_role_perm()
        else:
            role_permission = self.update_role_perm(role_permission)
        return role_permission

    def create_role_perm(self):
        role_permission = None
        self.result['changed'] = True
        args = {'rule': self.module.params.get('name'), 'description': self.module.params.get('description'), 'roleid': self._get_role_id(), 'permission': self.module.params.get('permission')}
        if not self.module.check_mode:
            res = self.query_api('createRolePermission', **args)
            role_permission = res['rolepermission']
        return role_permission

    def update_role_perm(self, role_perm):
        perm_order = None
        if not self.module.params.get('parent'):
            args = {'ruleid': role_perm['id'], 'roleid': role_perm['roleid'], 'permission': self.module.params.get('permission')}
            if self.has_changed(args, role_perm, only_keys=['permission']):
                self.result['changed'] = True
                if not self.module.check_mode:
                    if self.cloudstack_version >= LooseVersion('4.11.0'):
                        self.query_api('updateRolePermission', **args)
                        role_perm = self._get_rule()
                    else:
                        perm_order = self.replace_rule()
        else:
            perm_order = self.order_permissions(self.module.params.get('parent'), role_perm['id'])
        if perm_order:
            args = {'roleid': role_perm['roleid'], 'ruleorder': perm_order}
            self.result['changed'] = True
            if not self.module.check_mode:
                self.query_api('updateRolePermission', **args)
                role_perm = self._get_rule()
        return role_perm

    def remove_role_perm(self):
        role_permission = self._get_rule()
        if role_permission:
            self.result['changed'] = True
            args = {'id': role_permission['id']}
            if not self.module.check_mode:
                self.query_api('deleteRolePermission', **args)
        return role_permission

def main():
    argument_spec = cs_argument_spec()
    argument_spec.update(dict(role=dict(required=True), name=dict(required=True), permission=dict(choices=['allow', 'deny'], default='deny'), description=dict(), state=dict(choices=['present', 'absent'], default='present'), parent=dict()))
    module = AnsibleModule(argument_spec=argument_spec, required_together=cs_required_together(), mutually_exclusive=(['permission', 'parent'],), supports_check_mode=True)
    acs_role_perm = AnsibleCloudStackRolePermission(module)
    state = module.params.get('state')
    if state in ['absent']:
        role_permission = acs_role_perm.remove_role_perm()
    else:
        role_permission = acs_role_perm.create_or_update_role_perm()
    result = acs_role_perm.get_result(role_permission)
    module.exit_json(**result)
if __name__ == '__main__':
    main()

def test_AnsibleCloudStackRolePermission__cloudstack_ver():
    ret = AnsibleCloudStackRolePermission()._cloudstack_ver()

def test_AnsibleCloudStackRolePermission__get_role_id():
    ret = AnsibleCloudStackRolePermission()._get_role_id()

def test_AnsibleCloudStackRolePermission__get_role_perm():
    ret = AnsibleCloudStackRolePermission()._get_role_perm()

def test_AnsibleCloudStackRolePermission__get_rule():
    ret = AnsibleCloudStackRolePermission()._get_rule()

def test_AnsibleCloudStackRolePermission__get_rule_order():
    ret = AnsibleCloudStackRolePermission()._get_rule_order()

def test_AnsibleCloudStackRolePermission_replace_rule():
    ret = AnsibleCloudStackRolePermission().replace_rule()

def test_AnsibleCloudStackRolePermission_order_permissions():
    ret = AnsibleCloudStackRolePermission().order_permissions()

def test_AnsibleCloudStackRolePermission_create_or_update_role_perm():
    ret = AnsibleCloudStackRolePermission().create_or_update_role_perm()

def test_AnsibleCloudStackRolePermission_create_role_perm():
    ret = AnsibleCloudStackRolePermission().create_role_perm()

def test_AnsibleCloudStackRolePermission_update_role_perm():
    ret = AnsibleCloudStackRolePermission().update_role_perm()

def test_AnsibleCloudStackRolePermission_remove_role_perm():
    ret = AnsibleCloudStackRolePermission().remove_role_perm()