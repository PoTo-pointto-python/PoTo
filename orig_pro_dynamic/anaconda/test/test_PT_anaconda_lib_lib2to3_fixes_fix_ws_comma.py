from anaconda.anaconda_lib.autopep.autopep8_lib.lib2to3.fixes.fix_ws_comma import FixWsComma

def test_PT_FixWsComma_transform():
    f = FixWsComma()
    f.transform()
