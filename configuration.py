import sys
import os.path
import configparser



class Configuration:
    def __init__(self):
        self.loadDefaults()
        self.loadFile('~/.fireworks/config')
        self.readCommandline()


    def loadDefaults(self):
        self.sections = \
        {
        'modules':
            {
            'frontend': 'qt',
            'backend': 'lightningd'
            },
        'lightningd':
            {
            'lightning-dir': '~/.lightning'
            }
        }


    def loadFile(self, filename):
        filename = os.path.expanduser(filename)
        config = configparser.ConfigParser()
        config.read(filename)
        for section in config.sections():
            for name in config[section]:
                self.setValue(section, name, config[section][name])


    def readCommandline(self):
        for arg in sys.argv[1:]:
            try:
                name, value = arg.split('=')
                section, name = name.split('/')
                self.setValue(section, name, value)
            except ValueError:
                continue #different syntax - ignore


    def getValue(self, section, name):
        return self.sections[section][name]


    def setValue(self, section, name, value):
        if section not in self.sections:
            self.sections[section] = {}
        self.sections[section][name] = value

