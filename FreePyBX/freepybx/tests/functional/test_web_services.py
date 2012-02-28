from freepybx.tests import *

class TestWebServicesController(TestController):

    def test_index(self):
        response = self.app.get(url(controller='web_services', action='index'))
        # Test response...
