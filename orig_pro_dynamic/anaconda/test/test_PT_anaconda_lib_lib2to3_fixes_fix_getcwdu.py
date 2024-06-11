from anaconda.anaconda_lib.autopep.autopep8_lib.lib2to3.fixes.fix_getcwdu import FixGetcwdu

def test_PT_FixGetcwdu_transform():
    f = FixGetcwdu()
    f.transform()
