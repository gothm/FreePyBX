from freepybx.tests import *

class TestRootController(TestController):

    def test_index(self):
        response = self.app.get(url(controller='root', action='index'))
        # Test response...
