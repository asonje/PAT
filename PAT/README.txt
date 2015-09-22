INSTRUCTIONS

To install the tool, make a copy of the "./config_template" file as "./config", 
and make all your edits within the "./config" file.

Be sure to edit the following parameters: 
ALL_NODES          (this needs to be in a format of <hostname>:<port>; the port
                    is expected to be the port ID of the SSH port, which is often 22)
WORKER_SCRIPT_DIR  (where worker scripts will live on each worker node)
WORKER_TMP_DIR     (where workers will store temporary files on each node)

Next, run "./pat install" script to install PAT on all nodes. Be sure to run the 
install script on the master node. If you wish to collect data on the master node
as well, make sure to include the hostname of the master node in the 'ALL_NODES'
parameter in the config file.
**Please Note that paswordless ssh is required for each 'node' listed in the
'ALL_NODES' parameter.**

You may make further edits to the "./config" file at this point.
You can update the "CMD_PATH" variable inside "./config" file to be either the path
to a script that you wish to run, or the actual command line that you wish to run.
After "CMD_PATH" is updated with your desired command or script, run "./pat run"
to start the run.

The "./pat run" command can be run with an optional argument which specifies a
name for your results, otherwise a timestamp is used. e.g %./pat run [test_run_name]

The recommended version of sysstat is version 9.0.4 or newer. 
At least Microsoft Office 2010 is also recommended.

Once the job is done, all the data is collated and copied to the master node across
the cluster to the "results" directory, under the [test_run_name] (or timestamp) folder.

To postprocess, copy the entire results directory to a Windows machine, navigate to the
"instruments" directory and then open the provided spreadsheet template. Press Ctrl-q 
to launch the macros that will import all the data, draw tables and plot graphs.

Contact olasoji.denloye@intel.com with questions regarding this tool.

Enjoy.
