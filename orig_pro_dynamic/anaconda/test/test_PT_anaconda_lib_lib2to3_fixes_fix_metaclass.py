from anaconda.anaconda_lib.autopep.autopep8_lib.lib2to3.fixes.fix_metaclass import FixMetaclass
from anaconda.anaconda_lib.autopep.autopep8_lib.lib2to3.fixes.fix_metaclass import has_metaclass
from anaconda.anaconda_lib.autopep.autopep8_lib.lib2to3.fixes.fix_metaclass import fixup_parse_tree
from anaconda.anaconda_lib.autopep.autopep8_lib.lib2to3.fixes.fix_metaclass import fixup_simple_stmt
from anaconda.anaconda_lib.autopep.autopep8_lib.lib2to3.fixes.fix_metaclass import remove_trailing_newline
from anaconda.anaconda_lib.autopep.autopep8_lib.lib2to3.fixes.fix_metaclass import find_metas
from anaconda.anaconda_lib.autopep.autopep8_lib.lib2to3.fixes.fix_metaclass import fixup_indent

def test_PT_has_metaclass():
    has_metaclass()

def test_PT_fixup_parse_tree():
    fixup_parse_tree()

def test_PT_fixup_simple_stmt():
    fixup_simple_stmt()

def test_PT_remove_trailing_newline():
    remove_trailing_newline()

def test_PT_find_metas():
    find_metas()

def test_PT_fixup_indent():
    fixup_indent()

def test_PT_FixMetaclass_transform():
    f = FixMetaclass()
    f.transform()