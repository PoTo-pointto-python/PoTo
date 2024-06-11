from anaconda.anaconda import plugin_loaded
from anaconda.anaconda import plugin_unloaded
from anaconda.anaconda import monitor_plugins
from anaconda.anaconda import enable_plugins

def test_PT_plugin_loaded():
    plugin_loaded()
    
def test_PT_plugin_unloaded():
    plugin_unloaded()
    
def test_PT_monitor_plugins():
    monitor_plugins()
    
def test_PT_enable_plugins():
    enable_plugins()