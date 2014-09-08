INSTRUCTIONS

To install the tool, edit the "../MASTER_scripts/config" file. Be sure to edit the following parameters: 
ALL_NODES 
WORKER_SCRIPT_DIR
MASTER_SCRIPT_DIR
WORKER_TMP_DIR
MASTER_RESULTS_DIR

Next, run the install.sh script to install. Be sure to run the install script on the master node. If you wish to collect data on the master node as well, include the hostname of the master node in the 'ALL_NODES' parameter in the config file.
**Please Note that paswordless ssh is required for each 'node' listed in the 'ALL_NODES' parameter.**

After installation go to the "MASTER_SCRIPT_DIR" location. You may make further edits to the "config" file and then run the "runall" script to run. Update the "CMD_PATH" variable in the config file.

The 'runall' script can be run with an optional argument which specifies a
name for your results, otherwise a datestamp is used. e.g %runall [test_run]

The recommended version of sysstat is version 9.0.4 or newer. At least Microsoft Office 2010 is also recommended.

Once the job is done, all the data is collated and copied to the master node across the cluster into the "MASTER_RESULTS_DIR"

To postprocess, copy the entire results directory to a windows machine, navigate to the "instruments" directory and then open the provided spreadsheet template. Press Ctrl-q to launch the macros that will import all the data, draw tables and plot graphs.

Contact olasoji.denloye@intel.com with questions regarding this tool.

Enjoy.




Contact olasoji.denloye@intel.com for support.
