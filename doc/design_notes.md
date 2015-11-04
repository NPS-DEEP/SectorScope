# SectorScope Import
import <image>, <hashdb_dir>
Import from a media image into an existing or new hashdb.

# SectorScope Scan
scan <image>, <hashdb_dir.hdb>, <new sectorscope output.ss>

output.ss is a directory containing the following files:

* settings.json
  * path to image
  * path to hashdb
* the identified_blocks_expanded.txt file
* mysql metadata file image_metadata.db
