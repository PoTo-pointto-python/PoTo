from __future__ import absolute_import, division, print_function
__metaclass__ = type
ANSIBLE_METADATA = {'metadata_version': '1.1', 'status': ['preview'], 'supported_by': 'community'}
DOCUMENTATION = '\nmodule: k8s_info\n\nshort_description: Describe Kubernetes (K8s) objects\n\nversion_added: "2.7"\n\nauthor:\n    - "Will Thames (@willthames)"\n\ndescription:\n  - Use the OpenShift Python client to perform read operations on K8s objects.\n  - Access to the full range of K8s APIs.\n  - Authenticate using either a config file, certificates, password or token.\n  - Supports check mode.\n  - This module was called C(k8s_facts) before Ansible 2.9. The usage did not change.\n\noptions:\n  api_version:\n    description:\n    - Use to specify the API version. in conjunction with I(kind), I(name), and I(namespace) to identify a\n      specific object.\n    default: v1\n    aliases:\n    - api\n    - version\n  kind:\n    description:\n    - Use to specify an object model. Use in conjunction with I(api_version), I(name), and I(namespace) to identify a\n      specific object.\n    required: yes\n  name:\n    description:\n    - Use to specify an object name.  Use in conjunction with I(api_version), I(kind) and I(namespace) to identify a\n      specific object.\n  namespace:\n    description:\n    - Use to specify an object namespace. Use in conjunction with I(api_version), I(kind), and I(name)\n      to identify a specific object.\n  label_selectors:\n    description: List of label selectors to use to filter results\n  field_selectors:\n    description: List of field selectors to use to filter results\n\nextends_documentation_fragment:\n  - k8s_auth_options\n\nrequirements:\n  - "python >= 2.7"\n  - "openshift >= 0.6"\n  - "PyYAML >= 3.11"\n'
EXAMPLES = '\n- name: Get an existing Service object\n  k8s_info:\n    api_version: v1\n    kind: Service\n    name: web\n    namespace: testing\n  register: web_service\n\n- name: Get a list of all service objects\n  k8s_info:\n    api_version: v1\n    kind: Service\n    namespace: testing\n  register: service_list\n\n- name: Get a list of all pods from any namespace\n  k8s_info:\n    kind: Pod\n  register: pod_list\n\n- name: Search for all Pods labelled app=web\n  k8s_info:\n    kind: Pod\n    label_selectors:\n      - app = web\n      - tier in (dev, test)\n\n- name: Search for all running pods\n  k8s_info:\n    kind: Pod\n    field_selectors:\n      - status.phase=Running\n'
RETURN = '\nresources:\n  description:\n  - The object(s) that exists\n  returned: success\n  type: complex\n  contains:\n    api_version:\n      description: The versioned schema of this representation of an object.\n      returned: success\n      type: str\n    kind:\n      description: Represents the REST resource this object represents.\n      returned: success\n      type: str\n    metadata:\n      description: Standard object metadata. Includes name, namespace, annotations, labels, etc.\n      returned: success\n      type: dict\n    spec:\n      description: Specific attributes of the object. Will vary based on the I(api_version) and I(kind).\n      returned: success\n      type: dict\n    status:\n      description: Current status details for the object.\n      returned: success\n      type: dict\n'
from ansible.module_utils.k8s.common import KubernetesAnsibleModule, AUTH_ARG_SPEC
import copy

class KubernetesInfoModule(KubernetesAnsibleModule):

    def __init__(self, *args, **kwargs):
        KubernetesAnsibleModule.__init__(self, *args, supports_check_mode=True, **kwargs)
        if self._name == 'k8s_facts':
            self.deprecate("The 'k8s_facts' module has been renamed to 'k8s_info'", version='2.13', collection_name='ansible.builtin')

    def execute_module(self):
        self.client = self.get_api_client()
        self.exit_json(changed=False, **self.kubernetes_facts(self.params['kind'], self.params['api_version'], self.params['name'], self.params['namespace'], self.params['label_selectors'], self.params['field_selectors']))

    @property
    def argspec(self):
        args = copy.deepcopy(AUTH_ARG_SPEC)
        args.update(dict(kind=dict(required=True), api_version=dict(default='v1', aliases=['api', 'version']), name=dict(), namespace=dict(), label_selectors=dict(type='list', default=[]), field_selectors=dict(type='list', default=[])))
        return args

def main():
    KubernetesInfoModule().execute_module()
if __name__ == '__main__':
    main()

def test_KubernetesInfoModule_execute_module():
    ret = KubernetesInfoModule().execute_module()

def test_KubernetesInfoModule_argspec():
    ret = KubernetesInfoModule().argspec()