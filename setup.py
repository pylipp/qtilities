from setuptools import setup, find_packages

with open("README.md") as readme:
    long_description = readme.read()

setup(
    name='qtilities',
    use_scm_version=True,
    setup_requires=["setuptools_scm"],
    description='Utilities for PyQt5 development',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/pylipp/qtilities',
    author='Philipp Metzner',
    author_email='beth.aleph@yahoo.de',
    license='GPLv3',
    # classifiers=[],
    packages=find_packages(exclude=['test', 'doc']),
    entry_points={
        'console_scripts': [
            'pqp = qtilities.pqp.previewer:main',
            'pqpc = qtilities.pqp.client:main',
            'qmltags = qtilities.qmltags.main:main',
            'pyqmlscene = qtilities.pyqmlscene.main:main',
        ]
    },
    install_requires=[
        "PyQt5",
    ],
    extras_require={
        "packaging": [
            "twine>=1.11.0",
            "setuptools>=38.6.0",
            "wheel>=0.31.0",
        ],
    },
)
