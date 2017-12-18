from setuptools import setup

setup(
    name='alas',
    version='1.0.0',
    description='All Linux aliases and auto-completion manager.',
    author='Hieu LE',
    author_email='sudo@rm-rf.cloud',
    license='Apache-2.0',
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
