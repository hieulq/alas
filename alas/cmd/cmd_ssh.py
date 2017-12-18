import os
import sys
import click

from alas.cli import pass_context


# NOTE(hieulq): kudos to mpatek ssh alias script.
def _read_host_configs(config_file):
    """ Reads all host configurations from specified file.

    Returns dict from aliases to configuration details.
    """
    host_configs = {}
    in_host_config = False
    curr_config = None
    curr_alias = None
    for line in open(config_file):
        tokens = line.strip().split()
        if tokens:
            first_token = tokens[0].lower()
            if not in_host_config:
                if first_token == 'host':
                    in_host_config = True
                    curr_config = {}
                    curr_alias = tokens[1]
            else:
                curr_config[first_token] = ' '.join(tokens[1:])
        elif in_host_config:
            in_host_config = False
            if curr_config and curr_alias:
                host_configs[curr_alias] = curr_config
                curr_config = None
                curr_alias = None
    if in_host_config and curr_config and curr_alias:
        host_configs[curr_alias] = curr_config
        curr_config = None
        curr_alias = None
    return host_configs


def _read_host_config(host, config_file):
    """
    Returns list of host configurations.
    """
    configs = _read_host_configs(config_file)
    if host in configs:
        return configs[host]
    return None


def _fetch_other_lines(host, config_file):
    """ Get lines not associated with specified host. """
    in_host_config = False
    lines = []
    for line in open(config_file):
        tokens = line.strip().split()
        if tokens:
            first_token = tokens[0].lower()
            if not in_host_config:
                if first_token == 'host' and tokens[1] == host:
                    in_host_config = True
        if not tokens and in_host_config:
            in_host_config = False
        elif not in_host_config:
            lines.append(line)
    return lines


def _write_host_config(host, config, config_file):
    """
    Adds/updates host configuration.
    """
    lines = _fetch_other_lines(host, config_file)
    if lines:
        last_line = lines[-1].strip()
        if last_line:
            lines.append("\n")  # separator
    lines.append("host {0}\n".format(host))
    for k, v in config.items():
        lines.append(" {0} {1}\n".format(k, v))
    with open(config_file, 'w') as ofh:
        for line in lines:
            ofh.write(line)


def _delete_host_config(host, config_file):
    """
    Removes host configuration.
    """
    lines = _fetch_other_lines(host, config_file)
    with open(config_file, 'w') as ofh:
        for line in lines:
            ofh.write(line)


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
    config_file = os.path.expanduser(config_file)
    conf = _get_conf_obj(host, port, user, id_file)
    if not os.path.exists(config_file):
        open(config_file, 'w').close()
    if alias:
        curr_config = _read_host_config(alias, config_file)
    else:
        curr_config = None
    if action == 'add':
        if curr_config:
            ctx.log('Alias already exists or missing alias name!\n')
            sys.exit(1)
        _write_host_config(alias, conf, config_file)
        ctx.log('Done!')
    elif action == 'update':
        if not curr_config:
            ctx.log('Alias does not exist or missing alias name!\n')
            sys.exit(2)
        _write_host_config(alias, conf, config_file)
        ctx.log('Done!')
    elif action == 'rm':
        if not curr_config:
            ctx.log('Alias does not exist or missing alias name!\n')
            sys.exit(3)
        _delete_host_config(alias, config_file)
        ctx.log('Done!')
    elif action == 'list':
        for alias, config in _read_host_configs(config_file).items():
            ctx.log("{0}\t{1}@{2}".format(
                alias,
                config['user'] if 'user' in config else '<user>',
                config['hostname'] if 'hostname' in config else alias,
            ))
    elif action == 'view':
        if curr_config:
            ctx.log("alias: {0}".format(alias))
            for k, v in curr_config.items():
                ctx.log("  {0}: {1}".format(k, v))
