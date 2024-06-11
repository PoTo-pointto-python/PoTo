from anaconda.anaconda_lib.autopep.autopep8_lib.lib2to3.fixes.fix_imports import alternates
from anaconda.anaconda_lib.autopep.autopep8_lib.lib2to3.fixes.fix_imports import build_pattern
from anaconda.anaconda_lib.autopep.autopep8_lib.lib2to3.fixes.fix_imports import FixImports

def test_PT_alternates():
    alternates()

def test_PT_build_pattern():
    build_pattern()

def test_PT_FixImports_build_pattern():
    f = FixImports()
    f.build_pattern()

def test_PT_FixImports_compile_pattern():
    f = FixImports()
    f.compile_pattern()

def test_PT_FixImports_():
    f = FixImports()
    f.xxx()

def test_PT_FixImports_match():
    f = FixImports()
    f.match()

def test_PT_FixImports_start_tree():
    f = FixImports()
    f.start_tree()

def test_PT_FixImports_transform():
    f = FixImports()
    f.transform()