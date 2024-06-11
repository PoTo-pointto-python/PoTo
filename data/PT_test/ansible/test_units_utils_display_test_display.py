from __future__ import absolute_import, division, print_function
__metaclass__ = type
from ansible.utils.display import Display

def test_display_basic_message(capsys, mocker):
    mocker.patch('ansible.utils.display.logger', return_value=None)
    d = Display()
    d.display(u'Some displayed message')
    (out, err) = capsys.readouterr()
    assert out == 'Some displayed message\n'
    assert err == ''