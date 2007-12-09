import re

def check_time(s) :
	_reg = re.compile('^(2[0-3]|1[0-9]|0{0,1}[0-9]):[0-5][0-9]$')
	return (_reg.match(s) != None)

def check_interval(s) :
	_reg = re.compile('^([1-9]{1}[0-9]*:[0-5][0-9]|[0-9]+)$')
	return (_reg.match(s) != None)
