from anaconda.anaconda_lib.autopep.autopep8_lib.lib2to3.fixes.fix_isinstance import FixIsinstance

def test_PT_FixIsinstance_transform():
    f = FixIsinstance()
    f.transform()