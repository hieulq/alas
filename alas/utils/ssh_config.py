import os


# NOTE(hieulq): kudos to mpatek ssh alias script.
class SSHConfig(object):

    def __init__(self, config_file=None):
        self.conf = None
        if config_file:
            self.parse(config_file)
            self.conf_file = config_file
        else:
            self.conf_file = None

    def parse(self, config_file):
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
        self.conf = host_configs

    def lookup(self, host):
        """
        Returns list of host configurations.
        """
        if host in self.conf:
            return self.conf[host]
        return None

    def _fetch_other_lines(self, host):
        """ Get lines not associated with specified host. """
        in_host_config = False
        lines = []
        for line in open(self.conf_file):
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

    def write(self, host, conf):
        """
        Adds/updates host configuration.
        """
        lines = self._fetch_other_lines(host)
        if lines:
            last_line = lines[-1].strip()
            if last_line:
                lines.append("\n")  # separator
        lines.append("host {0}\n".format(host))
        for k, v in conf.items():
            lines.append(" {0} {1}\n".format(k, v))
        with open(self.conf_file, 'w') as ofh:
            for line in lines:
                ofh.write(line)

    def delete(self, host):
        """
        Removes host configuration.
        """
        lines = self._fetch_other_lines(host)
        with open(self.conf_file, 'w') as ofh:
            for line in lines:
                ofh.write(line)

    def __str__(self):
        res = ''
        for alias, config in self.conf.items():
            res += "{0}\t{1}@{2}\n".format(
                alias,
                config['user'] if 'user' in config else '<user>',
                config['hostname'] if 'hostname' in config else alias,
            )
        return res

