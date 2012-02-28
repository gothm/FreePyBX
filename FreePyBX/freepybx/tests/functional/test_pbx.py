from freepybx.tests import *

class TestPbxController(TestController):

    def test_index(self):
        response = self.app.get(url(controller='pbx', action='index'))
        # Test response...
