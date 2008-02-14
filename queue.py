'''
Psyched is a scheduling and task management application.

Copyright 2007-2008 Eric Stein
License: GPL2/GPL3, at your option.  For details see LICENSE.

$Id$
'''

class Queue :
	"A Queue."

	def __init__(self) :
		self.a = []

	def push(self, o) :
		self.a.insert(0, o)

	def pop(self) :
		return self.a.pop()
