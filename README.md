PAT
===

**_Performance Analysis Tool (PAT)_** is a flexible performance profiling framework designed for Linux operating system. It gathers system level performance metrics including CPU, Disk and Network as well as detailed software hot methods. It generates a pdf and a Microsoft Excel file at the end to provide an instant visual representation of the data. PAT can be configured for a single machine, a subset of a cluster or an entire cluster of machines. User also can customize the metrics being collected. PAT can be used for workload characterization, performance study and software optimization.


<p align = "center">
<img src=https://cloud.githubusercontent.com/assets/13007048/19003282/f5991524-8704-11e6-9471-65438aabdf33.png width="530"/>
</p>
<p align = "center">
Figure 1: CPU chart
</p><br><br><br>


<p align = "center">
<img src=https://cloud.githubusercontent.com/assets/13007048/19003283/f5995c96-8704-11e6-9b47-53156181c6c4.png width="530"/>
</p>
<p align = "center">
Figure 2: Disk chart
</p><br><br><br>

<p align = "center">
<img src=https://cloud.githubusercontent.com/assets/13007048/19003284/f59c702a-8704-11e6-9bdd-317d7d86ea7a.png width="530"/>
</p>
<p align = "center">
Figure 3: Network chart
</p><br><br><br>

<p align = "center">
<img src=https://cloud.githubusercontent.com/assets/13007048/18935780/2950e0fa-8597-11e6-9d0c-d5437e8e4941.png width="530"/>
</p>
<p align = "center">
Figure 4: Perf module
</p><br><br><br>
</p>

## I. ARCHITECTURE OVERVIEW:

- Collecting data phase is run completely on the server.
- In postprocess phase modular approach is being used to increase scalability.
- Each node in the cluster is mapped to a node object.
- The node object holds separate objects for each of the metrics (such as DISK, NETWORK, CPU, PERF) that were measured using PAT. These objects contain actual raw data in an internal data structure [Figure 5]. 
- Modules for DISK, NETWORK, CPU and PERF have been implemented.

<p align = center>
<img src=https://cloud.githubusercontent.com/assets/13007048/9281698/c045391c-427b-11e5-9030-bdbc0c4d6152.jpg />
</p>
<p align = "center">
Figure 5: PAT Post-Processing architecture
</p>


## II. SOFTWARE REQUIREMENTS:

- For collecting data
  - Linux Sysstat (version 9.0.4 or newer) 
  - gawk 
  - perf 
- For postprocess data
  - MS Office 2010 or higher
  - **Python 2.7.x+ (on the python2 series). Post-process script will NOT work on Python 3.x+**
  - matplotlib 1.3.1+ **matplotlib 1.5.3 is the last one that post-process script will work on**
  - xlsxwriter 0.6.3+

## III. STEPS FOR INSTALLING DEPENDENCIES:

Before installing any dependencies it is recommended to first update the local package index. 

**_(Fedora / CentOS / RHEL)_** 

    yum -y update

**_(Debian / Ubuntu)_** 

    apt-get update


## Gawk, sysstat, perf 
Gawk, sysstat and perf should be installed by default on every modern full-fledged Linus system. To check the version type
`gawk --version`      (will tell you the version of gawk)

`sar -V`              (will tell yo the version of sysstat)

`perf --version`      (will tell you the version of perf)


## Python:
If you are working on Linux machine then by default you should have Python already install. Update to 2.7 if you have older version.  

Make sure you are using the same version of Python as the OS is using. To check that

1. Go to /usr/bin and type `python -V` (will tell you which version of Python OS is using)

2. `python` will tell you which version of Python you are using and `which python` will tell you the location of Python you are using. You want 1. and 2. to be the same. 

## pip:
If you have Python 2.7.9+ (on the python2 series) or Python 3.4+ then by default you ought to have pip already install. If not, then

**_(recomended)_**

    wget https://bootstrap.pypa.io/get-pip.py
    <path you your python executable> get-pip.py

**_(Fedora / CentOS / RHEL)_**

Installing pip using `sudo yum install python-pip` may install an older version of the pip that can produce build errors while installing new libraries.

**_(Debian / Ubuntu)_**

    sudo apt-get install python-pip

## matplotlib:

**_(recomended)_**

    sudo pip install matplotlib

**_(Fedora / CentOS / RHEL) (pip is not installed)_**

    sudo yum install python-matplotlib 

Installing matplotlib using pip is preferred as yum may download and install older version of library that may not be compatible with the tool.

**_(Debian / Ubuntu) (pip is not installed)_**

    sudo apt-get install python-matplotlib

If you encounter an error 

> Could not find a version that satisfies the requirement python-matplotlib (from versions:) 

> No matching distribution found for python-matplotlib

then you should:

    sudo yum install python-devel
    sudo yum install libprog-devel
    sudo yum install libpng-devel
    git clone https://github.com/matplotlib/matplotlib.git
    cd matplotlib
    python setup.py install

To check the version of pip and associated python type `pip -V`. Your version of pip must be the same as version of Python you want to use. 

## XlsxWriter:

**_(recommended)_**

    sudo pip install XlsxWriter	

**_(Debian / Ubuntu) (pip is not installed)_**

    sudo apt-get install python-xlsxwriter

**_(Fedora / CentOS / RHEL) (pip is not installed)_**  

    curl -O -L http://github.com/jmcnamara/XlsxWriter/archive/master.tar.gz
    tar zxvf master.tar.gz
    cd XlsxWriter-master/
    sudo python setup.py install

To check the version of the library in terminal type `python` (will get you to Python script) and then

    import matplotlib
    matplotlib.__version__

Above two lines will check matplotlib version. Similarly next two lines will tell you the version of XlsxWriter: 

    import xlsxwriter
    xlsxwriter.__version__


## IV. TROUBLESHOOTING ISSUES:
> /usr/lib64/python2.7/site-packages/matplotlib/__init__.py:1005: UserWarning:  This call to matplotlib.use() has no effect
> because the the backend has already been chosen;
> matplotlib.use() must be called *before* pylab, matplotlib.pyplot, or matplotlib.backends is imported for the first time.

`pip install --upgrade numpy scipy matplotlib` will upgrade Python libraries and solve the error

## V. CONFIGURATION:

> :information_source: To collect PAT data you must be a root. Alternatively go to `/proc/sys/kernel/` and `set perf_event_paranoid to 0` (you need root permissions). This flag allow you to collect perf data without being a root.

To install the PAT tool, make a copy of the `./config_template` file as `./config`, and make all your edits within the `./config` file:

`ALL_NODES`          (this needs to be in a format of <hostname>:<port>; the port is expected to be the port ID of the SSH port, which is often 22). If you wish to collect data on the master node as well, make sure to include the hostname of the master node here as well.

`WORKER_SCRIPT_DIR`  (where worker scripts will live on each worker node)

`WORKER_TMP_DIR`     (where workers will store temporary files on each node)

> :information_source: Please Note that paswordless ssh is required for each 'node' listed in the 'ALL_NODES' parameter.

You may make further edits to the `./config` file at this point. You can update the `CMD_PATH` variable inside `./config` file to be either the path to a script that you wish to run, or the actual command line that you wish to run. After `CMD_PATH` is updated with your desired command or script, run `./pat run` on the master node to start the run and collect the data. The `./pat run` command can be run with an optional argument which specifies a name for your results, otherwise a timestamp is used. e.g `./pat run [test_run_name]`. Once the job is done, all the data is collated and copied to the master node across the cluster to the `results` directory, under the `[test_run_name]` (or `timestamp`) folder.


**config.xml** is the file where you make all postprocess configuration changes. Below instructions are dedicated to that file.
- Before you modify anything in configuration file, make sure your data are stored in directories (each data node in separate directory). Most likely your data are in a format of `<hostname>:<port>`
- Make changes in config.xml file that suit your needs. Between the tag `<source></source>` specify the path to the directory that contains PAT data. By default it is a directory where your `<hostname>:<port>` data are located (for most cases this will be an instruments directory in your PAT-RESULT folder. In this case the path will be of the form `/foo/bar/instruments/`).
- You may eliminate node(s) if you do not want to do any calculations on that node(s). To do that between the tag `<exclude-node></exclude-node>` specify the name of the node(s) that you want to discard. The exclude-node entry should match the value under 'hostname' in files within the node-name directory. This node will be excluded while computing averages across all nodes. Otherwise further actions are not required. If you wish to do calculations on all nodes then leave everything in default settings. 
- You are also able to turn on or off detailed graphs and averaged graphs by modifying the config.xml file. By default only averaged graphs will be printed and excel file will contain all 4 metric outputs.
- During runtime a different config.xml file can be given as a command line argument to the pat-post-process script. It will override the default config.xml file.

## VI. EXECUTION:

Launch `./pat run` to collect data and then  `./pat-post-process.py` to postporcess collected data.

## VII. OUTPUT:
- Postprocess data will be located at the same path that was entered in the tag `<source></source>`. Copy the entire results directory to a Windows machine, navigate to the `instruments` directory and then open the provided spreadsheet. In Excel 2010 and above press **Ctrl+q** to launch the macros that will import all the data, draw tables and plot graphs.
- Output can be customized by editing the config.xml file. The pdf and excel contains only the data specified in the config.xml file.
- The output consists of 2 files – a pdf file that gives a visual representation of data, and an excel file that contains RAW data along with macros to draw the relevant charts.


For questions regardng tool contact 
- Olasoji Denloy at olasoji.denloye@intel.com 
- Yingqi (Lucy) Lu at yingqi.lu@intel.com
- Eric Kaczmarek at eric.kaczmarek@intel.com
- Agata Gruza at agata.gruza@intel.com




