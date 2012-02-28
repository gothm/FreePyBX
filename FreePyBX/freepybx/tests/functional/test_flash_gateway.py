from freepybx.tests import *

class TestFlashGatewayController(TestController):

    def test_index(self):
        response = self.app.get(url(controller='flash_gateway', action='index'))
        # Test response...
