from typing import Type

from .itest import ITest

from .chat_ai_test import ChatAI_Test
from .pubsub_test import PubSub_Test


class TestRunner():
    def __init__(self):
        tests_list: list[ITest] = [
            ChatAI_Test,
            PubSub_Test,
        ]
        self.tests: dict[str, Type[ITest]] = {}
        for test in tests_list:
            self.tests[test.name] = test

    def _run_test(self, test_class: Type[ITest]):
        print(f'running test: {test_class.name}')
        test_class().run()

    def _name_to_test_class(self, name: str):
        name_lower = name.lower()
        for test_name in self.tests:
            if name_lower == test_name.lower():
                return self.tests[test_name]
        return None

    def print_info(self):
        print('list of existing tests:')
        for idx, test_name in enumerate(self.tests, start=1):
            print(f'{idx}. {test_name}')

    def run(self, names: list[str]):
        for name in names:
            test = self._name_to_test_class(name)
            if not test:
                print(f'no such test exists [{name}]')
                self.print_info()
                return
            self._run_test(test)
