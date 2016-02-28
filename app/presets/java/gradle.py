from ..preset import Preset


class JavaGradlePreset(Preset):

    def __init__(self):
        pass

    def prepare(self):
        pass

    def get_run_cmd(self):
        return '/bin/bash run.sh'

    def perform_verifications(self):
        pass

    def get_environment_vars(self):
        return ''
