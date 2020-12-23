import unittest
import os.path
import tempfile

from qtilities.qmltags import main as qmltags


class QmltagsTestCase(unittest.TestCase):

    def test_generating_qmltags_file(self):
        output_filepath = tempfile.mkstemp()[1]
        qmltags.generate_all_tags(
            # Path resolution works because test is invoked from root directory
            filepaths=[os.path.join("test", "TheWindow.qml")],
            output_filepath=output_filepath,
        )

        with open(output_filepath) as f:
            actual_content = f.read()

        excepted_content = \
            'TheWindow\ttest/TheWindow.qml\t/^ApplicationWindow {$/;"\tc'
        self.assertEqual(actual_content, excepted_content)

        os.unlink(output_filepath)


if __name__ == "__main__":
    unittest.main()
