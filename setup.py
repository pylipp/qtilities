from setuptools import setup, find_packages
from qtilities import __version__

with open("README.md") as readme:
    long_description = readme.read()

setup(
    name='qtilities',
    version=__version__,
    description='Utilities for PyQt5 development',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/pylipp/qtilities',
    author='Philipp Metzner',
    author_email='beth.aleph@yahoo.de',
    license='GPLv3',
    # classifiers=[],
    packages=find_packages(exclude=['test', 'doc']),
    scripts=["bin/qmltags"],
    entry_points={
        'console_scripts': [
            'pqp = qtilities.pqp.previewer:main',
            'pqpc = qtilities.pqp.client:main',
        ]
    },
    install_requires=[
        "PyQt5",
    ]
)
