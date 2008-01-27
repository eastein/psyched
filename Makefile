# Copyright 2007 Eric Stein
# Makefile License: GPL2
# Some parts of makefile copied from Meld, a graphical diff tool.
#
# $Id$

prefix := /usr
bindir := $(prefix)/bin
libdir := $(prefix)/lib
sharedir := $(prefix)/share
libdir_ := $(libdir)/psyched
helpdir_ := $(helpdir)/psyched

psyched.install: psyched
	sed -e "s^#SYSPATH#^sys.path += ['$(DESTDIR)$(libdir_)']^" psyched > psyched.tmp
	sed -e "s%iconpath =.*$%%iconpath = '$(DESTDIR)$(sharedir)/pixmaps'%" psyched.tmp > psyched.install
	rm -f psyched.tmp

install: share/psyched.png psyched.desktop psyched.install psyched_backend.py psyched_strings.py psyched_validate.py
	mkdir -m 755 -p \
		$(DESTDIR)$(bindir) \
		$(DESTDIR)$(libdir_) \
		$(DESTDIR)$(sharedir)/applications \
		$(DESTDIR)$(sharedir)/pixmaps
	install -m 755 psyched.install $(DESTDIR)$(bindir)/psyched
	install -m 644 *.py $(DESTDIR)$(libdir_)
	install -m 644 share/psyched.png $(DESTDIR)$(sharedir)/pixmaps
	install -m 644 psyched.desktop $(DESTDIR)$(sharedir)/applications

uninstall:
	-rm -rf \
		$(libdir_) \
		$(sharedir)/pixmaps/psyched.png \
		$(sharedir)/applications/psyched.desktop \
		$(bindir)/psyched

clean:
	rm -f psyched.install
