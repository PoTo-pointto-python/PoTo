from __future__ import absolute_import, division, print_function
__metaclass__ = type
ANSIBLE_METADATA = {'metadata_version': '1.1', 'status': ['preview'], 'supported_by': 'community'}
DOCUMENTATION = '\n---\nauthor:\n- Alexander Bulimov (@abulimov)\nmodule: lvg\nshort_description: Configure LVM volume groups\ndescription:\n  - This module creates, removes or resizes volume groups.\nversion_added: "1.1"\noptions:\n  vg:\n    description:\n    - The name of the volume group.\n    type: str\n    required: true\n  pvs:\n    description:\n    - List of comma-separated devices to use as physical devices in this volume group.\n    - Required when creating or resizing volume group.\n    - The module will take care of running pvcreate if needed.\n    type: list\n  pesize:\n    description:\n    - "The size of the physical extent. I(pesize) must be a power of 2 of at least 1 sector\n       (where the sector size is the largest sector size of the PVs currently used in the VG),\n       or at least 128KiB."\n    - Since Ansible 2.6, pesize can be optionally suffixed by a UNIT (k/K/m/M/g/G), default unit is megabyte.\n    type: str\n    default: "4"\n  pv_options:\n    description:\n    - Additional options to pass to C(pvcreate) when creating the volume group.\n    type: str\n    version_added: "2.4"\n  vg_options:\n    description:\n    - Additional options to pass to C(vgcreate) when creating the volume group.\n    type: str\n    version_added: "1.6"\n  state:\n    description:\n    - Control if the volume group exists.\n    type: str\n    choices: [ absent, present ]\n    default: present\n  force:\n    description:\n    - If C(yes), allows to remove volume group with logical volumes.\n    type: bool\n    default: no\nseealso:\n- module: filesystem\n- module: lvol\n- module: parted\nnotes:\n  - This module does not modify PE size for already present volume group.\n'
EXAMPLES = '\n- name: Create a volume group on top of /dev/sda1 with physical extent size = 32MB\n  lvg:\n    vg: vg.services\n    pvs: /dev/sda1\n    pesize: 32\n\n- name: Create a volume group on top of /dev/sdb with physical extent size = 128KiB\n  lvg:\n    vg: vg.services\n    pvs: /dev/sdb\n    pesize: 128K\n\n# If, for example, we already have VG vg.services on top of /dev/sdb1,\n# this VG will be extended by /dev/sdc5.  Or if vg.services was created on\n# top of /dev/sda5, we first extend it with /dev/sdb1 and /dev/sdc5,\n# and then reduce by /dev/sda5.\n- name: Create or resize a volume group on top of /dev/sdb1 and /dev/sdc5.\n  lvg:\n    vg: vg.services\n    pvs: /dev/sdb1,/dev/sdc5\n\n- name: Remove a volume group with name vg.services\n  lvg:\n    vg: vg.services\n    state: absent\n'
import itertools
import os
from ansible.module_utils.basic import AnsibleModule

def parse_vgs(data):
    vgs = []
    for line in data.splitlines():
        parts = line.strip().split(';')
        vgs.append({'name': parts[0], 'pv_count': int(parts[1]), 'lv_count': int(parts[2])})
    return vgs

def find_mapper_device_name(module, dm_device):
    dmsetup_cmd = module.get_bin_path('dmsetup', True)
    mapper_prefix = '/dev/mapper/'
    (rc, dm_name, err) = module.run_command('%s info -C --noheadings -o name %s' % (dmsetup_cmd, dm_device))
    if rc != 0:
        module.fail_json(msg='Failed executing dmsetup command.', rc=rc, err=err)
    mapper_device = mapper_prefix + dm_name.rstrip()
    return mapper_device

def parse_pvs(module, data):
    pvs = []
    dm_prefix = '/dev/dm-'
    for line in data.splitlines():
        parts = line.strip().split(';')
        if parts[0].startswith(dm_prefix):
            parts[0] = find_mapper_device_name(module, parts[0])
        pvs.append({'name': parts[0], 'vg_name': parts[1]})
    return pvs

def main():
    module = AnsibleModule(argument_spec=dict(vg=dict(type='str', required=True), pvs=dict(type='list'), pesize=dict(type='str', default='4'), pv_options=dict(type='str', default=''), vg_options=dict(type='str', default=''), state=dict(type='str', default='present', choices=['absent', 'present']), force=dict(type='bool', default=False)), supports_check_mode=True)
    vg = module.params['vg']
    state = module.params['state']
    force = module.boolean(module.params['force'])
    pesize = module.params['pesize']
    pvoptions = module.params['pv_options'].split()
    vgoptions = module.params['vg_options'].split()
    dev_list = []
    if module.params['pvs']:
        dev_list = list(module.params['pvs'])
    elif state == 'present':
        module.fail_json(msg='No physical volumes given.')
    for (idx, dev) in enumerate(dev_list):
        dev_list[idx] = os.path.realpath(dev)
    if state == 'present':
        for test_dev in dev_list:
            if not os.path.exists(test_dev):
                module.fail_json(msg='Device %s not found.' % test_dev)
        pvs_cmd = module.get_bin_path('pvs', True)
        if dev_list:
            pvs_filter_pv_name = ' || '.join(('pv_name = {0}'.format(x) for x in itertools.chain(dev_list, module.params['pvs'])))
            pvs_filter_vg_name = 'vg_name = {0}'.format(vg)
            pvs_filter = "--select '{0} || {1}' ".format(pvs_filter_pv_name, pvs_filter_vg_name)
        else:
            pvs_filter = ''
        (rc, current_pvs, err) = module.run_command("%s --noheadings -o pv_name,vg_name --separator ';' %s" % (pvs_cmd, pvs_filter))
        if rc != 0:
            module.fail_json(msg='Failed executing pvs command.', rc=rc, err=err)
        pvs = parse_pvs(module, current_pvs)
        used_pvs = [pv for pv in pvs if pv['name'] in dev_list and pv['vg_name'] and (pv['vg_name'] != vg)]
        if used_pvs:
            module.fail_json(msg='Device %s is already in %s volume group.' % (used_pvs[0]['name'], used_pvs[0]['vg_name']))
    vgs_cmd = module.get_bin_path('vgs', True)
    (rc, current_vgs, err) = module.run_command("%s --noheadings -o vg_name,pv_count,lv_count --separator ';'" % vgs_cmd)
    if rc != 0:
        module.fail_json(msg='Failed executing vgs command.', rc=rc, err=err)
    changed = False
    vgs = parse_vgs(current_vgs)
    for test_vg in vgs:
        if test_vg['name'] == vg:
            this_vg = test_vg
            break
    else:
        this_vg = None
    if this_vg is None:
        if state == 'present':
            if module.check_mode:
                changed = True
            else:
                pvcreate_cmd = module.get_bin_path('pvcreate', True)
                for current_dev in dev_list:
                    (rc, _, err) = module.run_command([pvcreate_cmd] + pvoptions + ['-f', str(current_dev)])
                    if rc == 0:
                        changed = True
                    else:
                        module.fail_json(msg="Creating physical volume '%s' failed" % current_dev, rc=rc, err=err)
                vgcreate_cmd = module.get_bin_path('vgcreate')
                (rc, _, err) = module.run_command([vgcreate_cmd] + vgoptions + ['-s', pesize, vg] + dev_list)
                if rc == 0:
                    changed = True
                else:
                    module.fail_json(msg="Creating volume group '%s' failed" % vg, rc=rc, err=err)
    else:
        if state == 'absent':
            if module.check_mode:
                module.exit_json(changed=True)
            elif this_vg['lv_count'] == 0 or force:
                vgremove_cmd = module.get_bin_path('vgremove', True)
                (rc, _, err) = module.run_command('%s --force %s' % (vgremove_cmd, vg))
                if rc == 0:
                    module.exit_json(changed=True)
                else:
                    module.fail_json(msg='Failed to remove volume group %s' % vg, rc=rc, err=err)
            else:
                module.fail_json(msg='Refuse to remove non-empty volume group %s without force=yes' % vg)
        current_devs = [os.path.realpath(pv['name']) for pv in pvs if pv['vg_name'] == vg]
        devs_to_remove = list(set(current_devs) - set(dev_list))
        devs_to_add = list(set(dev_list) - set(current_devs))
        if devs_to_add or devs_to_remove:
            if module.check_mode:
                changed = True
            else:
                if devs_to_add:
                    devs_to_add_string = ' '.join(devs_to_add)
                    pvcreate_cmd = module.get_bin_path('pvcreate', True)
                    for current_dev in devs_to_add:
                        (rc, _, err) = module.run_command([pvcreate_cmd] + pvoptions + ['-f', str(current_dev)])
                        if rc == 0:
                            changed = True
                        else:
                            module.fail_json(msg="Creating physical volume '%s' failed" % current_dev, rc=rc, err=err)
                    vgextend_cmd = module.get_bin_path('vgextend', True)
                    (rc, _, err) = module.run_command('%s %s %s' % (vgextend_cmd, vg, devs_to_add_string))
                    if rc == 0:
                        changed = True
                    else:
                        module.fail_json(msg='Unable to extend %s by %s.' % (vg, devs_to_add_string), rc=rc, err=err)
                if devs_to_remove:
                    devs_to_remove_string = ' '.join(devs_to_remove)
                    vgreduce_cmd = module.get_bin_path('vgreduce', True)
                    (rc, _, err) = module.run_command('%s --force %s %s' % (vgreduce_cmd, vg, devs_to_remove_string))
                    if rc == 0:
                        changed = True
                    else:
                        module.fail_json(msg='Unable to reduce %s by %s.' % (vg, devs_to_remove_string), rc=rc, err=err)
    module.exit_json(changed=changed)
if __name__ == '__main__':
    main()