from __future__ import absolute_import, division, print_function
__metaclass__ = type
ANSIBLE_METADATA = {'metadata_version': '1.1', 'status': ['preview'], 'supported_by': 'community'}
DOCUMENTATION = "\n---\nmodule: xml\nshort_description: Manage bits and pieces of XML files or strings\ndescription:\n- A CRUD-like interface to managing bits of XML files.\nversion_added: '2.4'\noptions:\n  path:\n    description:\n    - Path to the file to operate on.\n    - This file must exist ahead of time.\n    - This parameter is required, unless C(xmlstring) is given.\n    type: path\n    required: yes\n    aliases: [ dest, file ]\n  xmlstring:\n    description:\n    - A string containing XML on which to operate.\n    - This parameter is required, unless C(path) is given.\n    type: str\n    required: yes\n  xpath:\n    description:\n    - A valid XPath expression describing the item(s) you want to manipulate.\n    - Operates on the document root, C(/), by default.\n    type: str\n  namespaces:\n    description:\n    - The namespace C(prefix:uri) mapping for the XPath expression.\n    - Needs to be a C(dict), not a C(list) of items.\n    type: dict\n  state:\n    description:\n    - Set or remove an xpath selection (node(s), attribute(s)).\n    type: str\n    choices: [ absent, present ]\n    default: present\n    aliases: [ ensure ]\n  attribute:\n    description:\n    - The attribute to select when using parameter C(value).\n    - This is a string, not prepended with C(@).\n    type: raw\n  value:\n    description:\n    - Desired state of the selected attribute.\n    - Either a string, or to unset a value, the Python C(None) keyword (YAML Equivalent, C(null)).\n    - Elements default to no value (but present).\n    - Attributes default to an empty string.\n    type: raw\n  add_children:\n    description:\n    - Add additional child-element(s) to a selected element for a given C(xpath).\n    - Child elements must be given in a list and each item may be either a string\n      (eg. C(children=ansible) to add an empty C(<ansible/>) child element),\n      or a hash where the key is an element name and the value is the element value.\n    - This parameter requires C(xpath) to be set.\n    type: list\n  set_children:\n    description:\n    - Set the child-element(s) of a selected element for a given C(xpath).\n    - Removes any existing children.\n    - Child elements must be specified as in C(add_children).\n    - This parameter requires C(xpath) to be set.\n    type: list\n  count:\n    description:\n    - Search for a given C(xpath) and provide the count of any matches.\n    - This parameter requires C(xpath) to be set.\n    type: bool\n    default: no\n  print_match:\n    description:\n    - Search for a given C(xpath) and print out any matches.\n    - This parameter requires C(xpath) to be set.\n    type: bool\n    default: no\n  pretty_print:\n    description:\n    - Pretty print XML output.\n    type: bool\n    default: no\n  content:\n    description:\n    - Search for a given C(xpath) and get content.\n    - This parameter requires C(xpath) to be set.\n    type: str\n    choices: [ attribute, text ]\n  input_type:\n    description:\n    - Type of input for C(add_children) and C(set_children).\n    type: str\n    choices: [ xml, yaml ]\n    default: yaml\n  backup:\n    description:\n      - Create a backup file including the timestamp information so you can get\n        the original file back if you somehow clobbered it incorrectly.\n    type: bool\n    default: no\n  strip_cdata_tags:\n    description:\n      - Remove CDATA tags surrounding text values.\n      - Note that this might break your XML file if text values contain characters that could be interpreted as XML.\n    type: bool\n    default: no\n    version_added: '2.7'\n  insertbefore:\n    description:\n      - Add additional child-element(s) before the first selected element for a given C(xpath).\n      - Child elements must be given in a list and each item may be either a string\n        (eg. C(children=ansible) to add an empty C(<ansible/>) child element),\n        or a hash where the key is an element name and the value is the element value.\n      - This parameter requires C(xpath) to be set.\n    type: bool\n    default: no\n    version_added: '2.8'\n  insertafter:\n    description:\n      - Add additional child-element(s) after the last selected element for a given C(xpath).\n      - Child elements must be given in a list and each item may be either a string\n        (eg. C(children=ansible) to add an empty C(<ansible/>) child element),\n        or a hash where the key is an element name and the value is the element value.\n      - This parameter requires C(xpath) to be set.\n    type: bool\n    default: no\n    version_added: '2.8'\nrequirements:\n- lxml >= 2.3.0\nnotes:\n- Use the C(--check) and C(--diff) options when testing your expressions.\n- The diff output is automatically pretty-printed, so may not reflect the actual file content, only the file structure.\n- This module does not handle complicated xpath expressions, so limit xpath selectors to simple expressions.\n- Beware that in case your XML elements are namespaced, you need to use the C(namespaces) parameter, see the examples.\n- Namespaces prefix should be used for all children of an element where namespace is defined, unless another namespace is defined for them.\nseealso:\n- name: Xml module development community wiki\n  description: More information related to the development of this xml module.\n  link: https://github.com/ansible/community/wiki/Module:-xml\n- name: Introduction to XPath\n  description: A brief tutorial on XPath (w3schools.com).\n  link: https://www.w3schools.com/xml/xpath_intro.asp\n- name: XPath Reference document\n  description: The reference documentation on XSLT/XPath (developer.mozilla.org).\n  link: https://developer.mozilla.org/en-US/docs/Web/XPath\nauthor:\n- Tim Bielawa (@tbielawa)\n- Magnus Hedemark (@magnus919)\n- Dag Wieers (@dagwieers)\n"
EXAMPLES = '\n# Consider the following XML file:\n#\n# <business type="bar">\n#   <name>Tasty Beverage Co.</name>\n#     <beers>\n#       <beer>Rochefort 10</beer>\n#       <beer>St. Bernardus Abbot 12</beer>\n#       <beer>Schlitz</beer>\n#    </beers>\n#   <rating subjective="true">10</rating>\n#   <website>\n#     <mobilefriendly/>\n#     <address>http://tastybeverageco.com</address>\n#   </website>\n# </business>\n\n- name: Remove the \'subjective\' attribute of the \'rating\' element\n  xml:\n    path: /foo/bar.xml\n    xpath: /business/rating/@subjective\n    state: absent\n\n- name: Set the rating to \'11\'\n  xml:\n    path: /foo/bar.xml\n    xpath: /business/rating\n    value: 11\n\n# Retrieve and display the number of nodes\n- name: Get count of \'beers\' nodes\n  xml:\n    path: /foo/bar.xml\n    xpath: /business/beers/beer\n    count: yes\n  register: hits\n\n- debug:\n    var: hits.count\n\n# Example where parent XML nodes are created automatically\n- name: Add a \'phonenumber\' element to the \'business\' element\n  xml:\n    path: /foo/bar.xml\n    xpath: /business/phonenumber\n    value: 555-555-1234\n\n- name: Add several more beers to the \'beers\' element\n  xml:\n    path: /foo/bar.xml\n    xpath: /business/beers\n    add_children:\n    - beer: Old Rasputin\n    - beer: Old Motor Oil\n    - beer: Old Curmudgeon\n\n- name: Add several more beers to the \'beers\' element and add them before the \'Rochefort 10\' element\n  xml:\n    path: /foo/bar.xml\n    xpath: \'/business/beers/beer[text()="Rochefort 10"]\'\n    insertbefore: yes\n    add_children:\n    - beer: Old Rasputin\n    - beer: Old Motor Oil\n    - beer: Old Curmudgeon\n\n# NOTE: The \'state\' defaults to \'present\' and \'value\' defaults to \'null\' for elements\n- name: Add a \'validxhtml\' element to the \'website\' element\n  xml:\n    path: /foo/bar.xml\n    xpath: /business/website/validxhtml\n\n- name: Add an empty \'validatedon\' attribute to the \'validxhtml\' element\n  xml:\n    path: /foo/bar.xml\n    xpath: /business/website/validxhtml/@validatedon\n\n- name: Add or modify an attribute, add element if needed\n  xml:\n    path: /foo/bar.xml\n    xpath: /business/website/validxhtml\n    attribute: validatedon\n    value: 1976-08-05\n\n# How to read an attribute value and access it in Ansible\n- name: Read an element\'s attribute values\n  xml:\n    path: /foo/bar.xml\n    xpath: /business/website/validxhtml\n    content: attribute\n  register: xmlresp\n\n- name: Show an attribute value\n  debug:\n    var: xmlresp.matches[0].validxhtml.validatedon\n\n- name: Remove all children from the \'website\' element (option 1)\n  xml:\n    path: /foo/bar.xml\n    xpath: /business/website/*\n    state: absent\n\n- name: Remove all children from the \'website\' element (option 2)\n  xml:\n    path: /foo/bar.xml\n    xpath: /business/website\n    children: []\n\n# In case of namespaces, like in below XML, they have to be explicitly stated.\n#\n# <foo xmlns="http://x.test" xmlns:attr="http://z.test">\n#   <bar>\n#     <baz xmlns="http://y.test" attr:my_namespaced_attribute="true" />\n#   </bar>\n# </foo>\n\n# NOTE: There is the prefix \'x\' in front of the \'bar\' element, too.\n- name: Set namespaced \'/x:foo/x:bar/y:baz/@z:my_namespaced_attribute\' to \'false\'\n  xml:\n    path: foo.xml\n    xpath: /x:foo/x:bar/y:baz\n    namespaces:\n      x: http://x.test\n      y: http://y.test\n      z: http://z.test\n    attribute: z:my_namespaced_attribute\n    value: \'false\'\n'
RETURN = "\nactions:\n    description: A dictionary with the original xpath, namespaces and state.\n    type: dict\n    returned: success\n    sample: {xpath: xpath, namespaces: [namespace1, namespace2], state=present}\nbackup_file:\n    description: The name of the backup file that was created\n    type: str\n    returned: when backup=yes\n    sample: /path/to/file.xml.1942.2017-08-24@14:16:01~\ncount:\n    description: The count of xpath matches.\n    type: int\n    returned: when parameter 'count' is set\n    sample: 2\nmatches:\n    description: The xpath matches found.\n    type: list\n    returned: when parameter 'print_match' is set\nmsg:\n    description: A message related to the performed action(s).\n    type: str\n    returned: always\nxmlstring:\n    description: An XML string of the resulting output.\n    type: str\n    returned: when parameter 'xmlstring' is set\n"
import copy
import json
import os
import re
import traceback
from distutils.version import LooseVersion
from io import BytesIO
LXML_IMP_ERR = None
try:
    from lxml import etree, objectify
    HAS_LXML = True
except ImportError:
    LXML_IMP_ERR = traceback.format_exc()
    HAS_LXML = False
from ansible.module_utils.basic import AnsibleModule, json_dict_bytes_to_unicode, missing_required_lib
from ansible.module_utils.six import iteritems, string_types
from ansible.module_utils._text import to_bytes, to_native
from ansible.module_utils.common._collections_compat import MutableMapping
_IDENT = '[a-zA-Z-][a-zA-Z0-9_\\-\\.]*'
_NSIDENT = _IDENT + '|' + _IDENT + ':' + _IDENT
_XPSTR = '(\'(?:.*)\'|"(?:.*)")'
_RE_SPLITSIMPLELAST = re.compile('^(.*)/(' + _NSIDENT + ')$')
_RE_SPLITSIMPLELASTEQVALUE = re.compile('^(.*)/(' + _NSIDENT + ')/text\\(\\)=' + _XPSTR + '$')
_RE_SPLITSIMPLEATTRLAST = re.compile('^(.*)/(@(?:' + _NSIDENT + '))$')
_RE_SPLITSIMPLEATTRLASTEQVALUE = re.compile('^(.*)/(@(?:' + _NSIDENT + '))=' + _XPSTR + '$')
_RE_SPLITSUBLAST = re.compile('^(.*)/(' + _NSIDENT + ')\\[(.*)\\]$')
_RE_SPLITONLYEQVALUE = re.compile('^(.*)/text\\(\\)=' + _XPSTR + '$')

def has_changed(doc):
    orig_obj = etree.tostring(objectify.fromstring(etree.tostring(orig_doc)))
    obj = etree.tostring(objectify.fromstring(etree.tostring(doc)))
    return orig_obj != obj

def do_print_match(module, tree, xpath, namespaces):
    match = tree.xpath(xpath, namespaces=namespaces)
    match_xpaths = []
    for m in match:
        match_xpaths.append(tree.getpath(m))
    match_str = json.dumps(match_xpaths)
    msg = "selector '%s' match: %s" % (xpath, match_str)
    finish(module, tree, xpath, namespaces, changed=False, msg=msg)

def count_nodes(module, tree, xpath, namespaces):
    """ Return the count of nodes matching the xpath """
    hits = tree.xpath('count(/%s)' % xpath, namespaces=namespaces)
    msg = 'found %d nodes' % hits
    finish(module, tree, xpath, namespaces, changed=False, msg=msg, hitcount=int(hits))

def is_node(tree, xpath, namespaces):
    """ Test if a given xpath matches anything and if that match is a node.

    For now we just assume you're only searching for one specific thing."""
    if xpath_matches(tree, xpath, namespaces):
        match = tree.xpath(xpath, namespaces=namespaces)
        if isinstance(match[0], etree._Element):
            return True
    return False

def is_attribute(tree, xpath, namespaces):
    """ Test if a given xpath matches and that match is an attribute

    An xpath attribute search will only match one item"""
    if xpath_matches(tree, xpath, namespaces):
        match = tree.xpath(xpath, namespaces=namespaces)
        if isinstance(match[0], etree._ElementStringResult):
            return True
        elif isinstance(match[0], etree._ElementUnicodeResult):
            return True
    return False

def xpath_matches(tree, xpath, namespaces):
    """ Test if a node exists """
    if tree.xpath(xpath, namespaces=namespaces):
        return True
    return False

def delete_xpath_target(module, tree, xpath, namespaces):
    """ Delete an attribute or element from a tree """
    try:
        for result in tree.xpath(xpath, namespaces=namespaces):
            if is_attribute(tree, xpath, namespaces):
                parent = result.getparent()
                parent.attrib.pop(result.attrname)
            elif is_node(tree, xpath, namespaces):
                result.getparent().remove(result)
            else:
                raise Exception('Impossible error')
    except Exception as e:
        module.fail_json(msg="Couldn't delete xpath target: %s (%s)" % (xpath, e))
    else:
        finish(module, tree, xpath, namespaces, changed=True)

def replace_children_of(children, match):
    for element in list(match):
        match.remove(element)
    match.extend(children)

def set_target_children_inner(module, tree, xpath, namespaces, children, in_type):
    matches = tree.xpath(xpath, namespaces=namespaces)
    children = children_to_nodes(module, children, in_type)
    children_as_string = [etree.tostring(c) for c in children]
    changed = False
    for match in matches:
        if len(list(match)) == len(children):
            for (idx, element) in enumerate(list(match)):
                if etree.tostring(element) != children_as_string[idx]:
                    replace_children_of(children, match)
                    changed = True
                    break
        else:
            replace_children_of(children, match)
            changed = True
    return changed

def set_target_children(module, tree, xpath, namespaces, children, in_type):
    changed = set_target_children_inner(module, tree, xpath, namespaces, children, in_type)
    finish(module, tree, xpath, namespaces, changed=changed)

def add_target_children(module, tree, xpath, namespaces, children, in_type, insertbefore, insertafter):
    if is_node(tree, xpath, namespaces):
        new_kids = children_to_nodes(module, children, in_type)
        if insertbefore or insertafter:
            insert_target_children(tree, xpath, namespaces, new_kids, insertbefore, insertafter)
        else:
            for node in tree.xpath(xpath, namespaces=namespaces):
                node.extend(new_kids)
        finish(module, tree, xpath, namespaces, changed=True)
    else:
        finish(module, tree, xpath, namespaces)

def insert_target_children(tree, xpath, namespaces, children, insertbefore, insertafter):
    """
    Insert the given children before or after the given xpath. If insertbefore is True, it is inserted before the
    first xpath hit, with insertafter, it is inserted after the last xpath hit.
    """
    insert_target = tree.xpath(xpath, namespaces=namespaces)
    loc_index = 0 if insertbefore else -1
    index_in_parent = insert_target[loc_index].getparent().index(insert_target[loc_index])
    parent = insert_target[0].getparent()
    if insertafter:
        index_in_parent += 1
    for child in children:
        parent.insert(index_in_parent, child)
        index_in_parent += 1

def _extract_xpstr(g):
    return g[1:-1]

def split_xpath_last(xpath):
    """split an XPath of the form /foo/bar/baz into /foo/bar and baz"""
    xpath = xpath.strip()
    m = _RE_SPLITSIMPLELAST.match(xpath)
    if m:
        return (m.group(1), [(m.group(2), None)])
    m = _RE_SPLITSIMPLELASTEQVALUE.match(xpath)
    if m:
        return (m.group(1), [(m.group(2), _extract_xpstr(m.group(3)))])
    m = _RE_SPLITSIMPLEATTRLAST.match(xpath)
    if m:
        return (m.group(1), [(m.group(2), None)])
    m = _RE_SPLITSIMPLEATTRLASTEQVALUE.match(xpath)
    if m:
        return (m.group(1), [(m.group(2), _extract_xpstr(m.group(3)))])
    m = _RE_SPLITSUBLAST.match(xpath)
    if m:
        content = [x.strip() for x in m.group(3).split(' and ')]
        return (m.group(1), [('/' + m.group(2), content)])
    m = _RE_SPLITONLYEQVALUE.match(xpath)
    if m:
        return (m.group(1), [('', _extract_xpstr(m.group(2)))])
    return (xpath, [])

def nsnameToClark(name, namespaces):
    if ':' in name:
        (nsname, rawname) = name.split(':')
        return '{{{0}}}{1}'.format(namespaces[nsname], rawname)
    return name

def check_or_make_target(module, tree, xpath, namespaces):
    (inner_xpath, changes) = split_xpath_last(xpath)
    if inner_xpath == xpath or changes is None:
        module.fail_json(msg="Can't process Xpath %s in order to spawn nodes! tree is %s" % (xpath, etree.tostring(tree, pretty_print=True)))
        return False
    changed = False
    if not is_node(tree, inner_xpath, namespaces):
        changed = check_or_make_target(module, tree, inner_xpath, namespaces)
    if is_node(tree, inner_xpath, namespaces) and changes:
        for (eoa, eoa_value) in changes:
            if eoa and eoa[0] != '@' and (eoa[0] != '/'):
                new_kids = children_to_nodes(module, [nsnameToClark(eoa, namespaces)], 'yaml')
                if eoa_value:
                    for nk in new_kids:
                        nk.text = eoa_value
                for node in tree.xpath(inner_xpath, namespaces=namespaces):
                    node.extend(new_kids)
                    changed = True
            elif eoa and eoa[0] == '/':
                element = eoa[1:]
                new_kids = children_to_nodes(module, [nsnameToClark(element, namespaces)], 'yaml')
                for node in tree.xpath(inner_xpath, namespaces=namespaces):
                    node.extend(new_kids)
                    for nk in new_kids:
                        for subexpr in eoa_value:
                            check_or_make_target(module, nk, './' + subexpr, namespaces)
                    changed = True
            elif eoa == '':
                for node in tree.xpath(inner_xpath, namespaces=namespaces):
                    if node.text != eoa_value:
                        node.text = eoa_value
                        changed = True
            elif eoa and eoa[0] == '@':
                attribute = nsnameToClark(eoa[1:], namespaces)
                for element in tree.xpath(inner_xpath, namespaces=namespaces):
                    changing = attribute not in element.attrib or element.attrib[attribute] != eoa_value
                    if changing:
                        changed = changed or changing
                        if eoa_value is None:
                            value = ''
                        else:
                            value = eoa_value
                        element.attrib[attribute] = value
            else:
                module.fail_json(msg='unknown tree transformation=%s' % etree.tostring(tree, pretty_print=True))
    return changed

def ensure_xpath_exists(module, tree, xpath, namespaces):
    changed = False
    if not is_node(tree, xpath, namespaces):
        changed = check_or_make_target(module, tree, xpath, namespaces)
    finish(module, tree, xpath, namespaces, changed)

def set_target_inner(module, tree, xpath, namespaces, attribute, value):
    changed = False
    try:
        if not is_node(tree, xpath, namespaces):
            changed = check_or_make_target(module, tree, xpath, namespaces)
    except Exception as e:
        missing_namespace = ''
        if tree.getroot().nsmap and ':' not in xpath:
            missing_namespace = 'XML document has namespace(s) defined, but no namespace prefix(es) used in xpath!\n'
        module.fail_json(msg='%sXpath %s causes a failure: %s\n  -- tree is %s' % (missing_namespace, xpath, e, etree.tostring(tree, pretty_print=True)), exception=traceback.format_exc())
    if not is_node(tree, xpath, namespaces):
        module.fail_json(msg='Xpath %s does not reference a node! tree is %s' % (xpath, etree.tostring(tree, pretty_print=True)))
    for element in tree.xpath(xpath, namespaces=namespaces):
        if not attribute:
            changed = changed or element.text != value
            if element.text != value:
                element.text = value
        else:
            changed = changed or element.get(attribute) != value
            if ':' in attribute:
                (attr_ns, attr_name) = attribute.split(':')
                attribute = '{{{0}}}{1}'.format(namespaces[attr_ns], attr_name)
            if element.get(attribute) != value:
                element.set(attribute, value)
    return changed

def set_target(module, tree, xpath, namespaces, attribute, value):
    changed = set_target_inner(module, tree, xpath, namespaces, attribute, value)
    finish(module, tree, xpath, namespaces, changed)

def get_element_text(module, tree, xpath, namespaces):
    if not is_node(tree, xpath, namespaces):
        module.fail_json(msg='Xpath %s does not reference a node!' % xpath)
    elements = []
    for element in tree.xpath(xpath, namespaces=namespaces):
        elements.append({element.tag: element.text})
    finish(module, tree, xpath, namespaces, changed=False, msg=len(elements), hitcount=len(elements), matches=elements)

def get_element_attr(module, tree, xpath, namespaces):
    if not is_node(tree, xpath, namespaces):
        module.fail_json(msg='Xpath %s does not reference a node!' % xpath)
    elements = []
    for element in tree.xpath(xpath, namespaces=namespaces):
        child = {}
        for key in element.keys():
            value = element.get(key)
            child.update({key: value})
        elements.append({element.tag: child})
    finish(module, tree, xpath, namespaces, changed=False, msg=len(elements), hitcount=len(elements), matches=elements)

def child_to_element(module, child, in_type):
    if in_type == 'xml':
        infile = BytesIO(to_bytes(child, errors='surrogate_or_strict'))
        try:
            parser = etree.XMLParser()
            node = etree.parse(infile, parser)
            return node.getroot()
        except etree.XMLSyntaxError as e:
            module.fail_json(msg='Error while parsing child element: %s' % e)
    elif in_type == 'yaml':
        if isinstance(child, string_types):
            return etree.Element(child)
        elif isinstance(child, MutableMapping):
            if len(child) > 1:
                module.fail_json(msg='Can only create children from hashes with one key')
            (key, value) = next(iteritems(child))
            if isinstance(value, MutableMapping):
                children = value.pop('_', None)
                node = etree.Element(key, value)
                if children is not None:
                    if not isinstance(children, list):
                        module.fail_json(msg='Invalid children type: %s, must be list.' % type(children))
                    subnodes = children_to_nodes(module, children)
                    node.extend(subnodes)
            else:
                node = etree.Element(key)
                node.text = value
            return node
        else:
            module.fail_json(msg='Invalid child type: %s. Children must be either strings or hashes.' % type(child))
    else:
        module.fail_json(msg='Invalid child input type: %s. Type must be either xml or yaml.' % in_type)

def children_to_nodes(module=None, children=None, type='yaml'):
    """turn a str/hash/list of str&hash into a list of elements"""
    children = [] if children is None else children
    return [child_to_element(module, child, type) for child in children]

def make_pretty(module, tree):
    xml_string = etree.tostring(tree, xml_declaration=True, encoding='UTF-8', pretty_print=module.params['pretty_print'])
    result = dict(changed=False)
    if module.params['path']:
        xml_file = module.params['path']
        with open(xml_file, 'rb') as xml_content:
            if xml_string != xml_content.read():
                result['changed'] = True
                if not module.check_mode:
                    if module.params['backup']:
                        result['backup_file'] = module.backup_local(module.params['path'])
                    tree.write(xml_file, xml_declaration=True, encoding='UTF-8', pretty_print=module.params['pretty_print'])
    elif module.params['xmlstring']:
        result['xmlstring'] = xml_string
        if xml_string != module.params['xmlstring']:
            result['changed'] = True
    module.exit_json(**result)

def finish(module, tree, xpath, namespaces, changed=False, msg='', hitcount=0, matches=tuple()):
    result = dict(actions=dict(xpath=xpath, namespaces=namespaces, state=module.params['state']), changed=has_changed(tree))
    if module.params['count'] or hitcount:
        result['count'] = hitcount
    if module.params['print_match'] or matches:
        result['matches'] = matches
    if msg:
        result['msg'] = msg
    if result['changed']:
        if module._diff:
            result['diff'] = dict(before=etree.tostring(orig_doc, xml_declaration=True, encoding='UTF-8', pretty_print=True), after=etree.tostring(tree, xml_declaration=True, encoding='UTF-8', pretty_print=True))
        if module.params['path'] and (not module.check_mode):
            if module.params['backup']:
                result['backup_file'] = module.backup_local(module.params['path'])
            tree.write(module.params['path'], xml_declaration=True, encoding='UTF-8', pretty_print=module.params['pretty_print'])
    if module.params['xmlstring']:
        result['xmlstring'] = etree.tostring(tree, xml_declaration=True, encoding='UTF-8', pretty_print=module.params['pretty_print'])
    module.exit_json(**result)

def main():
    module = AnsibleModule(argument_spec=dict(path=dict(type='path', aliases=['dest', 'file']), xmlstring=dict(type='str'), xpath=dict(type='str'), namespaces=dict(type='dict', default={}), state=dict(type='str', default='present', choices=['absent', 'present'], aliases=['ensure']), value=dict(type='raw'), attribute=dict(type='raw'), add_children=dict(type='list'), set_children=dict(type='list'), count=dict(type='bool', default=False), print_match=dict(type='bool', default=False), pretty_print=dict(type='bool', default=False), content=dict(type='str', choices=['attribute', 'text']), input_type=dict(type='str', default='yaml', choices=['xml', 'yaml']), backup=dict(type='bool', default=False), strip_cdata_tags=dict(type='bool', default=False), insertbefore=dict(type='bool', default=False), insertafter=dict(type='bool', default=False)), supports_check_mode=True, required_by=dict(add_children=['xpath'], content=['xpath'], set_children=['xpath'], value=['xpath']), required_if=[['count', True, ['xpath']], ['print_match', True, ['xpath']], ['insertbefore', True, ['xpath']], ['insertafter', True, ['xpath']]], required_one_of=[['path', 'xmlstring'], ['add_children', 'content', 'count', 'pretty_print', 'print_match', 'set_children', 'value']], mutually_exclusive=[['add_children', 'content', 'count', 'print_match', 'set_children', 'value'], ['path', 'xmlstring'], ['insertbefore', 'insertafter']])
    xml_file = module.params['path']
    xml_string = module.params['xmlstring']
    xpath = module.params['xpath']
    namespaces = module.params['namespaces']
    state = module.params['state']
    value = json_dict_bytes_to_unicode(module.params['value'])
    attribute = module.params['attribute']
    set_children = json_dict_bytes_to_unicode(module.params['set_children'])
    add_children = json_dict_bytes_to_unicode(module.params['add_children'])
    pretty_print = module.params['pretty_print']
    content = module.params['content']
    input_type = module.params['input_type']
    print_match = module.params['print_match']
    count = module.params['count']
    backup = module.params['backup']
    strip_cdata_tags = module.params['strip_cdata_tags']
    insertbefore = module.params['insertbefore']
    insertafter = module.params['insertafter']
    if not HAS_LXML:
        module.fail_json(msg=missing_required_lib('lxml'), exception=LXML_IMP_ERR)
    elif LooseVersion('.'.join((to_native(f) for f in etree.LXML_VERSION))) < LooseVersion('2.3.0'):
        module.fail_json(msg='The xml ansible module requires lxml 2.3.0 or newer installed on the managed machine')
    elif LooseVersion('.'.join((to_native(f) for f in etree.LXML_VERSION))) < LooseVersion('3.0.0'):
        module.warn('Using lxml version lower than 3.0.0 does not guarantee predictable element attribute order.')
    if content == 'attribute' and attribute is not None:
        module.deprecate("Parameter 'attribute=%s' is ignored when using 'content=attribute' only 'xpath' is used. Please remove entry." % attribute, '2.12', collection_name='ansible.builtin')
    if xml_string:
        infile = BytesIO(to_bytes(xml_string, errors='surrogate_or_strict'))
    elif os.path.isfile(xml_file):
        infile = open(xml_file, 'rb')
    else:
        module.fail_json(msg="The target XML source '%s' does not exist." % xml_file)
    if xpath is not None:
        try:
            etree.XPath(xpath)
        except etree.XPathSyntaxError as e:
            module.fail_json(msg='Syntax error in xpath expression: %s (%s)' % (xpath, e))
        except etree.XPathEvalError as e:
            module.fail_json(msg='Evaluation error in xpath expression: %s (%s)' % (xpath, e))
    try:
        parser = etree.XMLParser(remove_blank_text=pretty_print, strip_cdata=strip_cdata_tags)
        doc = etree.parse(infile, parser)
    except etree.XMLSyntaxError as e:
        module.fail_json(msg='Error while parsing document: %s (%s)' % (xml_file or 'xml_string', e))
    global orig_doc
    orig_doc = copy.deepcopy(doc)
    if print_match:
        do_print_match(module, doc, xpath, namespaces)
    if count:
        count_nodes(module, doc, xpath, namespaces)
    if content == 'attribute':
        get_element_attr(module, doc, xpath, namespaces)
    elif content == 'text':
        get_element_text(module, doc, xpath, namespaces)
    if state == 'absent':
        delete_xpath_target(module, doc, xpath, namespaces)
    if set_children:
        set_target_children(module, doc, xpath, namespaces, set_children, input_type)
    if add_children:
        add_target_children(module, doc, xpath, namespaces, add_children, input_type, insertbefore, insertafter)
    if value is not None:
        set_target(module, doc, xpath, namespaces, attribute, value)
    if xpath is not None:
        ensure_xpath_exists(module, doc, xpath, namespaces)
    if pretty_print:
        make_pretty(module, doc)
    module.fail_json(msg="Don't know what to do")
if __name__ == '__main__':
    main()