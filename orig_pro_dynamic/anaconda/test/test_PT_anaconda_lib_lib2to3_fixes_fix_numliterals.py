from anaconda.anaconda_lib.autopep.autopep8_lib.lib2to3.fixes.fix_numliterals import FixNumliterals

def test_PT_FixNumliterals_match():
    f = FixNumliterals()
    f.match()

def test_PT_FixNumliterals_transform():
    f = FixNumliterals()
    f.transform()