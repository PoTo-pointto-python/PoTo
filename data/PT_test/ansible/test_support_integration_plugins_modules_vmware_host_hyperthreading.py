from __future__ import absolute_import, division, print_function
__metaclass__ = type
ANSIBLE_METADATA = {'metadata_version': '1.1', 'status': ['preview'], 'supported_by': 'community'}
DOCUMENTATION = "\n---\nmodule: vmware_host_hyperthreading\nshort_description: Enables/Disables Hyperthreading optimization for an ESXi host system\ndescription:\n- This module can be used to enable or disable Hyperthreading optimization for ESXi host systems in given vCenter infrastructure.\n- It also checks if Hyperthreading is activated/deactivated and if the host needs to be restarted.\n- The module informs the user if Hyperthreading is enabled but inactive because the processor is vulnerable to L1 Terminal Fault (L1TF).\nversion_added: 2.8\nauthor:\n- Christian Kotte (@ckotte)\nnotes:\n- Tested on vSphere 6.5\nrequirements:\n- python >= 2.6\n- PyVmomi\noptions:\n  state:\n     description:\n        - Enable or disable Hyperthreading.\n        - You need to reboot the ESXi host if you change the configuration.\n        - Make sure that Hyperthreading is enabled in the BIOS. Otherwise, it will be enabled, but never activated.\n     type: str\n     choices: [ enabled, disabled ]\n     default: 'enabled'\n  esxi_hostname:\n    description:\n    - Name of the host system to work with.\n    - This parameter is required if C(cluster_name) is not specified.\n    type: str\n  cluster_name:\n    description:\n    - Name of the cluster from which all host systems will be used.\n    - This parameter is required if C(esxi_hostname) is not specified.\n    type: str\nextends_documentation_fragment: vmware.documentation\n"
EXAMPLES = "\n- name: Enable Hyperthreading for an host system\n  vmware_host_hyperthreading:\n    hostname: '{{ vcenter_hostname }}'\n    username: '{{ vcenter_username }}'\n    password: '{{ vcenter_password }}'\n    esxi_hostname: '{{ esxi_hostname }}'\n    state: enabled\n    validate_certs: no\n  delegate_to: localhost\n\n- name: Disable Hyperthreading for an host system\n  vmware_host_hyperthreading:\n    hostname: '{{ vcenter_hostname }}'\n    username: '{{ vcenter_username }}'\n    password: '{{ vcenter_password }}'\n    esxi_hostname: '{{ esxi_hostname }}'\n    state: disabled\n    validate_certs: no\n  delegate_to: localhost\n\n- name: Disable Hyperthreading for all host systems from cluster\n  vmware_host_hyperthreading:\n    hostname: '{{ vcenter_hostname }}'\n    username: '{{ vcenter_username }}'\n    password: '{{ vcenter_password }}'\n    cluster_name: '{{ cluster_name }}'\n    state: disabled\n    validate_certs: no\n  delegate_to: localhost\n"
RETURN = '\nresults:\n    description: metadata about host system\'s Hyperthreading configuration\n    returned: always\n    type: dict\n    sample: {\n        "esxi01": {\n            "msg": "Hyperthreading is already enabled and active for host \'esxi01\'",\n            "state_current": "active",\n            "state": "enabled",\n        },\n    }\n'
try:
    from pyVmomi import vim, vmodl
except ImportError:
    pass
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.vmware import PyVmomi, vmware_argument_spec
from ansible.module_utils._text import to_native

class VmwareHostHyperthreading(PyVmomi):
    """Manage Hyperthreading for an ESXi host system"""

    def __init__(self, module):
        super(VmwareHostHyperthreading, self).__init__(module)
        cluster_name = self.params.get('cluster_name')
        esxi_host_name = self.params.get('esxi_hostname')
        self.hosts = self.get_all_host_objs(cluster_name=cluster_name, esxi_host_name=esxi_host_name)
        if not self.hosts:
            self.module.fail_json(msg='Failed to find host system.')

    def ensure(self):
        """Manage Hyperthreading for an ESXi host system"""
        results = dict(changed=False, result=dict())
        desired_state = self.params.get('state')
        host_change_list = []
        for host in self.hosts:
            changed = False
            results['result'][host.name] = dict(msg='')
            hyperthreading_info = host.config.hyperThread
            results['result'][host.name]['state'] = desired_state
            if desired_state == 'enabled':
                if hyperthreading_info.config:
                    if hyperthreading_info.active:
                        results['result'][host.name]['changed'] = False
                        results['result'][host.name]['state_current'] = 'active'
                        results['result'][host.name]['msg'] = 'Hyperthreading is enabled and active'
                    if not hyperthreading_info.active:
                        option_manager = host.configManager.advancedOption
                        try:
                            mitigation = option_manager.QueryOptions('VMkernel.Boot.hyperthreadingMitigation')
                        except vim.fault.InvalidName:
                            mitigation = None
                        if mitigation and mitigation[0].value:
                            results['result'][host.name]['changed'] = False
                            results['result'][host.name]['state_current'] = 'enabled'
                            results['result'][host.name]['msg'] = 'Hyperthreading is enabled, but not active because the processor is vulnerable to L1 Terminal Fault (L1TF).'
                        else:
                            changed = results['result'][host.name]['changed'] = True
                            results['result'][host.name]['state_current'] = 'enabled'
                            results['result'][host.name]['msg'] = 'Hyperthreading is enabled, but not active. A reboot is required!'
                elif hyperthreading_info.available:
                    if not self.module.check_mode:
                        try:
                            host.configManager.cpuScheduler.EnableHyperThreading()
                            changed = results['result'][host.name]['changed'] = True
                            results['result'][host.name]['state_previous'] = 'disabled'
                            results['result'][host.name]['state_current'] = 'enabled'
                            results['result'][host.name]['msg'] = 'Hyperthreading enabled for host. Reboot the host to activate it.'
                        except vmodl.fault.NotSupported as not_supported:
                            self.module.fail_json(msg="Failed to enable Hyperthreading for host '%s' : %s" % (host.name, to_native(not_supported.msg)))
                        except (vmodl.RuntimeFault, vmodl.MethodFault) as runtime_fault:
                            self.module.fail_json(msg="Failed to enable Hyperthreading for host '%s' due to : %s" % (host.name, to_native(runtime_fault.msg)))
                    else:
                        changed = results['result'][host.name]['changed'] = True
                        results['result'][host.name]['state_previous'] = 'disabled'
                        results['result'][host.name]['state_current'] = 'enabled'
                        results['result'][host.name]['msg'] = 'Hyperthreading will be enabled'
                else:
                    self.module.fail_json(msg="Hyperthreading optimization is not available for host '%s'" % host.name)
            elif desired_state == 'disabled':
                if not hyperthreading_info.config:
                    if not hyperthreading_info.active:
                        results['result'][host.name]['changed'] = False
                        results['result'][host.name]['state_current'] = 'inactive'
                        results['result'][host.name]['msg'] = 'Hyperthreading is disabled and inactive'
                    if hyperthreading_info.active:
                        changed = results['result'][host.name]['changed'] = True
                        results['result'][host.name]['state_current'] = 'disabled'
                        results['result'][host.name]['msg'] = 'Hyperthreading is already disabled but still active. A reboot is required!'
                elif hyperthreading_info.available:
                    if not self.module.check_mode:
                        try:
                            host.configManager.cpuScheduler.DisableHyperThreading()
                            changed = results['result'][host.name]['changed'] = True
                            results['result'][host.name]['state_previous'] = 'enabled'
                            results['result'][host.name]['state_current'] = 'disabled'
                            results['result'][host.name]['msg'] = 'Hyperthreading disabled. Reboot the host to deactivate it.'
                        except vmodl.fault.NotSupported as not_supported:
                            self.module.fail_json(msg="Failed to disable Hyperthreading for host '%s' : %s" % (host.name, to_native(not_supported.msg)))
                        except (vmodl.RuntimeFault, vmodl.MethodFault) as runtime_fault:
                            self.module.fail_json(msg="Failed to disable Hyperthreading for host '%s' due to : %s" % (host.name, to_native(runtime_fault.msg)))
                    else:
                        changed = results['result'][host.name]['changed'] = True
                        results['result'][host.name]['state_previous'] = 'enabled'
                        results['result'][host.name]['state_current'] = 'disabled'
                        results['result'][host.name]['msg'] = 'Hyperthreading will be disabled'
                else:
                    self.module.fail_json(msg="Hyperthreading optimization is not available for host '%s'" % host.name)
            host_change_list.append(changed)
        if any(host_change_list):
            results['changed'] = True
        self.module.exit_json(**results)

def main():
    """Main"""
    argument_spec = vmware_argument_spec()
    argument_spec.update(state=dict(default='enabled', choices=['enabled', 'disabled']), esxi_hostname=dict(type='str', required=False), cluster_name=dict(type='str', required=False))
    module = AnsibleModule(argument_spec=argument_spec, required_one_of=[['cluster_name', 'esxi_hostname']], supports_check_mode=True)
    hyperthreading = VmwareHostHyperthreading(module)
    hyperthreading.ensure()
if __name__ == '__main__':
    main()

def test_VmwareHostHyperthreading_ensure():
    ret = VmwareHostHyperthreading().ensure()