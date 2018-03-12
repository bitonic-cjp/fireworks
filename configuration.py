#    Copyright (C) 2018 by Bitonic B.V.
#
#    This file is part of Fireworks.
#
#    Fireworks is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Fireworks is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Fireworks. If not, see <http://www.gnu.org/licenses/>.

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
            'dir': '~/.lightning'
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

