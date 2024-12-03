import unittest
from typing import List, Dict
from auto_code_review.utils import Util 

class TestUtilMethods(unittest.TestCase):

    def test_numerate_lines(self):
        code = """def foo():
  
    print("Hello")
    return 42

"""
        expected_output = """def foo():  ##1
    ##2
    print("Hello")  ##3
    return 42  ##4
  ##5
"""
        result = Util.numerate_lines(code)
        print("result:",result)
        self.assertEqual(result, expected_output)

    def test_parse_response(self):
        input_data = """123 : This is line 1
456 : This is line 2"""
        expected_output = [{"line": 123, "comment": "123 : This is line 1"},
                           {"line": 456, "comment": "456 : This is line 2"}]
        result = Util.parse_response(input_data)
        self.assertEqual(result, expected_output)

        result_empty = Util.parse_response("")
        self.assertEqual(result_empty, [])

        result_none = Util.parse_response(None)
        self.assertEqual(result_none, [])

    def test_parse_diffs(self):
        diff_data = """@@ -1,3 +1,3 @@
- line 1
+ new line 1
- line 2
+ new line 2"""
        expected_output = [(1, 3)]
        result = Util.parse_diffs(diff_data)
        self.assertEqual(result, expected_output)

        diff_data_invalid = """@@ -1,3 +1,3 @@
- line 1"""
        result_invalid = Util.parse_diffs(diff_data_invalid)
        self.assertEqual(result_invalid, [(1,3)])

    def test_check_availability_to_post_comment(self):
        intervals = [(1, 3), (5, 8)]
        self.assertTrue(Util.check_availability_to_post_comment(2, intervals))
        self.assertTrue(Util.check_availability_to_post_comment(5, intervals))
        self.assertFalse(Util.check_availability_to_post_comment(4, intervals))
        self.assertFalse(Util.check_availability_to_post_comment(9, intervals))

if __name__ == "__main__":
    unittest.main()
