from setuptools import setup

setup(
    name='alas',
    version='1.0',
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
