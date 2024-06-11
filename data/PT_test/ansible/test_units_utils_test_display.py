from __future__ import absolute_import, division, print_function
__metaclass__ = type
from units.compat.mock import MagicMock
import pytest
from ansible.module_utils.six import PY3
from ansible.utils.display import Display, get_text_width, initialize_locale

def test_get_text_width():
    initialize_locale()
    assert get_text_width(u'コンニチハ') == 10
    assert get_text_width(u'abコcd') == 6
    assert get_text_width(u'café') == 4
    assert get_text_width(u'four') == 4
    assert get_text_width(u'\x1b') == 0
    assert get_text_width(u'ab\x00') == 2
    assert get_text_width(u'abコ\x00') == 4
    assert get_text_width(u'🚀🐮') == 4
    assert get_text_width(u'\x08') == 0
    assert get_text_width(u'\x08\x08') == 0
    assert get_text_width(u'ab\x08cd') == 3
    assert get_text_width(u'ab\x1bcd') == 3
    assert get_text_width(u'ab\x7fcd') == 3
    assert get_text_width(u'ab\x94cd') == 3
    pytest.raises(TypeError, get_text_width, 1)
    pytest.raises(TypeError, get_text_width, b'four')

@pytest.mark.skipif(PY3, reason='Fallback only happens reliably on py2')
def test_get_text_width_no_locale():
    pytest.raises(EnvironmentError, get_text_width, u'🚀🐮')

def test_Display_banner_get_text_width(monkeypatch):
    initialize_locale()
    display = Display()
    display_mock = MagicMock()
    monkeypatch.setattr(display, 'display', display_mock)
    display.banner(u'🚀🐮', color=False, cows=False)
    (args, kwargs) = display_mock.call_args
    msg = args[0]
    stars = u' %s' % (75 * u'*')
    assert msg.endswith(stars)

@pytest.mark.skipif(PY3, reason='Fallback only happens reliably on py2')
def test_Display_banner_get_text_width_fallback(monkeypatch):
    display = Display()
    display_mock = MagicMock()
    monkeypatch.setattr(display, 'display', display_mock)
    display.banner(u'🚀🐮', color=False, cows=False)
    (args, kwargs) = display_mock.call_args
    msg = args[0]
    stars = u' %s' % (77 * u'*')
    assert msg.endswith(stars)