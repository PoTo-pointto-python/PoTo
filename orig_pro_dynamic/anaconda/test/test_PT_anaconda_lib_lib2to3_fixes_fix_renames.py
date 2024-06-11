from anaconda.anaconda_lib.autopep.autopep8_lib.lib2to3.fixes.fix_renames import FixRenames
from anaconda.anaconda_lib.autopep.autopep8_lib.lib2to3.fixes.fix_renames import alternates
from anaconda.anaconda_lib.autopep.autopep8_lib.lib2to3.fixes.fix_renames import build_pattern

def test_PT_alternates():
    alternates()

def test_PT_build_pattern():
    build_pattern()

def test_PT_FixRenames_match():
    f = FixRenames()
    f.match()

def test_PT_FixRenames_transform():
    f = FixRenames()
    f.transform()
