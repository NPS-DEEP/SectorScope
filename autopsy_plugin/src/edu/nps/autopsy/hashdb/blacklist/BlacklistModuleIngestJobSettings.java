// The software provided here is released by the Naval Postgraduate
// School, an agency of the U.S. Department of Navy.  The software
// bears no warranty, either expressed or implied. NPS does not assume
// legal liability nor responsibility for a User's use of the software
// or the results of such use.
//
// Please note that within the United States, copyright protection,
// under Section 105 of the United States Code, Title 17, is not
// available for any work of the United States Government and/or for
// any works created by United States Government employees. User
// acknowledges that this software contains work which was created by
// NPS government employees and is therefore in the public domain and
// not subject to copyright.
//
// Released into the public domain on April 28, 2015 by Bruce Allen.

package edu.nps.autopsy.hashdb.blacklist;

import org.sleuthkit.autopsy.ingest.IngestModuleIngestJobSettings;

/**
 * Ingest job options for sample ingest module instances.
 */
public class BlacklistModuleIngestJobSettings implements IngestModuleIngestJobSettings {
    
    private static final long serialVersionUID = 1L;
    private String hashdbDir = "enter path to blacklist .hdb directory";

    BlacklistModuleIngestJobSettings() {
    }

    BlacklistModuleIngestJobSettings(String hashdbDir) {
        this.hashdbDir = hashdbDir;
    }

    @Override
    public long getVersionNumber() {
        return serialVersionUID;
    }    
    
    void setHashdbDir(String hashdbDir) {
        this.hashdbDir = hashdbDir;
    }

    String getHashdbDir() {
        return hashdbDir;
    }
}
