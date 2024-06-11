from __future__ import absolute_import, division, print_function
__metaclass__ = type
from io import StringIO
import pytest
from units.compat import unittest
from ansible.plugins.connection import local
from ansible.playbook.play_context import PlayContext

class TestLocalConnectionClass(unittest.TestCase):

    def test_local_connection_module(self):
        play_context = PlayContext()
        play_context.prompt = '[sudo via ansible, key=ouzmdnewuhucvuaabtjmweasarviygqq] password: '
        in_stream = StringIO()
        self.assertIsInstance(local.Connection(play_context, in_stream), local.Connection)

def test_TestLocalConnectionClass_test_local_connection_module():
    ret = TestLocalConnectionClass().test_local_connection_module()