from __future__ import absolute_import, division, print_function
__metaclass__ = type
import pytest
from ansible import constants as C
from ansible.errors import AnsibleUndefinedVariable
C.DEFAULT_JINJA2_NATIVE = True
from ansible.template import Templar
from units.mock.loader import DictDataLoader

def test_undefined_variable():
    fake_loader = DictDataLoader({})
    variables = {}
    templar = Templar(loader=fake_loader, variables=variables)
    with pytest.raises(AnsibleUndefinedVariable):
        templar.template('{{ missing }}')