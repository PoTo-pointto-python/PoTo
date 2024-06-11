"""
Test that the release name is present in the list of used up release names
"""
from __future__ import absolute_import, division, print_function
__metaclass__ = type
from yaml import safe_load
from ansible.release import __codename__

def main():
    """Entrypoint to the script"""
    with open('.github/RELEASE_NAMES.yml') as f:
        releases = safe_load(f.read())
    for name in (r.split(maxsplit=1)[1] for r in releases):
        if __codename__ == name:
            break
    else:
        print('.github/RELEASE_NAMES.yml: Current codename was not present in the file')
if __name__ == '__main__':
    main()