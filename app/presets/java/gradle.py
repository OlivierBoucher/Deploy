from ..preset import Preset


class JavaGradlePreset(Preset):

    def __init__(self):
        pass

    def prepare(self):
        pass

    def get_run_cmd(self):
        return '/bin/bash run.sh'

    def perform_verifications(self):
        """
        Perform verifications such as build.gradle file detection,
        gradle wrapper detection, etc...

        """
        pass

    def get_environment_vars(self):
        return ''
