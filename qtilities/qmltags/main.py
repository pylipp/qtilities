#! /usr/bin/env python3

"""Utility script to generate basic ctags for custom QML components.
Currently only generates 'class' ctags.

Usage:
Run in the top level of QML code to generate a 'tags' file. By default, all
files with '.qml' suffix are evaluated:
    qmltags
Pass an arbitrary number of QML files to generate tags on base of these:
    qmltags MyComponent.qml buttons/MyButton.qml
    qmltags screens/*.qml
"""


import argparse
import os.path
import sys
import glob

# ClassName file    /^Pattern   c
# variable  file    /^Pattern   v   class:ClassName



class Tag:
    """Base class representing a ctags Tag."""
    def __init__(self, name, file, pattern, kind):
        self.name = name
        self.file = file
        self.pattern = pattern
        self.kind = kind

    def __str__(self):
        """Tab-separated textual representation of the tag."""
        return "\t".join([self.name, self.file, self.pattern, self.kind])


class ClassTag(Tag):
    def __init__(self, name, file, pattern):
        super().__init__(name, file, pattern, "c")


class ClassChildTag(Tag):
    def __init__(self, name, file, pattern, parent, kind):
        super().__init__(name, file, pattern, kind)
        self.parent = "class:" + parent

    def __str__(self):
        return super().__str__() + "\t" + self.parent


class VariableTag(ClassChildTag):
    def __init__(self, name, file, pattern, parent):
        super().__init__(name, file, pattern, parent, "v")


def generate_class_tag(filepath):
    """Generate class tag from given component file.
    Raises SystemExit if no main component found."""
    # remove .ui.qml or .qml suffix
    name = os.path.basename(filepath).split(".")[0]

    # the line defining the main component is used as target point
    pattern = None
    with open(filepath) as source:
        for line in source:
            if "{" in line:
                pattern = "/^{}$/;\"".format(line.strip())
                break

    if pattern is None:
        raise SystemExit("No main component found in {}".format(filepath))

    return ClassTag(name, filepath, pattern)


def generate_variable_tags(filepath):
    """Generate variable tags from given filepath. Work in progress."""
    parent, _ = os.path.splitext(os.path.basename(filepath))
    variables = []
    with open(filepath) as source:
        for line in source:
            if line.startswith("    "):
                try:
                    name, _ = line.split(":")
                except ValueError:
                    continue
                pattern = "/^{}$/;\"".format(line.strip("\n"))
                tag = VariableTag(name.strip(), filepath, pattern, parent)
                variables.append(tag)
    return [str(v) for v in variables]


def generate_all_tags(*, filepaths, output_filepath):
    """Generate all tags from an arbitrary number of filepaths and write them to
    the given output filepath (silently overwritten if already existing).
    """
    tags = [str(generate_class_tag(f)) for f in filepaths if f.endswith(".qml")]

    # for f in filepaths:
    #     tags.extend(generate_variable_tags(f))

    print("Writing {} tags to '{}'...".format(len(tags), output_filepath))
    with open(output_filepath, "w") as tag_file:
        tag_file.write("\n".join(tags))


def _parse_cli():
    parser = argparse.ArgumentParser(
        description=globals()["__doc__"],
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "filepaths", metavar="FILEPATH", nargs="*",
        help="QML file path(s) to generate tags from",
    )
    parser.add_argument(
        "-o", "--output-filepath", default="qmltags",
        help="Path of output tags file (default: 'tags' in current directory)",
    )
    return parser.parse_args()


def main():
    options = _parse_cli()
    filepaths = options.filepaths
    if not filepaths:
        filepaths = glob.glob("**/*.qml", recursive=True)
    generate_all_tags(
        filepaths=filepaths, output_filepath=options.output_filepath,
    )
