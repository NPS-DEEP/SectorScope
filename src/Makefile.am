# Author:  Bruce Allen <bdallen@nps.edu>
# Created: 10/28/2015
#
# The software provided here is released by the Naval Postgraduate
# School, an agency of the U.S. Department of Navy.  The software
# bears no warranty, either expressed or implied. NPS does not assume
# legal liability nor responsibility for a User's use of the software
# or the results of such use.
#
# Please note that within the United States, copyright protection,
# under Section 105 of the United States Code, Title 17, is not
# available for any work of the United States Government and/or for
# any works created by United States Government employees. User
# acknowledges that this software contains work which was created by
# NPS government employees and is therefore in the public domain and
# not subject to copyright.
#
# Released into the public domain on November 18, 2015 by Bruce Allen.

test_SOURCES = test.cpp

JSON_INCS = \
	json/JSON.cpp \
	json/JSON.h \
	json/JSONValue.cpp \
	json/JSONValue.h

READER_INCS = \
        $(JSON_INCS) \
	data_reader.cpp \
	data_reader.h

MANAGER_INCS = \
        data_manager.cpp \
        data_manager.h

bin_PROGRAMS = test

#lib_LTLIBRARIES = libdata_reader.la libdata_manager.la
#noinst_LTLIBRARIES = libdata_reader.la libdata_manager.la
#libdata_reader_la_SOURCES = $(READER_INCS)
#libdata_manager_la_SOURCES = $(MANAGER_INCS)

EXTRA_DIST = \
	json/LICENSE \
	json/README \
	json/README.md

#libdata_reader_la_CFLAGS = -avoid-version
#libdata_manager_la_CFLAGS = -avoid-version

AM_CPPFLAGS = -I${top_srcdir}/src/json

AM_CFLAGS = $(SECTORSCOPE_CFLAGS)
AM_CXXFLAGS = $(SECTORSCOPE_CXXFLAGS)

