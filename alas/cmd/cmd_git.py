import click
import os
import sys
from git import GitConfigParser

from alas.cli import pass_context

from pyparsing import (
    OneOrMore, restOfLine, Group, ZeroOrMore,
    CharsNotIn, Suppress, Word, alphanums, Literal, pythonStyleComment)


def build_parser():
    key = Word(alphanums).setResultsName('key')
    value = restOfLine.setParseAction(
        lambda string, location, tokens: tokens[0].strip()
    ).setResultsName('value')
    property_ = Group(key + Suppress(Literal('=')) + value)
    properties = Group(OneOrMore(property_)).setResultsName('properties')
    section_name = (Suppress('[') + OneOrMore(CharsNotIn(']')) +
                    Suppress(']')).setResultsName('section')
    section = Group(section_name + properties)
    ini_file = ZeroOrMore(section).setResultsName('sections')
    ini_file.ignore(pythonStyleComment)
    return ini_file


def parse_file(file_):
    parser = build_parser()
    return parser.parseWithTabs().parseFile(file_, parseAll=True)


@click.command('git', short_help='Manage Git alias.')
@click.option('-c', '--config-file', type=click.File(),
              default='~/.gitconfig',
              help='SSH config file to manage host aliases; default to '
                   '~/.ssh/config.')
@click.argument('action', type=click.Choice(['add', 'update', 'rm', 'list',
                                             'view']))
@pass_context
def cli(ctx, action, config_file):
    globalconfig = GitConfigParser(
        [os.path.expanduser(config_file)], read_only=True)
    ini_file_list = parse_file(os.path.expanduser(config_file)).asList()
    ctx.log(action)

