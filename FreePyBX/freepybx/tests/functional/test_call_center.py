from freepybx.tests import *

class TestCallCenterController(TestController):

    def test_index(self):
        response = self.app.get(url(controller='call_center', action='index'))
        # Test response...
