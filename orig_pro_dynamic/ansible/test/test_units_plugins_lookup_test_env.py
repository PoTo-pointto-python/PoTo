from __future__ import absolute_import, division, print_function
__metaclass__ = type
import pytest
from ansible.plugins.loader import lookup_loader

@pytest.mark.parametrize('env_var,exp_value', [('foo', 'bar'), ('equation', 'a=b*100')])
def test_env_var_value(monkeypatch, env_var, exp_value):
    (env_var, exp_value) = ('foo', 'bar')
    monkeypatch.setattr('ansible.utils.py3compat.environ.get', lambda x, y: exp_value)
    env_lookup = lookup_loader.get('env')
    retval = env_lookup.run([env_var], None)
    assert retval == [exp_value]

@pytest.mark.parametrize('env_var,exp_value', [('simple_var', 'alpha-β-gamma'), ('the_var', 'ãnˈsiβle')])
def test_utf8_env_var_value(monkeypatch, env_var, exp_value):
    (env_var, exp_value) = ('simple_var', 'alpha-β-gamma')
    monkeypatch.setattr('ansible.utils.py3compat.environ.get', lambda x, y: exp_value)
    env_lookup = lookup_loader.get('env')
    retval = env_lookup.run([env_var], None)
    assert retval == [exp_value]