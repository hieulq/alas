import os
import sys
import click

from alas.cli import pass_context
from alas.utils import ssh_config


def _get_conf_obj(host, port, user, id_file):
    config = {}
    if host:
        config['hostname'] = host
    if port:
        config['port'] = port
    if user:
        config['user'] = user
    if id_file:
        config['identityfile'] = id_file
    return config


@click.command('ssh', short_help='Manage SSH host alias.')
@click.option('-c', '--config-file', type=click.Path(),
              default='~/.ssh/config',
              help='SSH config file to manage host aliases; default to '
                   '~/.ssh/config.')
@click.option('-i', '--id-file', type=click.Path(),
              help='Identity file used for perform authz in SSH session; '
                   'default is ~/.ssh/id_rsa key.')
@click.option('-h', '--host',
              help='Target host to SSH.')
@click.option('-p', '--port', default=22,
              help='Port for perform SSH in target host; default is 22.')
@click.option('-u', '--user',
              help='Username for authz with target host.')
@click.option('-a', '--alias', type=click.STRING,
              help='Alias name to add/update/remove or view.')
@click.argument('action', type=click.Choice(['add', 'update', 'rm', 'list',
                                             'view']))
@pass_context
def cli(ctx, action, alias, user, port, host, id_file, config_file):
    if not os.path.exists(os.path.expanduser(config_file)):
        ctx.log('Config file not existed!\n')
        sys.exit(1)
    else:
        config = ssh_config.SSHConfig(os.path.expanduser(config_file))
        conf = _get_conf_obj(host, port, user, id_file)
    if alias:
        curr_config = config.lookup(alias)
    else:
        curr_config = None
    if action == 'add':
        if curr_config:
            ctx.log('Alias already exists or missing alias name!\n')
            sys.exit(1)
        config.write(alias, conf)
        ctx.log('Done!')
    elif action == 'update':
        if not curr_config:
            ctx.log('Alias does not exist or missing alias name!\n')
            sys.exit(2)
        config.write(alias, conf)
        ctx.log('Done!')
    elif action == 'rm':
        if not curr_config:
            ctx.log('Alias does not exist or missing alias name!\n')
            sys.exit(3)
        config.delete(alias)
        ctx.log('Done!')
    elif action == 'list':
        ctx.log(str(config))
    elif action == 'view':
        if curr_config:
            ctx.log("alias: {0}".format(alias))
            for k, v in curr_config.items():
                ctx.log("  {0}: {1}".format(k, v))
