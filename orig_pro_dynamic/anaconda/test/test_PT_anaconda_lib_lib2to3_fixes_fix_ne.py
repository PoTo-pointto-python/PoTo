from anaconda.anaconda_lib.autopep.autopep8_lib.lib2to3.fixes.fix_ne import FixNe

def test_PT_FixNe_match():
    f = FixNe()
    f.match()

def test_PT_FixNe_transform():
    f = FixNe()
    f.transform()