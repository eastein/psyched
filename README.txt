# About

Psyched is a simple, fast scheduling application for planning your life.
It is task and appointment based, with operations for adding,
modifying, deleting and rescheduling both tasks and appointments.

# Dependencies

Before using Psyched you will want to have the following packages
installed on your system.

## Gentoo

* python
* pygtk
* pysqlite
* notify-python
* pyxml

## Ubuntu

* python
* python-gtk
* python-pysqlite2
* python-notify
* python-xml

## n900

I need to fill this in, there are some complexities here.

# Running Tests

## To run the automatic tests (coverage is pretty low at this point):

    nosetests -v tests

## To run the manual tests, perform these tasks:

* Move your .psyched directory and check that basic program startup works OK.
* Try adding and removing a few tasks and schedule items.
* Create a task and a schedule item and make sure that the alerts work as expected.

# State Files

Psyched stores data in `~/.psyched/psyched.db`.  No other files are
written on disk during normal program operation.
