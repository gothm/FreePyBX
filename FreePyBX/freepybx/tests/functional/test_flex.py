from freepybx.tests import *

class TestFlexController(TestController):

    def test_index(self):
        response = self.app.get(url(controller='flex', action='index'))
        # Test response...
