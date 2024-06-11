from __future__ import absolute_import, division, print_function
__metaclass__ = type
from ansible.plugins.action import ActionBase
from ansible.plugins.action.template import ActionModule as TemplateActionModule

class ActionModule(TemplateActionModule, ActionBase):
    DEFAULT_NEWLINE_SEQUENCE = '\r\n'