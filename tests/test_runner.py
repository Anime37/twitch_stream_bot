from .chat_ai_test import ChatAI_Test
from .itest import ITest


class TestRunner():
    tests: list[ITest] = [
        ChatAI_Test
    ]

    def run(self):
        for test in self.tests:
            test_obj = test()
            print(f'running test: {test_obj.name}')
            test_obj.run()
