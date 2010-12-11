'''
Psyched is a scheduling and task management application.

Copyright 2007-2010 Eric Stein
License: GPL2/GPL3, at your option.  For details see LICENSE.

$Id$
'''

import re

def check_time(s) :
	_reg = re.compile('^(2[0-3]|1[0-9]|0{0,1}[0-9])(:|)[0-5][0-9]$')
	return (_reg.match(s) != None)

def check_interval(s) :
	_reg = re.compile('^([0-9]*(:|)[0-5][0-9]|[0-9])$')
	return (_reg.match(s) != None)
