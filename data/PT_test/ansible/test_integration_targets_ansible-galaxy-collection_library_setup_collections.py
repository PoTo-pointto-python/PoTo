from __future__ import absolute_import, division, print_function
__metaclass__ = type
ANSIBLE_METADATA = {'metadata_version': '1.1', 'status': ['preview'], 'supported_by': 'community'}
DOCUMENTATION = "\n---\nmodule: setup_collections\nshort_description: Set up test collections based on the input\ndescription:\n- Builds and publishes a whole bunch of collections used for testing in bulk.\noptions:\n  server:\n    description:\n    - The Galaxy server to upload the collections to.\n    required: yes\n    type: str\n  token:\n    description:\n    - The token used to authenticate with the Galaxy server.\n    required: yes\n    type: str\n  collections:\n    description:\n    - A list of collection details to use for the build.\n    required: yes\n    type: list\n    elements: dict\n    options:\n      namespace:\n        description:\n        - The namespace of the collection.\n        required: yes\n        type: str\n      name:\n        description:\n        - The name of the collection.\n        required: yes\n        type: str\n      version:\n        description:\n        - The version of the collection.\n        type: str\n        default: '1.0.0'\n      dependencies:\n        description:\n        - The dependencies of the collection.\n        type: dict\n        default: '{}'\nauthor:\n- Jordan Borean (@jborean93)\n"
EXAMPLES = '\n- name: Build test collections\n  setup_collections:\n    path: ~/ansible/collections/ansible_collections\n    collections:\n    - namespace: namespace1\n      name: name1\n      version: 0.0.1\n    - namespace: namespace1\n      name: name1\n      version: 0.0.2\n'
RETURN = '\n#\n'
import os
import tempfile
import yaml
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils._text import to_bytes

def run_module():
    module_args = dict(server=dict(type='str', required=True), token=dict(type='str'), collections=dict(type='list', elements='dict', required=True, options=dict(namespace=dict(type='str', required=True), name=dict(type='str', required=True), version=dict(type='str', default='1.0.0'), dependencies=dict(type='dict', default={}), use_symlink=dict(type='bool', default=False))))
    module = AnsibleModule(argument_spec=module_args, supports_check_mode=False)
    result = dict(changed=True, results=[])
    for (idx, collection) in enumerate(module.params['collections']):
        collection_dir = os.path.join(module.tmpdir, '%s-%s-%s' % (collection['namespace'], collection['name'], collection['version']))
        b_collection_dir = to_bytes(collection_dir, errors='surrogate_or_strict')
        os.mkdir(b_collection_dir)
        with open(os.path.join(b_collection_dir, b'README.md'), mode='wb') as fd:
            fd.write(b'Collection readme')
        galaxy_meta = {'namespace': collection['namespace'], 'name': collection['name'], 'version': collection['version'], 'readme': 'README.md', 'authors': ['Collection author <name@email.com'], 'dependencies': collection['dependencies'], 'license': ['GPL-3.0-or-later']}
        with open(os.path.join(b_collection_dir, b'galaxy.yml'), mode='wb') as fd:
            fd.write(to_bytes(yaml.safe_dump(galaxy_meta), errors='surrogate_or_strict'))
        with tempfile.NamedTemporaryFile(mode='wb') as temp_fd:
            temp_fd.write(b'data')
            if collection['use_symlink']:
                os.mkdir(os.path.join(b_collection_dir, b'docs'))
                os.mkdir(os.path.join(b_collection_dir, b'plugins'))
                b_target_file = b'RE\xc3\x85DM\xc3\x88.md'
                with open(os.path.join(b_collection_dir, b_target_file), mode='wb') as fd:
                    fd.write(b'data')
                os.symlink(b_target_file, os.path.join(b_collection_dir, b_target_file + b'-link'))
                os.symlink(temp_fd.name, os.path.join(b_collection_dir, b_target_file + b'-outside-link'))
                os.symlink(os.path.join(b'..', b_target_file), os.path.join(b_collection_dir, b'docs', b_target_file))
                os.symlink(os.path.join(b_collection_dir, b_target_file), os.path.join(b_collection_dir, b'plugins', b_target_file))
                os.symlink(b'docs', os.path.join(b_collection_dir, b'docs-link'))
            release_filename = '%s-%s-%s.tar.gz' % (collection['namespace'], collection['name'], collection['version'])
            collection_path = os.path.join(collection_dir, release_filename)
            (rc, stdout, stderr) = module.run_command(['ansible-galaxy', 'collection', 'build'], cwd=collection_dir)
            result['results'].append({'build': {'rc': rc, 'stdout': stdout, 'stderr': stderr}})
        publish_args = ['ansible-galaxy', 'collection', 'publish', collection_path, '--server', module.params['server']]
        if module.params['token']:
            publish_args.extend(['--token', module.params['token']])
        if idx != len(module.params['collections']) - 1:
            publish_args.append('--no-wait')
        (rc, stdout, stderr) = module.run_command(publish_args)
        result['results'][-1]['publish'] = {'rc': rc, 'stdout': stdout, 'stderr': stderr}
    failed = bool(sum((r['build']['rc'] + r['publish']['rc'] for r in result['results'])))
    module.exit_json(failed=failed, **result)

def main():
    run_module()
if __name__ == '__main__':
    main()