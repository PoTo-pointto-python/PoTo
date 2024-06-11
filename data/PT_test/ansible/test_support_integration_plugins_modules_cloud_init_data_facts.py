from __future__ import absolute_import, division, print_function
__metaclass__ = type
ANSIBLE_METADATA = {'metadata_version': '1.1', 'status': ['preview'], 'supported_by': 'community'}
DOCUMENTATION = '\n---\nmodule: cloud_init_data_facts\nshort_description: Retrieve facts of cloud-init.\ndescription:\n  - Gathers facts by reading the status.json and result.json of cloud-init.\nversion_added: 2.6\nauthor: René Moser (@resmo)\noptions:\n  filter:\n    description:\n      - Filter facts\n    choices: [ status, result ]\nnotes:\n  - See http://cloudinit.readthedocs.io/ for more information about cloud-init.\n'
EXAMPLES = '\n- name: Gather all facts of cloud init\n  cloud_init_data_facts:\n  register: result\n\n- debug:\n    var: result\n\n- name: Wait for cloud init to finish\n  cloud_init_data_facts:\n    filter: status\n  register: res\n  until: "res.cloud_init_data_facts.status.v1.stage is defined and not res.cloud_init_data_facts.status.v1.stage"\n  retries: 50\n  delay: 5\n'
RETURN = '\n---\ncloud_init_data_facts:\n  description: Facts of result and status.\n  returned: success\n  type: dict\n  sample: \'{\n    "status": {\n        "v1": {\n            "datasource": "DataSourceCloudStack",\n            "errors": []\n        },\n    "result": {\n        "v1": {\n            "datasource": "DataSourceCloudStack",\n            "init": {\n                "errors": [],\n                "finished": 1522066377.0185432,\n                "start": 1522066375.2648022\n            },\n            "init-local": {\n                "errors": [],\n                "finished": 1522066373.70919,\n                "start": 1522066373.4726632\n            },\n            "modules-config": {\n                "errors": [],\n                "finished": 1522066380.9097016,\n                "start": 1522066379.0011985\n            },\n            "modules-final": {\n                "errors": [],\n                "finished": 1522066383.56594,\n                "start": 1522066382.3449218\n            },\n            "stage": null\n        }\n    }\'\n'
import os
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils._text import to_text
CLOUD_INIT_PATH = '/var/lib/cloud/data/'

def gather_cloud_init_data_facts(module):
    res = {'cloud_init_data_facts': dict()}
    for i in ['result', 'status']:
        filter = module.params.get('filter')
        if filter is None or filter == i:
            res['cloud_init_data_facts'][i] = dict()
            json_file = CLOUD_INIT_PATH + i + '.json'
            if os.path.exists(json_file):
                f = open(json_file, 'rb')
                contents = to_text(f.read(), errors='surrogate_or_strict')
                f.close()
                if contents:
                    res['cloud_init_data_facts'][i] = module.from_json(contents)
    return res

def main():
    module = AnsibleModule(argument_spec=dict(filter=dict(choices=['result', 'status'])), supports_check_mode=True)
    facts = gather_cloud_init_data_facts(module)
    result = dict(changed=False, ansible_facts=facts, **facts)
    module.exit_json(**result)
if __name__ == '__main__':
    main()