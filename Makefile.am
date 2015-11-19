ACLOCAL_AMFLAGS = -I m4

SRC_WIN = src_win
#include src_win/Makefile

SUBDIRS = src

SRC_WIN_DIST = \
	src_win/README

# don't include bootstrap. People run it, and they shoudln't
# It's only for people who check out the git repo
EXTRA_DIST = \
	$(SRC_WIN_DIST)

RELEASE	= $(PACKAGE)-$(VERSION)

