import pytest
pytest
from bokeh._testing.util.selenium import RECORD
from bokeh.models import CustomAction, CustomJS
from bokeh.plotting import figure
pytest_plugins = ('bokeh._testing.plugins.project',)

def Test_CustomAction_test_tap_triggers_callback(self, single_plot_page) -> None:
    plot = figure(height=800, width=1000, tools='')
    plot.rect(x=[1, 2], y=[1, 1], width=1, height=1)
    plot.add_tools(CustomAction(callback=CustomJS(code=RECORD('activated', 'true'))))
    page = single_plot_page(plot)
    page.click_custom_action()
    assert page.results['activated'] == True
    assert page.has_no_console_errors()