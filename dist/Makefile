# Run this Makefile to build the NPS-block_match Windows Installer and
# the .zip distribution.  Both are copied into the download directory.

VERSION = 0.1.0

SOURCES = ../python/*.py
UM_DIR = ../doc/block_match_viewer_um
UM = block_match_viewer_um.pdf

INSTALLER = NPS-block_match-$(VERSION)-windowsinstaller.exe
ZIP = NPS-block_match-$(VERSION).zip
ZIP_DIR = NPS-block_match-$(VERSION)

all: installer zip

installer: $(INSTALLER)

$(INSTALLER): build_installer.nsi EnvVarUpdate.nsi $(UM) $(SOURCES)
	@echo Making $(INSTALLER)
	makensis -DVERSION=$(VERSION) build_installer.nsi
	cp $(INSTALLER) download/$(INSTALLER)
	@echo '**************** INSTALLER IS MADE ****************'

$(UM_DIR)/$(UM):
	@echo Please run make in $(UM_DIR)
	exit 1

$(UM): $(UM_DIR)/$(UM)
	cp $(UM_DIR)/$(UM) .

zip: $(ZIP)

$(ZIP): $(SOURCES) $(UM)
	rm -rf $(ZIP_DIR)
	mkdir $(ZIP_DIR)
	cp $(SOURCES) $(ZIP_DIR)
	zip -r9 $(ZIP) $(ZIP_DIR)
	rm -rf $(ZIP_DIR)
	cp $(ZIP) download/$(ZIP)

clean:
	/bin/rm -rf $(INSTALLER) $(ZIP_DIR) $(ZIP) $(UM)

.PHONY: installer zip clean

