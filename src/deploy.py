import json
import os

from git import Repo, InvalidGitRepositoryError

from utilities import get_string, valid_address, valid_config

from terminal import Terminal

from server import Server, ServerError


class DeployError(Exception):
    """ Base exception class for Deploy program.  """

    def __init__(self, message, base=None):
        super(DeployError, self).__init__(message)
        self.base_exception = base


class Deploy(object):
    def __init__(self, command):
        self.cmd = command
        self.commands = {
            'init': self._cmd_init,
            'now': self._cmd_now,
        }
        self.presets = {
            'java:gradle': '',
            'java:maven': '',
            'js:node': ''
        }

    def _cmd_init(self):
        """ Interactively creates a config file

        Raises:
            DeployError: if it is impossible to write the config to disc.

        """
        # Local info
        #   Project name, default to current dir
        directory = os.path.basename(os.getcwd())
        project = get_string(
            'Enter the project\'s name.',
            default=directory,
            validate=lambda x: x is not '',
            error_msg='The project field cannot be empty.\n')

        #   Preset, must choose from available presets
        presets_list = reduce(lambda x, y: x + '\n\t- ' + y, self.presets)
        preset = get_string(
            'Select the apropriate preset.',
            validate=lambda x: x in self.presets,
            error_msg='The selected preset does not exist. Please refer to this list:\n\t- ' + presets_list)

        #   Source dir
        source_dir = get_string(
            'Enter the source directory relative path. (Optional)',
            validate=lambda x: x is '' or os.path.exists(os.getcwd() + '/' + x),
            error_msg='The selected directory does not exist')

        #   Build dir
        build_dir = get_string(
            'Enter the build directory containing the binaries relative path. (Optional)',
            validate=lambda x: x is '' or os.path.exists(os.getcwd() + '/' + x),
            error_msg='The selected directory does not exist')

        # Remote
        #   Server address
        srv_address = get_string(
            'Enter the remote server address.',
            validate=valid_address,
            error_msg='The address must be a valid IP or hostname.')

        #   Server user
        srv_user = get_string(
            'Enter the remote server user.',
            validate=lambda x: x is not '',
            error_msg='The user field cannot be empty.')

        # Test SSH connection
        valid, err = Server(srv_address, srv_user).has_valid_connection()
        if not valid:
            Terminal.print_warn('Could not validate SSH connection.\n\t> %s' % err)

        # Write .deploy file
        config = {
            'server': {
                'address': srv_address,
                'user': srv_user
            },
            'project': {
                'name': project,
                'preset': preset,
                'directories': {
                    'source': source_dir,
                    'build': build_dir
                }
            },
            'scripts': {
                'before': [],
                'after': []
            }
        }

        try:
            with open('.deploy', 'w+') as file_handle:
                json.dump(config, file_handle, sort_keys=True, indent=4, separators=(',', ': '))
        except IOError, e:
            raise DeployError('Could not write config file to disk. > %s' % e, base=e)

    def _read_config(self):
        """ Read the configuration file and parses it.
            It then assigns the config to the current Deploy instance.

        Raises:
            DeployError: if the config is missing or invalid.

        """
        try:
            with open('.deploy', 'r') as file_handle:
                config_json = file_handle.read()
                if valid_config(config_json):
                    self.config = json.loads(config_json)
                else:
                    raise DeployError('Invalid configuration file, please refer to previous errors.')
        except IOError, e:
            raise DeployError('Config file not found nor present.\n\t> %s' % e, base=e)
        except ValueError, e:
            raise DeployError('Invalid configuration file, could not parse JSON.\n\t> %s' % e, base=e)

    def _read_repository(self):
        """ Tries to load the git repository located at current working directory.
            It then assigns the repository to the current Deploy instance.

        Raises:
            DeployError: if there is no git repository.

        """
        try:
            self.repository = Repo(os.getcwd())
        except InvalidGitRepositoryError, e:
            raise DeployError('No git repository was found.\n\t> %s' % e, base=e)

    def _cmd_now(self):
        """ Tries to synchronize the project state with the remote server, then reloads the app remotely.

        Raises:
            DeployError: If any of the assertion steps fails.

        """
        # Initial asserts

        #   [x] Config file is valid.
        self._read_config()

        #   [x] Is called from root of a git repo.
        self._read_repository()

        #   [x] SSH connection is working.
        address = self.config['server']['address']
        user = self.config['server']['user']
        server = Server(address, user)
        valid, err = server.has_valid_connection()
        if not valid:
            raise DeployError('Impossible to connect to remote host.\n\t> %s' % err, base=err)

        # [x] Server has supervisor and git installed.
        try:
            server.validate_dep_list_installed(['supervisor', 'git'])
        except ServerError, e:
            raise DeployError('Server error.\n\t> %s' % e, base=e)

        # [x] ~/.deploy/{project} exists, or create
        project_name = self.config['project']['name']
        app_directory = '~/.deploy/%s' % project_name
        bare_repo_directory = '%s/src.git' % app_directory
        sources_directory = '%s/src' % app_directory
        try:
            server.has_directories([app_directory, bare_repo_directory, sources_directory])
        except ServerError, e:
            raise DeployError('Server error.\n\t> %s' % e, base=e)

        # [x] check if bare and src git repo exists, create if necessary
        try:
            server.has_git_repositories(bare_repo_directory, sources_directory)
        except Server, e:
            raise DeployError('Server error.\n\t> %s' % e, base=e)

        # [x] Local repo has the remote server
        remote_repo_url = 'ssh://{0}@{1}/home/{0}/.deploy/{2}/src.git'.format(user, address, project_name)
        try:
            remote_repo = self.repository.remote(name='deploy')
            if remote_repo.url != remote_repo_url:
                cw = remote_repo.config_writer
                cw.set('url', remote_repo_url)
        except ValueError, e:
            self.repository.create_remote('deploy', remote_repo_url)

        # [ ] setup supervisor config

        # Warnings
        #   [ ] Local repo has uncommitted changes
        #   [ ] Remote repo is already up to date

        # Do the do
        #   [ ] Push to the remote
        #   [ ] Run the before scripts
        #   [ ] Run the preset
        #   [ ] Run the after scripts

    def execute(self):
        try:
            self.commands[self.cmd]()
        except DeployError, e:
            Terminal.print_error(str(e))
