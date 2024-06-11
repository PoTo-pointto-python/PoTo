from __future__ import absolute_import, division, print_function
__metaclass__ = type
from ansible.errors import AnsibleError, AnsibleFilterError
try:
    import jmespath
    HAS_LIB = True
except ImportError:
    HAS_LIB = False

def json_query(data, expr):
    """Query data using jmespath query language ( http://jmespath.org ). Example:
    - debug: msg="{{ instance | json_query(tagged_instances[*].block_device_mapping.*.volume_id') }}"
    """
    if not HAS_LIB:
        raise AnsibleError('You need to install "jmespath" prior to running json_query filter')
    try:
        return jmespath.search(expr, data)
    except jmespath.exceptions.JMESPathError as e:
        raise AnsibleFilterError('JMESPathError in json_query filter plugin:\n%s' % e)
    except Exception as e:
        raise AnsibleFilterError('Error in jmespath.search in json_query filter plugin:\n%s' % e)

class FilterModule(object):
    """ Query filter """

    def filters(self):
        return {'json_query': json_query}

def test_FilterModule_filters():
    ret = FilterModule().filters()