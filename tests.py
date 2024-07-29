import unittest
from main import Actions


class TestStringMethods(unittest.TestCase):
    def test_championships(self):
        actions = Actions()
        championships_response_example = [
            {'CL': None,'CLI': '','EC': 2,'EGN': 'FIFA.Volta','Fid': 562890,'Id': 77777777,'N': 'FIFA.Volta','SID': 0},
            {'CL': None,'CLI': '','EC': 84,'EGN': 'Europe','Fid': 113,'Id': 88888888,'N': 'Европа','SID': 0}
        ]
        self.assertEqual('foo'.upper(), 'FOO')

    def test_isupper(self):
        self.assertTrue('FOO'.isupper())
        self.assertFalse('Foo'.isupper())

    def test_split(self):
        s = 'hello world'
        self.assertEqual(s.split(), ['hello', 'world'])
        # Проверим, что s.split не работает, если разделитель - не строка
        with self.assertRaises(TypeError):
            s.split(2)


if __name__ == '__main__':
    unittest.main()
