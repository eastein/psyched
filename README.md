<A name="toc1-0" title="About" />
# About

Psyched is a simple, fast scheduling application for planning your life.
It is task and appointment based, with operations for adding,
modifying, deleting and rescheduling both tasks and appointments.

<A name="toc1-7" title="Dependencies" />
# Dependencies

Before using Psyched you will want to have the following packages
installed on your system.

<A name="toc2-13" title="Gentoo" />
## Gentoo

* python
* pygtk
* pysqlite
* notify-python
* pyxml

<A name="toc2-22" title="Ubuntu" />
## Ubuntu

* python
* python-gtk
* python-pysqlite2
* python-notify
* python-xml

<A name="toc2-31" title="n900" />
## n900

I need to fill this in, there are some complexities here.

<A name="toc1-36" title="Running Tests" />
# Running Tests

<A name="toc2-39" title="To run the automatic tests (coverage is pretty low at this point):" />
## To run the automatic tests (coverage is pretty low at this point):

    nosetests -v tests

<A name="toc2-44" title="To run the manual tests, perform these tasks:" />
## To run the manual tests, perform these tasks:

* Move your .psyched directory and check that basic program startup works OK.
* Try adding and removing a few tasks and schedule items.
* Create a task and a schedule item and make sure that the alerts work as expected.

<A name="toc1-51" title="State Files" />
# State Files

Psyched stores data in `~/.psyched/psyched.db`.  No other files are
written on disk during normal program operation.
