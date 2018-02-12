import sys



class Configuration:
    def __init__(self):
        #For now, configuration is hard-coded.
        #In the future, load from config file.
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
        self.readCommandline()


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

