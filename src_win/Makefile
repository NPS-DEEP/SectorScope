# Run this Makefile to build the block_match Windows Installer and
# the .zip distribution.  Both are copied into the download directory.

VERSION = 0.0.3

SOURCES = ../python/*.py

INSTALLER = block_match-$(VERSION)-windowsinstaller.exe
ZIP = block_match-$(VERSION).zip
ZIP_DIR = block_match-$(VERSION)

all: installer zip

installer: $(INSTALLER)

$(INSTALLER): build_installer.nsi EnvVarUpdate.nsi $(SOURCES)
	@echo Making $(INSTALLER)
	makensis -DVERSION=$(VERSION) build_installer.nsi
	cp $(INSTALLER) download/$(INSTALLER)
	echo '**************** INSTALLER IS MADE ****************'

zip: $(ZIP)

$(ZIP): $(SOURCES)
	rm -rf $(ZIP_DIR)
	mkdir $(ZIP_DIR)
	cp $(SOURCES) $(ZIP_DIR)
	zip -r9 $(ZIP) $(ZIP_DIR)
	rm -rf $(ZIP_DIR)
	cp $(ZIP) download/$(ZIP)

clean:
	/bin/rm -rf $(INSTALLER) $(ZIP_DIR) $(ZIP)

.PHONY: installer zip clean

