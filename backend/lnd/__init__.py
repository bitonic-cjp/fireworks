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

import os
import sys

#The modules in this directory are importing each other through absolute
#imports. This doesn't work by default, since by default this directory is not
#in the module search path.
#Fixing this in the modules themselves would require ugly hacks, since
#these modules are auto-generated.
#So, instead, we add this directory to the module search path when this
#__init__.py is run; that is: when any external module imports anything from
#this directory.
thisModuleDir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(thisModuleDir)

