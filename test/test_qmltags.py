import unittest
import os.path
import tempfile

from qtilities.qmltags import main as qmltags


EXPECTED_CONTENT = """\
TheWindow\ttest/TheWindow.qml\t/^ApplicationWindow {$/;"\tc
doNothing\ttest/TheWindow.qml\t/^    function doNothing() {}$/;"\tm\tclass:TheWindow
doLess\ttest/TheWindow.qml\t/^    function doLess(argument) {}$/;"\tm\tclass:TheWindow
nested\ttest/TheWindow.qml\t/^        function nested() {}$/;"\tm\tclass:TheWindow
rectColor\ttest/TheWindow.qml\t/^    property alias rectColor: rectangle.color$/;"\tv\tclass:TheWindow
userLogin\ttest/TheWindow.qml\t/^    property bool userLogin$/;"\tv\tclass:TheWindow
count\ttest/TheWindow.qml\t/^        property int count: 5$/;"\tv\tclass:TheWindow
""".splitlines()


class QmltagsTestCase(unittest.TestCase):

    def test_generating_qmltags_file(self):
        output_filepath = tempfile.mkstemp()[1]
        qmltags.generate_all_tags(
            # Path resolution works because test is invoked from root directory
            filepaths=[os.path.join("test", "TheWindow.qml")],
            output_filepath=output_filepath,
        )

        with open(output_filepath) as f:
            actual_content = f.readlines()
            actual_content = [l.rstrip('\n') for l in actual_content]
        self.assertEqual(actual_content, EXPECTED_CONTENT)

        os.unlink(output_filepath)


if __name__ == "__main__":
    unittest.main()
