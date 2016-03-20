from .base import BaseTestCase

from accounting.utils import remove_extra_spaces


class RemoveExtraSpaceTest(BaseTestCase):
    def test_strips_space_chars(self):
        self.assertEqual(
            remove_extra_spaces(' test test   '),
            'test test'
        )

        self.assertEqual(
            remove_extra_spaces(' test test'),
            'test test'
        )

    def test_removes_space_char_from_middle_of_string(self):
        self.assertEqual(
            remove_extra_spaces('test   test  test'),
            'test test test'
        )
