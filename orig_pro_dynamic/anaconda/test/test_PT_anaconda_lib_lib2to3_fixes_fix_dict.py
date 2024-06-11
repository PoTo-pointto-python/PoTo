from anaconda.anaconda_lib.autopep.autopep8_lib.lib2to3.fixes.fix_dict import FixDict

def test_PT_FixDict_transform():
    f = FixDict()
    f.transform()
