from __future__ import absolute_import, division, print_function
__metaclass__ = type
from ansible import context

class FakeOptions:
    pass

def test_set_global_context():
    options = FakeOptions()
    options.tags = [u'production', u'webservers']
    options.check_mode = True
    options.start_at_task = u'Start with くらとみ'
    expected = frozenset((('tags', (u'production', u'webservers')), ('check_mode', True), ('start_at_task', u'Start with くらとみ')))
    context._init_global_context(options)
    assert frozenset(context.CLIARGS.items()) == expected