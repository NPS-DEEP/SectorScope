                   Announcing SectorScope 0.7.0
                       September 14, 2016

                          RELEASE NOTES

SectorScope Version 0.7.0 has been released for Linux, MacOS and Windows.

## Changes

* *SectorScope* is compatible with *hashdb* 3.0.0.
* Ingest, scan, and media read operations now use *hashdb* instead of *bulk_extractor*.
* *SectorScope* processes scan data faster because *hashdb* 3.0.0 input data is more compact.
* Low and high entropy filters are added which use new entropy data provided by *hashdb* 3.0.0.
* *SectorScope* can export raw sectors to files.
* A Users Manual is now available.
* Miscellaneous functional improvements include:
 * The sector size is now adjustable.
 * More scan statistics are now available in the statistics view.
 * Alternate file paths may be specified when opening a scan file, allowing data files to be relocated.
 * The histogram height can be adjusted, allowing low-frequency events to be visible.
 * Version numbers of *SectorScope* and *hashdb* are displayed to the user.
 * Byte alignment control has been removed:  *SectorScope* now zooms down to the size of the sector.
 * *SectorScope* now accepts matches found in recursively decompressed data.

## Known Limitations
* The histogram bar thumb wheel zoom function may not work on Windows systems.
* The GUI is sluggish. The GUI needs to be redesigned so that actions that take time are performed on alternate threads.

## Future Work
* We expect to replace the existing GUI, which is based on the Tkinter package, with PyQT to enable a more professional look and feel.
* The user interface event handler will be redesigned so that usage does not appear sluggish.  Filter and data load operations will still take time, but they will not "hang" the user interface while calculating.
* More annotations in addition to disk partition (mmls) and file system sector (fsstat) annotations may be provided, offering additional correlation between sectors and user data.

## Resources
* Downloads (Windows installer, source code, users manual): http://digitalcorpora.org/downloads/sectorscope/
* GIT repository (for developers): https://github.com/NPS-DEEP/sectorscope
* Wiki: https://github.com/NPS-DEEP/sectorscope/wiki
* Bulk Extractor Users Group: http://groups.google.com/group/bulk_extractor-users
* Developer: Bruce Allen bdallen nps edu
