from __future__ import absolute_import, division, print_function
__metaclass__ = type
ANSIBLE_METADATA = {'metadata_version': '1.1', 'status': ['preview'], 'supported_by': 'community'}
DOCUMENTATION = '\n---\nmodule: deploy_helper\nversion_added: "2.0"\nauthor: "Ramon de la Fuente (@ramondelafuente)"\nshort_description: Manages some of the steps common in deploying projects.\ndescription:\n  - The Deploy Helper manages some of the steps common in deploying software.\n    It creates a folder structure, manages a symlink for the current release\n    and cleans up old releases.\n  - "Running it with the C(state=query) or C(state=present) will return the C(deploy_helper) fact.\n    C(project_path), whatever you set in the path parameter,\n    C(current_path), the path to the symlink that points to the active release,\n    C(releases_path), the path to the folder to keep releases in,\n    C(shared_path), the path to the folder to keep shared resources in,\n    C(unfinished_filename), the file to check for to recognize unfinished builds,\n    C(previous_release), the release the \'current\' symlink is pointing to,\n    C(previous_release_path), the full path to the \'current\' symlink target,\n    C(new_release), either the \'release\' parameter or a generated timestamp,\n    C(new_release_path), the path to the new release folder (not created by the module)."\n\noptions:\n  path:\n    required: True\n    aliases: [\'dest\']\n    description:\n      - the root path of the project. Alias I(dest).\n        Returned in the C(deploy_helper.project_path) fact.\n\n  state:\n    description:\n      - the state of the project.\n        C(query) will only gather facts,\n        C(present) will create the project I(root) folder, and in it the I(releases) and I(shared) folders,\n        C(finalize) will remove the unfinished_filename file, create a symlink to the newly\n          deployed release and optionally clean old releases,\n        C(clean) will remove failed & old releases,\n        C(absent) will remove the project folder (synonymous to the M(file) module with C(state=absent))\n    choices: [ present, finalize, absent, clean, query ]\n    default: present\n\n  release:\n    description:\n      - the release version that is being deployed. Defaults to a timestamp format %Y%m%d%H%M%S (i.e. \'20141119223359\').\n        This parameter is optional during C(state=present), but needs to be set explicitly for C(state=finalize).\n        You can use the generated fact C(release={{ deploy_helper.new_release }}).\n\n  releases_path:\n    description:\n      - the name of the folder that will hold the releases. This can be relative to C(path) or absolute.\n        Returned in the C(deploy_helper.releases_path) fact.\n    default: releases\n\n  shared_path:\n    description:\n      - the name of the folder that will hold the shared resources. This can be relative to C(path) or absolute.\n        If this is set to an empty string, no shared folder will be created.\n        Returned in the C(deploy_helper.shared_path) fact.\n    default: shared\n\n  current_path:\n    description:\n      - the name of the symlink that is created when the deploy is finalized. Used in C(finalize) and C(clean).\n        Returned in the C(deploy_helper.current_path) fact.\n    default: current\n\n  unfinished_filename:\n    description:\n      - the name of the file that indicates a deploy has not finished. All folders in the releases_path that\n        contain this file will be deleted on C(state=finalize) with clean=True, or C(state=clean). This file is\n        automatically deleted from the I(new_release_path) during C(state=finalize).\n    default: DEPLOY_UNFINISHED\n\n  clean:\n    description:\n      - Whether to run the clean procedure in case of C(state=finalize).\n    type: bool\n    default: \'yes\'\n\n  keep_releases:\n    description:\n      - the number of old releases to keep when cleaning. Used in C(finalize) and C(clean). Any unfinished builds\n        will be deleted first, so only correct releases will count. The current version will not count.\n    default: 5\n\nnotes:\n  - Facts are only returned for C(state=query) and C(state=present). If you use both, you should pass any overridden\n    parameters to both calls, otherwise the second call will overwrite the facts of the first one.\n  - When using C(state=clean), the releases are ordered by I(creation date). You should be able to switch to a\n    new naming strategy without problems.\n  - Because of the default behaviour of generating the I(new_release) fact, this module will not be idempotent\n    unless you pass your own release name with C(release). Due to the nature of deploying software, this should not\n    be much of a problem.\n'
EXAMPLES = "\n\n# General explanation, starting with an example folder structure for a project:\n\n# root:\n#     releases:\n#         - 20140415234508\n#         - 20140415235146\n#         - 20140416082818\n#\n#     shared:\n#         - sessions\n#         - uploads\n#\n#     current: releases/20140416082818\n\n\n# The 'releases' folder holds all the available releases. A release is a complete build of the application being\n# deployed. This can be a clone of a repository for example, or a sync of a local folder on your filesystem.\n# Having timestamped folders is one way of having distinct releases, but you could choose your own strategy like\n# git tags or commit hashes.\n#\n# During a deploy, a new folder should be created in the releases folder and any build steps required should be\n# performed. Once the new build is ready, the deploy procedure is 'finalized' by replacing the 'current' symlink\n# with a link to this build.\n#\n# The 'shared' folder holds any resource that is shared between releases. Examples of this are web-server\n# session files, or files uploaded by users of your application. It's quite common to have symlinks from a release\n# folder pointing to a shared/subfolder, and creating these links would be automated as part of the build steps.\n#\n# The 'current' symlink points to one of the releases. Probably the latest one, unless a deploy is in progress.\n# The web-server's root for the project will go through this symlink, so the 'downtime' when switching to a new\n# release is reduced to the time it takes to switch the link.\n#\n# To distinguish between successful builds and unfinished ones, a file can be placed in the folder of the release\n# that is currently in progress. The existence of this file will mark it as unfinished, and allow an automated\n# procedure to remove it during cleanup.\n\n\n# Typical usage\n- name: Initialize the deploy root and gather facts\n  deploy_helper:\n    path: /path/to/root\n- name: Clone the project to the new release folder\n  git:\n    repo: git://foosball.example.org/path/to/repo.git\n    dest: '{{ deploy_helper.new_release_path }}'\n    version: v1.1.1\n- name: Add an unfinished file, to allow cleanup on successful finalize\n  file:\n    path: '{{ deploy_helper.new_release_path }}/{{ deploy_helper.unfinished_filename }}'\n    state: touch\n- name: Perform some build steps, like running your dependency manager for example\n  composer:\n    command: install\n    working_dir: '{{ deploy_helper.new_release_path }}'\n- name: Create some folders in the shared folder\n  file:\n    path: '{{ deploy_helper.shared_path }}/{{ item }}'\n    state: directory\n  with_items:\n    - sessions\n    - uploads\n- name: Add symlinks from the new release to the shared folder\n  file:\n    path: '{{ deploy_helper.new_release_path }}/{{ item.path }}'\n    src: '{{ deploy_helper.shared_path }}/{{ item.src }}'\n    state: link\n  with_items:\n      - path: app/sessions\n        src: sessions\n      - path: web/uploads\n        src: uploads\n- name: Finalize the deploy, removing the unfinished file and switching the symlink\n  deploy_helper:\n    path: /path/to/root\n    release: '{{ deploy_helper.new_release }}'\n    state: finalize\n\n# Retrieving facts before running a deploy\n- name: Run 'state=query' to gather facts without changing anything\n  deploy_helper:\n    path: /path/to/root\n    state: query\n# Remember to set the 'release' parameter when you actually call 'state=present' later\n- name: Initialize the deploy root\n  deploy_helper:\n    path: /path/to/root\n    release: '{{ deploy_helper.new_release }}'\n    state: present\n\n# all paths can be absolute or relative (to the 'path' parameter)\n- deploy_helper:\n    path: /path/to/root\n    releases_path: /var/www/project/releases\n    shared_path: /var/www/shared\n    current_path: /var/www/active\n\n# Using your own naming strategy for releases (a version tag in this case):\n- deploy_helper:\n    path: /path/to/root\n    release: v1.1.1\n    state: present\n- deploy_helper:\n    path: /path/to/root\n    release: '{{ deploy_helper.new_release }}'\n    state: finalize\n\n# Using a different unfinished_filename:\n- deploy_helper:\n    path: /path/to/root\n    unfinished_filename: README.md\n    release: '{{ deploy_helper.new_release }}'\n    state: finalize\n\n# Postponing the cleanup of older builds:\n- deploy_helper:\n    path: /path/to/root\n    release: '{{ deploy_helper.new_release }}'\n    state: finalize\n    clean: False\n- deploy_helper:\n    path: /path/to/root\n    state: clean\n# Or running the cleanup ahead of the new deploy\n- deploy_helper:\n    path: /path/to/root\n    state: clean\n- deploy_helper:\n    path: /path/to/root\n    state: present\n\n# Keeping more old releases:\n- deploy_helper:\n    path: /path/to/root\n    release: '{{ deploy_helper.new_release }}'\n    state: finalize\n    keep_releases: 10\n# Or, if you use 'clean=false' on finalize:\n- deploy_helper:\n    path: /path/to/root\n    state: clean\n    keep_releases: 10\n\n# Removing the entire project root folder\n- deploy_helper:\n    path: /path/to/root\n    state: absent\n\n# Debugging the facts returned by the module\n- deploy_helper:\n    path: /path/to/root\n- debug:\n    var: deploy_helper\n"
import os
import shutil
import time
import traceback
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils._text import to_native

class DeployHelper(object):

    def __init__(self, module):
        self.module = module
        self.file_args = module.load_file_common_arguments(module.params)
        self.clean = module.params['clean']
        self.current_path = module.params['current_path']
        self.keep_releases = module.params['keep_releases']
        self.path = module.params['path']
        self.release = module.params['release']
        self.releases_path = module.params['releases_path']
        self.shared_path = module.params['shared_path']
        self.state = module.params['state']
        self.unfinished_filename = module.params['unfinished_filename']

    def gather_facts(self):
        current_path = os.path.join(self.path, self.current_path)
        releases_path = os.path.join(self.path, self.releases_path)
        if self.shared_path:
            shared_path = os.path.join(self.path, self.shared_path)
        else:
            shared_path = None
        (previous_release, previous_release_path) = self._get_last_release(current_path)
        if not self.release and (self.state == 'query' or self.state == 'present'):
            self.release = time.strftime('%Y%m%d%H%M%S')
        if self.release:
            new_release_path = os.path.join(releases_path, self.release)
        else:
            new_release_path = None
        return {'project_path': self.path, 'current_path': current_path, 'releases_path': releases_path, 'shared_path': shared_path, 'previous_release': previous_release, 'previous_release_path': previous_release_path, 'new_release': self.release, 'new_release_path': new_release_path, 'unfinished_filename': self.unfinished_filename}

    def delete_path(self, path):
        if not os.path.lexists(path):
            return False
        if not os.path.isdir(path):
            self.module.fail_json(msg='%s exists but is not a directory' % path)
        if not self.module.check_mode:
            try:
                shutil.rmtree(path, ignore_errors=False)
            except Exception as e:
                self.module.fail_json(msg='rmtree failed: %s' % to_native(e), exception=traceback.format_exc())
        return True

    def create_path(self, path):
        changed = False
        if not os.path.lexists(path):
            changed = True
            if not self.module.check_mode:
                os.makedirs(path)
        elif not os.path.isdir(path):
            self.module.fail_json(msg='%s exists but is not a directory' % path)
        changed += self.module.set_directory_attributes_if_different(self._get_file_args(path), changed)
        return changed

    def check_link(self, path):
        if os.path.lexists(path):
            if not os.path.islink(path):
                self.module.fail_json(msg='%s exists but is not a symbolic link' % path)

    def create_link(self, source, link_name):
        changed = False
        if os.path.islink(link_name):
            norm_link = os.path.normpath(os.path.realpath(link_name))
            norm_source = os.path.normpath(os.path.realpath(source))
            if norm_link == norm_source:
                changed = False
            else:
                changed = True
                if not self.module.check_mode:
                    if not os.path.lexists(source):
                        self.module.fail_json(msg="the symlink target %s doesn't exists" % source)
                    tmp_link_name = link_name + '.' + self.unfinished_filename
                    if os.path.islink(tmp_link_name):
                        os.unlink(tmp_link_name)
                    os.symlink(source, tmp_link_name)
                    os.rename(tmp_link_name, link_name)
        else:
            changed = True
            if not self.module.check_mode:
                os.symlink(source, link_name)
        return changed

    def remove_unfinished_file(self, new_release_path):
        changed = False
        unfinished_file_path = os.path.join(new_release_path, self.unfinished_filename)
        if os.path.lexists(unfinished_file_path):
            changed = True
            if not self.module.check_mode:
                os.remove(unfinished_file_path)
        return changed

    def remove_unfinished_builds(self, releases_path):
        changes = 0
        for release in os.listdir(releases_path):
            if os.path.isfile(os.path.join(releases_path, release, self.unfinished_filename)):
                if self.module.check_mode:
                    changes += 1
                else:
                    changes += self.delete_path(os.path.join(releases_path, release))
        return changes

    def remove_unfinished_link(self, path):
        changed = False
        tmp_link_name = os.path.join(path, self.release + '.' + self.unfinished_filename)
        if not self.module.check_mode and os.path.exists(tmp_link_name):
            changed = True
            os.remove(tmp_link_name)
        return changed

    def cleanup(self, releases_path, reserve_version):
        changes = 0
        if os.path.lexists(releases_path):
            releases = [f for f in os.listdir(releases_path) if os.path.isdir(os.path.join(releases_path, f))]
            try:
                releases.remove(reserve_version)
            except ValueError:
                pass
            if not self.module.check_mode:
                releases.sort(key=lambda x: os.path.getctime(os.path.join(releases_path, x)), reverse=True)
                for release in releases[self.keep_releases:]:
                    changes += self.delete_path(os.path.join(releases_path, release))
            elif len(releases) > self.keep_releases:
                changes += len(releases) - self.keep_releases
        return changes

    def _get_file_args(self, path):
        file_args = self.file_args.copy()
        file_args['path'] = path
        return file_args

    def _get_last_release(self, current_path):
        previous_release = None
        previous_release_path = None
        if os.path.lexists(current_path):
            previous_release_path = os.path.realpath(current_path)
            previous_release = os.path.basename(previous_release_path)
        return (previous_release, previous_release_path)

def main():
    module = AnsibleModule(argument_spec=dict(path=dict(aliases=['dest'], required=True, type='path'), release=dict(required=False, type='str', default=None), releases_path=dict(required=False, type='str', default='releases'), shared_path=dict(required=False, type='path', default='shared'), current_path=dict(required=False, type='path', default='current'), keep_releases=dict(required=False, type='int', default=5), clean=dict(required=False, type='bool', default=True), unfinished_filename=dict(required=False, type='str', default='DEPLOY_UNFINISHED'), state=dict(required=False, choices=['present', 'absent', 'clean', 'finalize', 'query'], default='present')), add_file_common_args=True, supports_check_mode=True)
    deploy_helper = DeployHelper(module)
    facts = deploy_helper.gather_facts()
    result = {'state': deploy_helper.state}
    changes = 0
    if deploy_helper.state == 'query':
        result['ansible_facts'] = {'deploy_helper': facts}
    elif deploy_helper.state == 'present':
        deploy_helper.check_link(facts['current_path'])
        changes += deploy_helper.create_path(facts['project_path'])
        changes += deploy_helper.create_path(facts['releases_path'])
        if deploy_helper.shared_path:
            changes += deploy_helper.create_path(facts['shared_path'])
        result['ansible_facts'] = {'deploy_helper': facts}
    elif deploy_helper.state == 'finalize':
        if not deploy_helper.release:
            module.fail_json(msg="'release' is a required parameter for state=finalize (try the 'deploy_helper.new_release' fact)")
        if deploy_helper.keep_releases <= 0:
            module.fail_json(msg="'keep_releases' should be at least 1")
        changes += deploy_helper.remove_unfinished_file(facts['new_release_path'])
        changes += deploy_helper.create_link(facts['new_release_path'], facts['current_path'])
        if deploy_helper.clean:
            changes += deploy_helper.remove_unfinished_link(facts['project_path'])
            changes += deploy_helper.remove_unfinished_builds(facts['releases_path'])
            changes += deploy_helper.cleanup(facts['releases_path'], facts['new_release'])
    elif deploy_helper.state == 'clean':
        changes += deploy_helper.remove_unfinished_link(facts['project_path'])
        changes += deploy_helper.remove_unfinished_builds(facts['releases_path'])
        changes += deploy_helper.cleanup(facts['releases_path'], facts['new_release'])
    elif deploy_helper.state == 'absent':
        result['ansible_facts'] = {'deploy_helper': []}
        changes += deploy_helper.delete_path(facts['project_path'])
    if changes > 0:
        result['changed'] = True
    else:
        result['changed'] = False
    module.exit_json(**result)
if __name__ == '__main__':
    main()

def test_DeployHelper_gather_facts():
    ret = DeployHelper().gather_facts()

def test_DeployHelper_delete_path():
    ret = DeployHelper().delete_path()

def test_DeployHelper_create_path():
    ret = DeployHelper().create_path()

def test_DeployHelper_check_link():
    ret = DeployHelper().check_link()

def test_DeployHelper_create_link():
    ret = DeployHelper().create_link()

def test_DeployHelper_remove_unfinished_file():
    ret = DeployHelper().remove_unfinished_file()

def test_DeployHelper_remove_unfinished_builds():
    ret = DeployHelper().remove_unfinished_builds()

def test_DeployHelper_remove_unfinished_link():
    ret = DeployHelper().remove_unfinished_link()

def test_DeployHelper_cleanup():
    ret = DeployHelper().cleanup()

def test_DeployHelper__get_file_args():
    ret = DeployHelper()._get_file_args()

def test_DeployHelper__get_last_release():
    ret = DeployHelper()._get_last_release()