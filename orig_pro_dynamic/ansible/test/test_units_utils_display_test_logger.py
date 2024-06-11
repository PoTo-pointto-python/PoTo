from __future__ import absolute_import, division, print_function
__metaclass__ = type
import logging
import sys

def test_logger():
    """
    Avoid CVE-2019-14846 as 3rd party libs will disclose secrets when
    logging is set to DEBUG
    """
    for loaded in list(sys.modules.keys()):
        if 'ansible' in loaded:
            del sys.modules[loaded]
    from ansible import constants as C
    C.DEFAULT_LOG_PATH = '/dev/null'
    from ansible.utils.display import logger
    assert logger.root.level != logging.DEBUG