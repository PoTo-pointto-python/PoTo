from __future__ import absolute_import, division, print_function
__metaclass__ = type
import os
import json
import shutil
import tempfile
import pytest
from units.compat.mock import patch, MagicMock
from ansible.modules import async_wrapper
from pprint import pprint

class TestAsyncWrapper:

    def test_run_module(self, monkeypatch):

        def mock_get_interpreter(module_path):
            return ['/usr/bin/python']
        module_result = {'rc': 0}
        module_lines = ['#!/usr/bin/python', 'import sys', 'sys.stderr.write("stderr stuff")', "print('%s')" % json.dumps(module_result)]
        module_data = '\n'.join(module_lines) + '\n'
        module_data = module_data.encode('utf-8')
        workdir = tempfile.mkdtemp()
        (fh, fn) = tempfile.mkstemp(dir=workdir)
        with open(fn, 'wb') as f:
            f.write(module_data)
        command = fn
        jobid = 0
        jobpath = os.path.join(os.path.dirname(command), 'job')
        monkeypatch.setattr(async_wrapper, '_get_interpreter', mock_get_interpreter)
        res = async_wrapper._run_module(command, jobid, jobpath)
        with open(os.path.join(workdir, 'job'), 'r') as f:
            jres = json.loads(f.read())
        shutil.rmtree(workdir)
        assert jres.get('rc') == 0
        assert jres.get('stderr') == 'stderr stuff'

def test_TestAsyncWrapper_mock_get_interpreter():
    ret = TestAsyncWrapper().mock_get_interpreter()

def test_TestAsyncWrapper_test_run_module():
    ret = TestAsyncWrapper().test_run_module()