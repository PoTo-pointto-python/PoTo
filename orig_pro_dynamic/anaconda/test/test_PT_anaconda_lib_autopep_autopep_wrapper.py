from anaconda.anaconda_lib.autopep.autopep_wrapper import AnacondaAutopep8

def test_PT_AnacondaAutopep8_run():
    a = AnacondaAutopep8()
    a.run()

def test_PT_AnacondaAutopep8_parse_settings():
    a = AnacondaAutopep8()
    a.parse_settings()