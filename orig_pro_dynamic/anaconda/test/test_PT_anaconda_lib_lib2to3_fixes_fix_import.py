from anaconda.anaconda_lib.autopep.autopep8_lib.lib2to3.fixes.fix_import import FixImport
from anaconda.anaconda_lib.autopep.autopep8_lib.lib2to3.fixes.fix_import import traverse_imports

def test_PT_traverse_imports():
    traverse_imports("testnames")

def test_PT_FixImport_start_tree():
    f = FixImport()
    f.start_tree()

def test_PT_FixImport_transform():
    f = FixImport()
    f.transform()

def test_PT_FixImport_probably_a_local_import():
    f = FixImport()
    f.probably_a_local_import()
