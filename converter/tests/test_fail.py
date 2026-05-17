from django.test import TestCase

class DemoFailTest(TestCase):
    def test_demo_fail(self):
        self.assertEqual(1, 2)
