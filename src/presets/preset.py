from abc import ABCMeta, abstractmethod


class Preset:
    __metaclass__ = ABCMeta

    @abstractmethod
    def perform_verifications(self):
        """ If any verification is required. """

    @abstractmethod
    def prepare(self):
        """ The preset own method to build or run any preparation scripts. """

    @abstractmethod
    def get_run_cmd(self):
        """ The main run command used by supervisor to start the program. """
