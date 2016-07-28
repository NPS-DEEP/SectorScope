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

package edu.nps.sectorscope;

import org.openide.util.NbBundle;
import org.openide.util.lookup.ServiceProvider;
import org.sleuthkit.autopsy.ingest.IngestModuleFactory;
import org.sleuthkit.autopsy.ingest.DataSourceIngestModule;
import org.sleuthkit.autopsy.ingest.FileIngestModule;
import org.sleuthkit.autopsy.ingest.IngestModuleGlobalSettingsPanel;
import org.sleuthkit.autopsy.ingest.IngestModuleIngestJobSettings;
import org.sleuthkit.autopsy.ingest.IngestModuleIngestJobSettingsPanel;

/**
 * A factory for creating email parser file ingest module instances.
 */
@ServiceProvider(service = IngestModuleFactory.class)
public class BlacklistIngestModuleFactory implements IngestModuleFactory {

    private static final String VERSION_NUMBER = "1.0.0";

    // This class method allows the ingest module instances created by this 
    // factory to use the same display name that is provided to the Autopsy
    // ingest framework by the factory.
    static String getModuleName() {
        return NbBundle.getMessage(BlacklistIngestModuleFactory.class, "BlacklistIngestModuleFactory.moduleName");
    }

    /**
     * Gets the display name that identifies the family of ingest modules the
     * factory creates. Autopsy uses this string to identify the module in user
     * interface components and log messages. The module name must be unique. so
     * a brief but distinctive name is recommended.
     *
     * @return The module family display name.
     */
    @Override
    public String getModuleDisplayName() {
        return getModuleName();
    }

    /**
     * Gets a brief, user-friendly description of the family of ingest modules
     * the factory creates. Autopsy uses this string to describe the module in
     * user interface components.
     *
     * @return The module family description.
     */
    @Override
    public String getModuleDescription() {
        return NbBundle.getMessage(BlacklistIngestModuleFactory.class, "BlacklistIngestModuleFactory.moduleDescription");
    }

    /**
     * Gets the version number of the family of ingest modules the factory
     * creates.
     *
     * @return The module family version number.
     */
    @Override
    public String getModuleVersionNumber() {
        return VERSION_NUMBER;
    }

    /**
     * Queries the factory to determine if it provides a user interface panel to
     * allow a user to change settings that are used by all instances of the
     * family of ingest modules the factory creates. For example, the Autopsy
     * core hash lookup ingest module factory provides a global settings panel
     * to import and create hash databases. The hash databases are then enabled
     * or disabled per ingest job using an ingest job settings panel. If the
     * module family does not have global settings, the factory may extend
     * IngestModuleFactoryAdapter to get an implementation of this method that
     * returns false.
     *
     * @return True if the factory provides a global settings panel.
     */
    @Override
    public boolean hasGlobalSettingsPanel() {
        return false;
    }

    /**
     * Gets a user interface panel that allows a user to change settings that
     * are used by all instances of the family of ingest modules the factory
     * creates. For example, the Autopsy core hash lookup ingest module factory
     * provides a global settings panel to import and create hash databases. The
     * imported hash databases are then enabled or disabled per ingest job using
     * ingest an ingest job settings panel. If the module family does not have a
     * global settings, the factory may extend IngestModuleFactoryAdapter to get
     * an implementation of this method that throws an
     * UnsupportedOperationException.
     *
     * @return A global settings panel.
     */
    @Override
    public IngestModuleGlobalSettingsPanel getGlobalSettingsPanel() {
        throw new UnsupportedOperationException();
    }

    /**
     * Gets the default per ingest job settings for instances of the family of
     * ingest modules the factory creates. For example, the Autopsy core hash
     * lookup ingest modules family uses hash databases imported or created
     * using its global settings panel. All of the hash databases are enabled by
     * default for an ingest job. If the module family does not have per ingest
     * job settings, the factory may extend IngestModuleFactoryAdapter to get an
     * implementation of this method that returns an instance of the
     * NoIngestModuleJobSettings class.
     *
     * @return The default ingest job settings.
     */
    @Override
    public IngestModuleIngestJobSettings getDefaultIngestJobSettings() {
        return new BlacklistModuleIngestJobSettings();
    }

    /**
     * Queries the factory to determine if it provides user a interface panel to
     * allow a user to make per ingest job settings for instances of the family
     * of ingest modules the factory creates. For example, the Autopsy core hash
     * lookup ingest module factory provides an ingest job settings panels to
     * enable or disable hash databases per ingest job. If the module family
     * does not have per ingest job settings, the factory may extend
     * IngestModuleFactoryAdapter to get an implementation of this method that
     * returns false.
     *
     * @return True if the factory provides ingest job settings panels.
     */
    @Override
    public boolean hasIngestJobSettingsPanel() {
        return true;
    }

    /**
     * Gets a user interface panel that can be used to set per ingest job
     * settings for instances of the family of ingest modules the factory
     * creates. For example, the core hash lookup ingest module factory provides
     * an ingest job settings panel to enable or disable hash databases per
     * ingest job. If the module family does not have per ingest job settings,
     * the factory may extend IngestModuleFactoryAdapter to get an
     * implementation of this method that throws an
     * UnsupportedOperationException.
     *
     * @param setting Per ingest job settings to initialize the panel.
     * @return An ingest job settings panel.
     */
    @Override
    public IngestModuleIngestJobSettingsPanel getIngestJobSettingsPanel(IngestModuleIngestJobSettings settings) {
        if (!(settings instanceof BlacklistModuleIngestJobSettings)) {
            throw new IllegalArgumentException("Expected settings argument to be instanceof BlacklistModuleIngestJobSettings");
        }
        return new BlacklistIngestModuleIngestJobSettingsPanel((BlacklistModuleIngestJobSettings) settings);
    }

    /**
     * Queries the factory to determine if it is capable of creating data source
     * ingest modules. If the module family does not include data source ingest
     * modules, the factory may extend IngestModuleFactoryAdapter to get an
     * implementation of this method that returns false.
     *
     * @return True if the factory can create data source ingest modules.
     */
    @Override
    public boolean isDataSourceIngestModuleFactory() {
        return true;
    }

    /**
     * Creates a data source ingest module instance.
     * <p>
     * Autopsy will generally use the factory to several instances of each type
     * of module for each ingest job it performs. Completing an ingest job
     * entails processing a single data source (e.g., a disk image) and all of
     * the files from the data source, including files extracted from archives
     * and any unallocated space (made to look like a series of files). The data
     * source is passed through one or more pipelines of data source ingest
     * modules. The files are passed through one or more pipelines of file
     * ingest modules.
     * <p>
     * The ingest framework may use multiple threads to complete an ingest job,
     * but it is guaranteed that there will be no more than one module instance
     * per thread. However, if the module instances must share resources, the
     * modules are responsible for synchronizing access to the shared resources
     * and doing reference counting as required to release those resources
     * correctly. Also, more than one ingest job may be in progress at any given
     * time. This must also be taken into consideration when sharing resources
     * between module instances. modules.
     * <p>
     * If the module family does not include data source ingest modules, the
     * factory may extend IngestModuleFactoryAdapter to get an implementation of
     * this method that throws an UnsupportedOperationException.
     *
     * @param settings The settings for the ingest job.
     * @return A data source ingest module instance.
     */
    @Override
    public DataSourceIngestModule createDataSourceIngestModule(IngestModuleIngestJobSettings settings) {
        if (!(settings instanceof BlacklistModuleIngestJobSettings)) {
            throw new IllegalArgumentException("Expected settings argument to be instanceof BlacklistModuleIngestJobSettings");
        }
        return new BlacklistDataSourceIngestModule((BlacklistModuleIngestJobSettings) settings);
    }

    /**
     * Queries the factory to determine if it is capable of creating file ingest
     * modules. If the module family does not include file ingest modules, the
     * factory may extend IngestModuleFactoryAdapter to get an implementation of
     * this method that returns false.
     *
     * @return True if the factory can create file ingest modules.
     */
    @Override
    public boolean isFileIngestModuleFactory() {
        return false;
    }

    /**
     * Creates a file ingest module instance.
     * <p>
     * Autopsy will generally use the factory to several instances of each type
     * of module for each ingest job it performs. Completing an ingest job
     * entails processing a single data source (e.g., a disk image) and all of
     * the files from the data source, including files extracted from archives
     * and any unallocated space (made to look like a series of files). The data
     * source is passed through one or more pipelines of data source ingest
     * modules. The files are passed through one or more pipelines of file
     * ingest modules.
     * <p>
     * The ingest framework may use multiple threads to complete an ingest job,
     * but it is guaranteed that there will be no more than one module instance
     * per thread. However, if the module instances must share resources, the
     * modules are responsible for synchronizing access to the shared resources
     * and doing reference counting as required to release those resources
     * correctly. Also, more than one ingest job may be in progress at any given
     * time. This must also be taken into consideration when sharing resources
     * between module instances. modules.
     * <p>
     * If the module family does not include file ingest modules, the factory
     * may extend IngestModuleFactoryAdapter to get an implementation of this
     * method that throws an UnsupportedOperationException.
     *
     * @param settings The settings for the ingest job.
     * @return A file ingest module instance.
     */
    @Override
    public FileIngestModule createFileIngestModule(IngestModuleIngestJobSettings settings) {
        if (!(settings instanceof BlacklistModuleIngestJobSettings)) {
            throw new IllegalArgumentException("Expected settings argument to be instanceof BlacklistModuleIngestJobSettings");
        }
        return new BlacklistFileIngestModule();
    }
}

