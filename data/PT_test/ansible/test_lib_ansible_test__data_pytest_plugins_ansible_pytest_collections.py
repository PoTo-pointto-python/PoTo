"""Enable unit testing of Ansible collections. PYTEST_DONT_REWRITE"""
from __future__ import absolute_import, division, print_function
__metaclass__ = type
import os
import sys
ANSIBLE_COLLECTIONS_PATH = os.path.join(os.environ['ANSIBLE_COLLECTIONS_PATH'], 'ansible_collections')

def collection_pypkgpath(self):
    """Configure the Python package path so that pytest can find our collections."""
    for parent in self.parts(reverse=True):
        if str(parent) == ANSIBLE_COLLECTIONS_PATH:
            return parent
    raise Exception('File "%s" not found in collection path "%s".' % (self.strpath, ANSIBLE_COLLECTIONS_PATH))

def pytest_configure():
    """Configure this pytest plugin."""
    try:
        if pytest_configure.executed:
            return
    except AttributeError:
        pytest_configure.executed = True
    from ansible.utils.collection_loader._collection_finder import _AnsibleCollectionFinder
    _AnsibleCollectionFinder(paths=[os.path.dirname(ANSIBLE_COLLECTIONS_PATH)])._install()
    import py._path.local
    py._path.local.LocalPath.pypkgpath = collection_pypkgpath
pytest_configure()