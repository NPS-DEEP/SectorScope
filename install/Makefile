# Run this Makefile to build the NPS-block_match Windows Installer and
# the .zip distribution.  Both are copied into the download directory.
#
# Prerequisites:
# UM: please run make in UM_DIR.
# .nbm file: The .nbm file is generated using NetBeans on Windows.
#            Build it on Windows and then git push to make it current.

VERSION = 0.4.0

SOURCES = ../python/*.py
ICONS = ../python/icons/*.gif
UM_DIR = ../doc/sectorscope_um
UM_FROM = $(UM_DIR)/sectorscope_um.pdf
UM_TO = download/sectorscope_um.pdf

WIN_INSTALLER = NPS-SectorScope-$(VERSION)-windowsinstaller.exe
ZIP = NPS-SectorScope-$(VERSION).zip
ZIP_DIR = NPS-SectorScope-$(VERSION)
AUTOPSY_PLUGIN_FROM = ../SectorScope_autopsy_plugin/build/edu-nps-sectorscope.nbm
AUTOPSY_PLUGIN_TO = download/NPS-SectorScope-$(VERSION).nbm

all: zip $(AUTOPSY_PLUGIN_TO) $(UM_TO) win_installer

win_installer: $(WIN_INSTALLER)

$(WIN_INSTALLER): build_installer.nsi EnvVarUpdate.nsi $(UM_TO) $(SOURCES)
	@echo Making $(WIN_INSTALLER)
	makensis -DVERSION=$(VERSION) build_installer.nsi
	cp $(WIN_INSTALLER) download/$(WIN_INSTALLER)
	@echo '**************** WINDOWS INSTALLER IS MADE ****************'

$(UM_FROM):
	@echo Please run make in $(UM_DIR)
	exit 1

$(UM_TO): $(UM_FROM)
	cp $(UM_FROM) $(UM_TO)

zip: $(ZIP)

$(ZIP): $(SOURCES) $(UM_TO)
	rm -rf $(ZIP_DIR)
	mkdir $(ZIP_DIR)
	cp $(SOURCES) $(ZIP_DIR)
	mkdir $(ZIP_DIR)/icons
	cp $(ICONS) $(ZIP_DIR)/icons
	zip -r9 $(ZIP) $(ZIP_DIR)
	rm -rf $(ZIP_DIR)
	cp $(ZIP) download/$(ZIP)

$(AUTOPSY_PLUGIN_TO): $(AUTOPSY_PLUGIN_FROM)
	cp $(AUTOPSY_PLUGIN_FROM) $(AUTOPSY_PLUGIN_TO)

clean:
	/bin/rm -rf $(WIN_INSTALLER) download/$(WIN_INSTALLER) \
                    $(ZIP_DIR) $(ZIP) $(AUTOPSY_PLUGIN_TO) $(UM_TO)

.PHONY: win_installer zip clean

