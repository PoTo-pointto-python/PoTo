from __future__ import absolute_import, division, print_function
__metaclass__ = type
DOCUMENTATION = '\n    cache: notjsonfile\n    short_description: JSON formatted files.\n    description:\n        - This cache uses JSON formatted, per host, files saved to the filesystem.\n    author: Ansible Core (@ansible-core)\n    options:\n      _uri:\n        required: True\n        description:\n          - Path in which the cache plugin will save the JSON files\n        env:\n          - name: ANSIBLE_CACHE_PLUGIN_CONNECTION\n        ini:\n          - key: fact_caching_connection\n            section: defaults\n      _prefix:\n        description: User defined prefix to use when creating the JSON files\n        env:\n          - name: ANSIBLE_CACHE_PLUGIN_PREFIX\n        ini:\n          - key: fact_caching_prefix\n            section: defaults\n      _timeout:\n        default: 86400\n        description: Expiration timeout for the cache plugin data\n        env:\n          - name: ANSIBLE_CACHE_PLUGIN_TIMEOUT\n        ini:\n          - key: fact_caching_timeout\n            section: defaults\n        type: integer\n'
from ansible.plugins.cache import BaseFileCacheModule

class CacheModule(BaseFileCacheModule):
    """
    A caching module backed by json files.
    """
    pass