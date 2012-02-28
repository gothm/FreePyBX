from freepybx.tests import *

class TestCrmController(TestController):

    def test_index(self):
        response = self.app.get(url(controller='crm', action='index'))
        # Test response...
