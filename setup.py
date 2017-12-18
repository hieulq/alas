from setuptools import setup

setup(
    name='alas',
    version='1.0',
    author='Hieu LE',
    author_email='sudo@rm-rf.cloud',
    url='https://github.com/hieulq/alas',
    packages=['alas', 'alas.cmd', 'alas.utils'],
    include_package_data=True,
    install_requires=[
        'click',
        'prettytable'
    ],
    entry_points='''
        [console_scripts]
        alas=alas.cli:cli
    ''',
)
