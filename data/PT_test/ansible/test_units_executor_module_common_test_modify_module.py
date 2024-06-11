from __future__ import absolute_import, division, print_function
__metaclass__ = type
import pytest
from ansible.executor.module_common import modify_module
from ansible.module_utils.six import PY2
from test_module_common import templar
FAKE_OLD_MODULE = b'#!/usr/bin/python\nimport sys\nprint(\'{"result": "%s"}\' % sys.executable)\n'

@pytest.fixture
def fake_old_module_open(mocker):
    m = mocker.mock_open(read_data=FAKE_OLD_MODULE)
    if PY2:
        mocker.patch('__builtin__.open', m)
    else:
        mocker.patch('builtins.open', m)

def test_shebang_task_vars(fake_old_module_open, templar):
    fake_old_module_open = fake_old_module_open()
    task_vars = {'ansible_python_interpreter': '/usr/bin/python3'}
    (data, style, shebang) = modify_module('fake_module', 'fake_path', {}, templar, task_vars=task_vars)
    assert shebang == '#!/usr/bin/python3'