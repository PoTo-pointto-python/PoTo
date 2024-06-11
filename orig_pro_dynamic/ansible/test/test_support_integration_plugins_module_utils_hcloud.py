from __future__ import absolute_import, division, print_function
__metaclass__ = type
from ansible.module_utils.ansible_release import __version__
from ansible.module_utils.basic import env_fallback, missing_required_lib
try:
    import hcloud
    HAS_HCLOUD = True
except ImportError:
    HAS_HCLOUD = False

class Hcloud(object):

    def __init__(self, module, represent):
        self.module = module
        self.represent = represent
        self.result = {'changed': False, self.represent: None}
        if not HAS_HCLOUD:
            module.fail_json(msg=missing_required_lib('hcloud-python'))
        self._build_client()

    def _build_client(self):
        self.client = hcloud.Client(token=self.module.params['api_token'], api_endpoint=self.module.params['endpoint'], application_name='ansible-module', application_version=__version__)

    def _mark_as_changed(self):
        self.result['changed'] = True

    @staticmethod
    def base_module_arguments():
        return {'api_token': {'type': 'str', 'required': True, 'fallback': (env_fallback, ['HCLOUD_TOKEN']), 'no_log': True}, 'endpoint': {'type': 'str', 'default': 'https://api.hetzner.cloud/v1'}}

    def _prepare_result(self):
        """Prepare the result for every module

        :return: dict
        """
        return {}

    def get_result(self):
        if getattr(self, self.represent) is not None:
            self.result[self.represent] = self._prepare_result()
        return self.result

def test_Hcloud__build_client():
    ret = Hcloud()._build_client()

def test_Hcloud__mark_as_changed():
    ret = Hcloud()._mark_as_changed()

def test_Hcloud_base_module_arguments():
    ret = Hcloud().base_module_arguments()

def test_Hcloud__prepare_result():
    ret = Hcloud()._prepare_result()

def test_Hcloud_get_result():
    ret = Hcloud().get_result()