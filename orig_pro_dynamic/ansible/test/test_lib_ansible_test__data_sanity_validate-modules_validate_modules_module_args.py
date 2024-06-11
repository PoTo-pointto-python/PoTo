from __future__ import absolute_import, division, print_function
__metaclass__ = type
import runpy
import json
import os
import subprocess
import sys
from contextlib import contextmanager
from ansible.executor.powershell.module_manifest import PSModuleDepFinder
from ansible.module_utils.basic import FILE_COMMON_ARGUMENTS
from ansible.module_utils.six import reraise
from ansible.module_utils._text import to_bytes, to_text
from .utils import CaptureStd, find_executable, get_module_name_from_filename

class AnsibleModuleCallError(RuntimeError):
    pass

class AnsibleModuleImportError(ImportError):
    pass

class AnsibleModuleNotInitialized(Exception):
    pass

class _FakeAnsibleModuleInit:

    def __init__(self):
        self.args = tuple()
        self.kwargs = {}
        self.called = False

    def __call__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.called = True
        raise AnsibleModuleCallError('AnsibleModuleCallError')

def _fake_load_params():
    pass

@contextmanager
def setup_env(filename):
    pre_sys_modules = list(sys.modules.keys())
    fake = _FakeAnsibleModuleInit()
    module = __import__('ansible.module_utils.basic').module_utils.basic
    _original_init = module.AnsibleModule.__init__
    _original_load_params = module._load_params
    setattr(module.AnsibleModule, '__init__', fake)
    setattr(module, '_load_params', _fake_load_params)
    try:
        yield fake
    finally:
        setattr(module.AnsibleModule, '__init__', _original_init)
        setattr(module, '_load_params', _original_load_params)
        for k in list(sys.modules.keys()):
            if k not in pre_sys_modules and k.startswith('ansible.module_utils.'):
                del sys.modules[k]

def get_ps_argument_spec(filename, collection):
    fqc_name = get_module_name_from_filename(filename, collection)
    pwsh = find_executable('pwsh')
    if not pwsh:
        raise FileNotFoundError('Required program for PowerShell arg spec inspection "pwsh" not found.')
    module_path = os.path.join(os.getcwd(), filename)
    b_module_path = to_bytes(module_path, errors='surrogate_or_strict')
    with open(b_module_path, mode='rb') as module_fd:
        b_module_data = module_fd.read()
    ps_dep_finder = PSModuleDepFinder()
    ps_dep_finder.scan_module(b_module_data, fqn=fqc_name)
    ps_dep_finder._add_module((b'Ansible.ModuleUtils.AddType', '.psm1', None), wrapper=False)
    util_manifest = json.dumps({'module_path': to_text(module_path, errors='surrogiate_or_strict'), 'ansible_basic': ps_dep_finder.cs_utils_module['Ansible.Basic']['path'], 'ps_utils': dict([(name, info['path']) for (name, info) in ps_dep_finder.ps_modules.items()])})
    script_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'ps_argspec.ps1')
    proc = subprocess.Popen([script_path, util_manifest], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False)
    (stdout, stderr) = proc.communicate()
    if proc.returncode != 0:
        raise AnsibleModuleImportError('STDOUT:\n%s\nSTDERR:\n%s' % (stdout.decode('utf-8'), stderr.decode('utf-8')))
    kwargs = json.loads(stdout)
    kwargs['argument_spec'] = kwargs.pop('options', {})
    return (kwargs['argument_spec'], (), kwargs)

def get_py_argument_spec(filename, collection):
    name = get_module_name_from_filename(filename, collection)
    with setup_env(filename) as fake:
        try:
            with CaptureStd():
                runpy.run_module(name, run_name='__main__', alter_sys=True)
        except AnsibleModuleCallError:
            pass
        except BaseException as e:
            reraise(AnsibleModuleImportError, AnsibleModuleImportError('%s' % e), sys.exc_info()[2])
        if not fake.called:
            raise AnsibleModuleNotInitialized()
    try:
        try:
            argument_spec = fake.kwargs['argument_spec']
            if fake.kwargs.get('add_file_common_args'):
                for (k, v) in FILE_COMMON_ARGUMENTS.items():
                    if k not in argument_spec:
                        argument_spec[k] = v
            return (argument_spec, fake.args, fake.kwargs)
        except KeyError:
            return (fake.args[0], fake.args, fake.kwargs)
    except (TypeError, IndexError):
        return ({}, (), {})

def get_argument_spec(filename, collection):
    if filename.endswith('.py'):
        return get_py_argument_spec(filename, collection)
    else:
        return get_ps_argument_spec(filename, collection)

def test__FakeAnsibleModuleInit___call__():
    ret = _FakeAnsibleModuleInit().__call__()