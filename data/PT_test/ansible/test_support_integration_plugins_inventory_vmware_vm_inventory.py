from __future__ import absolute_import, division, print_function
__metaclass__ = type
DOCUMENTATION = '\n    name: vmware_vm_inventory\n    plugin_type: inventory\n    short_description: VMware Guest inventory source\n    version_added: "2.7"\n    author:\n      - Abhijeet Kasurde (@Akasurde)\n    description:\n        - Get virtual machines as inventory hosts from VMware environment.\n        - Uses any file which ends with vmware.yml, vmware.yaml, vmware_vm_inventory.yml, or vmware_vm_inventory.yaml as a YAML configuration file.\n        - The inventory_hostname is always the \'Name\' and UUID of the virtual machine. UUID is added as VMware allows virtual machines with the same name.\n    extends_documentation_fragment:\n      - inventory_cache\n    requirements:\n      - "Python >= 2.7"\n      - "PyVmomi"\n      - "requests >= 2.3"\n      - "vSphere Automation SDK - For tag feature"\n      - "vCloud Suite SDK - For tag feature"\n    options:\n        hostname:\n            description: Name of vCenter or ESXi server.\n            required: True\n            env:\n              - name: VMWARE_HOST\n              - name: VMWARE_SERVER\n        username:\n            description: Name of vSphere admin user.\n            required: True\n            env:\n              - name: VMWARE_USER\n              - name: VMWARE_USERNAME\n        password:\n            description: Password of vSphere admin user.\n            required: True\n            env:\n              - name: VMWARE_PASSWORD\n        port:\n            description: Port number used to connect to vCenter or ESXi Server.\n            default: 443\n            env:\n              - name: VMWARE_PORT\n        validate_certs:\n            description:\n            - Allows connection when SSL certificates are not valid. Set to C(false) when certificates are not trusted.\n            default: True\n            type: boolean\n            env:\n              - name: VMWARE_VALIDATE_CERTS\n        with_tags:\n            description:\n            - Include tags and associated virtual machines.\n            - Requires \'vSphere Automation SDK\' library to be installed on the given controller machine.\n            - Please refer following URLs for installation steps\n            - \'https://code.vmware.com/web/sdk/65/vsphere-automation-python\'\n            default: False\n            type: boolean\n        properties:\n            description:\n            - Specify the list of VMware schema properties associated with the VM.\n            - These properties will be populated in hostvars of the given VM.\n            - Each value in the list specifies the path to a specific property in VM object.\n            type: list\n            default: [ \'name\', \'config.cpuHotAddEnabled\', \'config.cpuHotRemoveEnabled\',\n                       \'config.instanceUuid\', \'config.hardware.numCPU\', \'config.template\',\n                       \'config.name\', \'guest.hostName\', \'guest.ipAddress\',\n                       \'guest.guestId\', \'guest.guestState\', \'runtime.maxMemoryUsage\',\n                       \'customValue\'\n                       ]\n            version_added: "2.9"\n'
EXAMPLES = "\n# Sample configuration file for VMware Guest dynamic inventory\n    plugin: vmware_vm_inventory\n    strict: False\n    hostname: 10.65.223.31\n    username: administrator@vsphere.local\n    password: Esxi@123$%\n    validate_certs: False\n    with_tags: True\n\n# Gather minimum set of properties for VMware guest\n    plugin: vmware_vm_inventory\n    strict: False\n    hostname: 10.65.223.31\n    username: administrator@vsphere.local\n    password: Esxi@123$%\n    validate_certs: False\n    with_tags: False\n    properties:\n    - 'name'\n    - 'guest.ipAddress'\n"
import ssl
import atexit
from ansible.errors import AnsibleError, AnsibleParserError
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False
try:
    from pyVim import connect
    from pyVmomi import vim, vmodl
    HAS_PYVMOMI = True
except ImportError:
    HAS_PYVMOMI = False
try:
    from com.vmware.vapi.std_client import DynamicID
    from vmware.vapi.vsphere.client import create_vsphere_client
    HAS_VSPHERE = True
except ImportError:
    HAS_VSPHERE = False
from ansible.plugins.inventory import BaseInventoryPlugin, Cacheable

class BaseVMwareInventory:

    def __init__(self, hostname, username, password, port, validate_certs, with_tags):
        self.hostname = hostname
        self.username = username
        self.password = password
        self.port = port
        self.with_tags = with_tags
        self.validate_certs = validate_certs
        self.content = None
        self.rest_content = None

    def do_login(self):
        """
        Check requirements and do login
        """
        self.check_requirements()
        self.content = self._login()
        if self.with_tags:
            self.rest_content = self._login_vapi()

    def _login_vapi(self):
        """
        Login to vCenter API using REST call
        Returns: connection object

        """
        session = requests.Session()
        session.verify = self.validate_certs
        if not self.validate_certs:
            requests.packages.urllib3.disable_warnings()
        server = self.hostname
        if self.port:
            server += ':' + str(self.port)
        client = create_vsphere_client(server=server, username=self.username, password=self.password, session=session)
        if client is None:
            raise AnsibleError('Failed to login to %s using %s' % (server, self.username))
        return client

    def _login(self):
        """
        Login to vCenter or ESXi server
        Returns: connection object

        """
        if self.validate_certs and (not hasattr(ssl, 'SSLContext')):
            raise AnsibleError('pyVim does not support changing verification mode with python < 2.7.9. Either update python or set validate_certs to false in configuration YAML file.')
        ssl_context = None
        if not self.validate_certs and hasattr(ssl, 'SSLContext'):
            ssl_context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
            ssl_context.verify_mode = ssl.CERT_NONE
        service_instance = None
        try:
            service_instance = connect.SmartConnect(host=self.hostname, user=self.username, pwd=self.password, sslContext=ssl_context, port=self.port)
        except vim.fault.InvalidLogin as e:
            raise AnsibleParserError('Unable to log on to vCenter or ESXi API at %s:%s as %s: %s' % (self.hostname, self.port, self.username, e.msg))
        except vim.fault.NoPermission as e:
            raise AnsibleParserError('User %s does not have required permission to log on to vCenter or ESXi API at %s:%s : %s' % (self.username, self.hostname, self.port, e.msg))
        except (requests.ConnectionError, ssl.SSLError) as e:
            raise AnsibleParserError('Unable to connect to vCenter or ESXi API at %s on TCP/%s: %s' % (self.hostname, self.port, e))
        except vmodl.fault.InvalidRequest as e:
            raise AnsibleParserError('Failed to get a response from server %s:%s as request is malformed: %s' % (self.hostname, self.port, e.msg))
        except Exception as e:
            raise AnsibleParserError('Unknown error while connecting to vCenter or ESXi API at %s:%s : %s' % (self.hostname, self.port, e))
        if service_instance is None:
            raise AnsibleParserError('Unknown error while connecting to vCenter or ESXi API at %s:%s' % (self.hostname, self.port))
        atexit.register(connect.Disconnect, service_instance)
        return service_instance.RetrieveContent()

    def check_requirements(self):
        """ Check all requirements for this inventory are satisified"""
        if not HAS_REQUESTS:
            raise AnsibleParserError('Please install "requests" Python module as this is required for VMware Guest dynamic inventory plugin.')
        elif not HAS_PYVMOMI:
            raise AnsibleParserError('Please install "PyVmomi" Python module as this is required for VMware Guest dynamic inventory plugin.')
        if HAS_REQUESTS:
            required_version = (2, 3)
            requests_version = requests.__version__.split('.')[:2]
            try:
                requests_major_minor = tuple(map(int, requests_version))
            except ValueError:
                raise AnsibleParserError("Failed to parse 'requests' library version.")
            if requests_major_minor < required_version:
                raise AnsibleParserError("'requests' library version should be >= %s, found: %s." % ('.'.join([str(w) for w in required_version]), requests.__version__))
        if not HAS_VSPHERE and self.with_tags:
            raise AnsibleError("Unable to find 'vSphere Automation SDK' Python library which is required. Please refer this URL for installation steps - https://code.vmware.com/web/sdk/65/vsphere-automation-python")
        if not all([self.hostname, self.username, self.password]):
            raise AnsibleError('Missing one of the following : hostname, username, password. Please read the documentation for more information.')

    def _get_managed_objects_properties(self, vim_type, properties=None):
        """
        Look up a Managed Object Reference in vCenter / ESXi Environment
        :param vim_type: Type of vim object e.g, for datacenter - vim.Datacenter
        :param properties: List of properties related to vim object e.g. Name
        :return: local content object
        """
        root_folder = self.content.rootFolder
        if properties is None:
            properties = ['name']
        mor = self.content.viewManager.CreateContainerView(root_folder, [vim_type], True)
        traversal_spec = vmodl.query.PropertyCollector.TraversalSpec(name='traversal_spec', path='view', skip=False, type=vim.view.ContainerView)
        property_spec = vmodl.query.PropertyCollector.PropertySpec(type=vim_type, all=False, pathSet=properties)
        object_spec = vmodl.query.PropertyCollector.ObjectSpec(obj=mor, skip=True, selectSet=[traversal_spec])
        filter_spec = vmodl.query.PropertyCollector.FilterSpec(objectSet=[object_spec], propSet=[property_spec], reportMissingObjectsInResults=False)
        return self.content.propertyCollector.RetrieveContents([filter_spec])

    @staticmethod
    def _get_object_prop(vm, attributes):
        """Safely get a property or return None"""
        result = vm
        for attribute in attributes:
            try:
                result = getattr(result, attribute)
            except (AttributeError, IndexError):
                return None
        return result

class InventoryModule(BaseInventoryPlugin, Cacheable):
    NAME = 'vmware_vm_inventory'

    def verify_file(self, path):
        """
        Verify plugin configuration file and mark this plugin active
        Args:
            path: Path of configuration YAML file
        Returns: True if everything is correct, else False
        """
        valid = False
        if super(InventoryModule, self).verify_file(path):
            if path.endswith(('vmware.yaml', 'vmware.yml', 'vmware_vm_inventory.yaml', 'vmware_vm_inventory.yml')):
                valid = True
        return valid

    def parse(self, inventory, loader, path, cache=True):
        """
        Parses the inventory file
        """
        super(InventoryModule, self).parse(inventory, loader, path, cache=cache)
        cache_key = self.get_cache_key(path)
        config_data = self._read_config_data(path)
        self._consume_options(config_data)
        self.pyv = BaseVMwareInventory(hostname=self.get_option('hostname'), username=self.get_option('username'), password=self.get_option('password'), port=self.get_option('port'), with_tags=self.get_option('with_tags'), validate_certs=self.get_option('validate_certs'))
        self.pyv.do_login()
        self.pyv.check_requirements()
        source_data = None
        if cache:
            cache = self.get_option('cache')
        update_cache = False
        if cache:
            try:
                source_data = self._cache[cache_key]
            except KeyError:
                update_cache = True
        using_current_cache = cache and (not update_cache)
        cacheable_results = self._populate_from_source(source_data, using_current_cache)
        if update_cache:
            self._cache[cache_key] = cacheable_results

    def _populate_from_cache(self, source_data):
        """ Populate cache using source data """
        hostvars = source_data.pop('_meta', {}).get('hostvars', {})
        for group in source_data:
            if group == 'all':
                continue
            else:
                self.inventory.add_group(group)
                hosts = source_data[group].get('hosts', [])
                for host in hosts:
                    self._populate_host_vars([host], hostvars.get(host, {}), group)
                self.inventory.add_child('all', group)

    def _populate_from_source(self, source_data, using_current_cache):
        """
        Populate inventory data from direct source

        """
        if using_current_cache:
            self._populate_from_cache(source_data)
            return source_data
        cacheable_results = {'_meta': {'hostvars': {}}}
        hostvars = {}
        objects = self.pyv._get_managed_objects_properties(vim_type=vim.VirtualMachine, properties=['name'])
        if self.pyv.with_tags:
            tag_svc = self.pyv.rest_content.tagging.Tag
            tag_association = self.pyv.rest_content.tagging.TagAssociation
            tags_info = dict()
            tags = tag_svc.list()
            for tag in tags:
                tag_obj = tag_svc.get(tag)
                tags_info[tag_obj.id] = tag_obj.name
                if tag_obj.name not in cacheable_results:
                    cacheable_results[tag_obj.name] = {'hosts': []}
                    self.inventory.add_group(tag_obj.name)
        for vm_obj in objects:
            for vm_obj_property in vm_obj.propSet:
                if not vm_obj.obj.config:
                    continue
                current_host = vm_obj_property.val + '_' + vm_obj.obj.config.uuid
                if current_host not in hostvars:
                    hostvars[current_host] = {}
                    self.inventory.add_host(current_host)
                    host_ip = vm_obj.obj.guest.ipAddress
                    if host_ip:
                        self.inventory.set_variable(current_host, 'ansible_host', host_ip)
                    self._populate_host_properties(vm_obj, current_host)
                    if HAS_VSPHERE and self.pyv.with_tags:
                        vm_mo_id = vm_obj.obj._GetMoId()
                        vm_dynamic_id = DynamicID(type='VirtualMachine', id=vm_mo_id)
                        attached_tags = tag_association.list_attached_tags(vm_dynamic_id)
                        for tag_id in attached_tags:
                            self.inventory.add_child(tags_info[tag_id], current_host)
                            cacheable_results[tags_info[tag_id]]['hosts'].append(current_host)
                    vm_power = str(vm_obj.obj.summary.runtime.powerState)
                    if vm_power not in cacheable_results:
                        cacheable_results[vm_power] = {'hosts': []}
                        self.inventory.add_group(vm_power)
                    cacheable_results[vm_power]['hosts'].append(current_host)
                    self.inventory.add_child(vm_power, current_host)
                    vm_guest_id = vm_obj.obj.config.guestId
                    if vm_guest_id and vm_guest_id not in cacheable_results:
                        cacheable_results[vm_guest_id] = {'hosts': []}
                        self.inventory.add_group(vm_guest_id)
                    cacheable_results[vm_guest_id]['hosts'].append(current_host)
                    self.inventory.add_child(vm_guest_id, current_host)
        for host in hostvars:
            h = self.inventory.get_host(host)
            cacheable_results['_meta']['hostvars'][h.name] = h.vars
        return cacheable_results

    def _populate_host_properties(self, vm_obj, current_host):
        vm_properties = self.get_option('properties') or []
        field_mgr = self.pyv.content.customFieldsManager.field
        for vm_prop in vm_properties:
            if vm_prop == 'customValue':
                for cust_value in vm_obj.obj.customValue:
                    self.inventory.set_variable(current_host, [y.name for y in field_mgr if y.key == cust_value.key][0], cust_value.value)
            else:
                vm_value = self.pyv._get_object_prop(vm_obj.obj, vm_prop.split('.'))
                self.inventory.set_variable(current_host, vm_prop, vm_value)

def test_BaseVMwareInventory_do_login():
    ret = BaseVMwareInventory().do_login()

def test_BaseVMwareInventory__login_vapi():
    ret = BaseVMwareInventory()._login_vapi()

def test_BaseVMwareInventory__login():
    ret = BaseVMwareInventory()._login()

def test_BaseVMwareInventory_check_requirements():
    ret = BaseVMwareInventory().check_requirements()

def test_BaseVMwareInventory__get_managed_objects_properties():
    ret = BaseVMwareInventory()._get_managed_objects_properties()

def test_BaseVMwareInventory__get_object_prop():
    ret = BaseVMwareInventory()._get_object_prop()

def test_InventoryModule_verify_file():
    ret = InventoryModule().verify_file()

def test_InventoryModule_parse():
    ret = InventoryModule().parse()

def test_InventoryModule__populate_from_cache():
    ret = InventoryModule()._populate_from_cache()

def test_InventoryModule__populate_from_source():
    ret = InventoryModule()._populate_from_source()

def test_InventoryModule__populate_host_properties():
    ret = InventoryModule()._populate_host_properties()