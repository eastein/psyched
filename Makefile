# Copyright 2007-2008 Eric Stein
# Makefile License: GPL2
# Some parts of makefile copied from Meld, a graphical diff tool.
#
# $Id$

prefix := /usr
bindir := $(prefix)/bin
libdir := $(prefix)/lib
sharedir := $(prefix)/share
libdir_ := $(libdir)/psyched

psyched.install: psyched
	sed -e "s^#SYSPATH#^sys.path += ['$(libdir_)']^" psyched > psyched.tmp
	sed -e "s%iconpath =.*$%%iconpath = '$(sharedir)/pixmaps'%" psyched.tmp > psyched.install
	rm -f psyched.tmp

install: share/psyched.png psyched.desktop psyched.install psyched_backend.py psyched_strings.py psyched_validate.py psyched_notify.py
	mkdir -m 755 -p \
		$(bindir) \
		$(libdir_) \
		$(sharedir)/applications \
		$(sharedir)/pixmaps
	install -m 755 psyched.install $(bindir)/psyched
	install -m 644 *.py $(libdir_)
	install -m 644 share/psyched.png $(sharedir)/pixmaps
	install -m 644 psyched.desktop $(sharedir)/applications

uninstall:
	-rm -rf \
		$(libdir_) \
		$(sharedir)/pixmaps/psyched.png \
		$(sharedir)/applications/psyched.desktop \
		$(bindir)/psyched

clean:
	rm -f psyched.install
