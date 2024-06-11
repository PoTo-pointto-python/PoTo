from __future__ import absolute_import, division, print_function
__metaclass__ = type
ANSIBLE_METADATA = {'metadata_version': '1.1', 'status': ['preview'], 'supported_by': 'community'}
DOCUMENTATION = '\n---\nmodule: rabbitmq_queue\nauthor: Manuel Sousa (@manuel-sousa)\nversion_added: "2.0"\n\nshort_description: Manage rabbitMQ queues\ndescription:\n  - This module uses rabbitMQ Rest API to create/delete queues\nrequirements: [ "requests >= 1.0.0" ]\noptions:\n    name:\n        description:\n            - Name of the queue\n        required: true\n    state:\n        description:\n            - Whether the queue should be present or absent\n        choices: [ "present", "absent" ]\n        default: present\n    durable:\n        description:\n            - whether queue is durable or not\n        type: bool\n        default: \'yes\'\n    auto_delete:\n        description:\n            - if the queue should delete itself after all queues/queues unbound from it\n        type: bool\n        default: \'no\'\n    message_ttl:\n        description:\n            - How long a message can live in queue before it is discarded (milliseconds)\n        default: forever\n    auto_expires:\n        description:\n            - How long a queue can be unused before it is automatically deleted (milliseconds)\n        default: forever\n    max_length:\n        description:\n            - How many messages can the queue contain before it starts rejecting\n        default: no limit\n    dead_letter_exchange:\n        description:\n            - Optional name of an exchange to which messages will be republished if they\n            - are rejected or expire\n    dead_letter_routing_key:\n        description:\n            - Optional replacement routing key to use when a message is dead-lettered.\n            - Original routing key will be used if unset\n    max_priority:\n        description:\n            - Maximum number of priority levels for the queue to support.\n            - If not set, the queue will not support message priorities.\n            - Larger numbers indicate higher priority.\n        version_added: "2.4"\n    arguments:\n        description:\n            - extra arguments for queue. If defined this argument is a key/value dictionary\n        default: {}\nextends_documentation_fragment:\n    - rabbitmq\n'
EXAMPLES = '\n# Create a queue\n- rabbitmq_queue:\n    name: myQueue\n\n# Create a queue on remote host\n- rabbitmq_queue:\n    name: myRemoteQueue\n    login_user: user\n    login_password: secret\n    login_host: remote.example.org\n'
import json
import traceback
REQUESTS_IMP_ERR = None
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    REQUESTS_IMP_ERR = traceback.format_exc()
    HAS_REQUESTS = False
from ansible.module_utils.basic import AnsibleModule, missing_required_lib
from ansible.module_utils.six.moves.urllib import parse as urllib_parse
from ansible.module_utils.rabbitmq import rabbitmq_argument_spec

def main():
    argument_spec = rabbitmq_argument_spec()
    argument_spec.update(dict(state=dict(default='present', choices=['present', 'absent'], type='str'), name=dict(required=True, type='str'), durable=dict(default=True, type='bool'), auto_delete=dict(default=False, type='bool'), message_ttl=dict(default=None, type='int'), auto_expires=dict(default=None, type='int'), max_length=dict(default=None, type='int'), dead_letter_exchange=dict(default=None, type='str'), dead_letter_routing_key=dict(default=None, type='str'), arguments=dict(default=dict(), type='dict'), max_priority=dict(default=None, type='int')))
    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    url = '%s://%s:%s/api/queues/%s/%s' % (module.params['login_protocol'], module.params['login_host'], module.params['login_port'], urllib_parse.quote(module.params['vhost'], ''), module.params['name'])
    if not HAS_REQUESTS:
        module.fail_json(msg=missing_required_lib('requests'), exception=REQUESTS_IMP_ERR)
    result = dict(changed=False, name=module.params['name'])
    r = requests.get(url, auth=(module.params['login_user'], module.params['login_password']), verify=module.params['ca_cert'], cert=(module.params['client_cert'], module.params['client_key']))
    if r.status_code == 200:
        queue_exists = True
        response = r.json()
    elif r.status_code == 404:
        queue_exists = False
        response = r.text
    else:
        module.fail_json(msg='Invalid response from RESTAPI when trying to check if queue exists', details=r.text)
    if module.params['state'] == 'present':
        change_required = not queue_exists
    else:
        change_required = queue_exists
    if not change_required and r.status_code == 200 and (module.params['state'] == 'present'):
        if not (response['durable'] == module.params['durable'] and response['auto_delete'] == module.params['auto_delete'] and ('x-message-ttl' in response['arguments'] and response['arguments']['x-message-ttl'] == module.params['message_ttl'] or ('x-message-ttl' not in response['arguments'] and module.params['message_ttl'] is None)) and ('x-expires' in response['arguments'] and response['arguments']['x-expires'] == module.params['auto_expires'] or ('x-expires' not in response['arguments'] and module.params['auto_expires'] is None)) and ('x-max-length' in response['arguments'] and response['arguments']['x-max-length'] == module.params['max_length'] or ('x-max-length' not in response['arguments'] and module.params['max_length'] is None)) and ('x-dead-letter-exchange' in response['arguments'] and response['arguments']['x-dead-letter-exchange'] == module.params['dead_letter_exchange'] or ('x-dead-letter-exchange' not in response['arguments'] and module.params['dead_letter_exchange'] is None)) and ('x-dead-letter-routing-key' in response['arguments'] and response['arguments']['x-dead-letter-routing-key'] == module.params['dead_letter_routing_key'] or ('x-dead-letter-routing-key' not in response['arguments'] and module.params['dead_letter_routing_key'] is None)) and ('x-max-priority' in response['arguments'] and response['arguments']['x-max-priority'] == module.params['max_priority'] or ('x-max-priority' not in response['arguments'] and module.params['max_priority'] is None))):
            module.fail_json(msg="RabbitMQ RESTAPI doesn't support attribute changes for existing queues")
    for (k, v) in {'message_ttl': 'x-message-ttl', 'auto_expires': 'x-expires', 'max_length': 'x-max-length', 'dead_letter_exchange': 'x-dead-letter-exchange', 'dead_letter_routing_key': 'x-dead-letter-routing-key', 'max_priority': 'x-max-priority'}.items():
        if module.params[k] is not None:
            module.params['arguments'][v] = module.params[k]
    if module.check_mode:
        result['changed'] = change_required
        result['details'] = response
        result['arguments'] = module.params['arguments']
        module.exit_json(**result)
    if change_required:
        if module.params['state'] == 'present':
            r = requests.put(url, auth=(module.params['login_user'], module.params['login_password']), headers={'content-type': 'application/json'}, data=json.dumps({'durable': module.params['durable'], 'auto_delete': module.params['auto_delete'], 'arguments': module.params['arguments']}), verify=module.params['ca_cert'], cert=(module.params['client_cert'], module.params['client_key']))
        elif module.params['state'] == 'absent':
            r = requests.delete(url, auth=(module.params['login_user'], module.params['login_password']), verify=module.params['ca_cert'], cert=(module.params['client_cert'], module.params['client_key']))
        if r.status_code == 204 or r.status_code == 201:
            result['changed'] = True
            module.exit_json(**result)
        else:
            module.fail_json(msg='Error creating queue', status=r.status_code, details=r.text)
    else:
        module.exit_json(changed=False, name=module.params['name'])
if __name__ == '__main__':
    main()