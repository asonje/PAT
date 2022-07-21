PAT
===

**_Performance Analysis Tool (PAT)_** is a flexible performance profiling framework designed for Linux operating system. It gathers system level performance metrics including CPU, Disk and Network as well as detailed software hot methods. It generates a pdf and a Microsoft Excel file at the end to provide an instant visual representation of the data. PAT can be configured for a single machine, a subset of a cluster or an entire cluster of machines. User also can customize the metrics being collected. PAT can be used for workload characterization, performance study and software optimization.

<p align = "center">
<img src=https://cloud.githubusercontent.com/assets/13007048/19003282/f5991524-8704-11e6-9471-65438aabdf33.png width="530"/>
</p>
<p align = "center">
Figure 1: CPU chart
</p><br>

<p align = "center">
<img src=https://cloud.githubusercontent.com/assets/13007048/19003283/f5995c96-8704-11e6-9b47-53156181c6c4.png width="530"/>
</p>
<p align = "center">
Figure 2: Disk chart
</p><br>

<p align = "center">
<img src=https://cloud.githubusercontent.com/assets/13007048/19003284/f59c702a-8704-11e6-9bdd-317d7d86ea7a.png width="530"/>
</p>
<p align = "center">
Figure 3: Network chart
</p><br>

<p align = "center">
<img src=https://cloud.githubusercontent.com/assets/13007048/18935780/2950e0fa-8597-11e6-9d0c-d5437e8e4941.png width="530"/>
</p>
<p align = "center">
Figure 4: Perf module
</p>

Requirements
------------

* pip packages listed in [requirements.txt](https://github.com/zyluo/PAT/blob/ansible_role/requirements.txt).

```bash
python3.8 -m venv ansible-venv
source ansible-venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r https://raw.githubusercontent.com/zyluo/PAT/ansible_role/requirements.txt
```

Role Variables
--------------

| Name | Default Value | Description |
| ------ | ------ | ------ |
| WORKER_SCRIPT_DIR | /tmp/PAT | Folder where PAT scripts are stored on the worker (absolute path) |
| WORKER_TMP_DIR | /tmp/PAT_TMP | Folder where PAT data will be stored on the worker (absolute path) |
| CMD_SCRIPT | sleep 30 | Replace this value with either the path to a script or the actual command line that launches the job. |
| PRE_EXEC_DELAY | 0 | Delays before running the job, while the system is monitored |
| POST_EXEC_DELAY | 0 | Delays after running the job, while the system is monitored |
| SAMPLE_RATE | 1 | Interval to collect metric from the system under test in seconds, please set this number to 3-5 seconds to avoid data overload for long running jobs |
| INSTRUMENTS | cpustat memstat netstat iostat vmstat jvms perf | List of instruments to be used in the analysis. Available instruments: cpustat memstat netstat iostat vmstat jvms perf |

Example Playbook
----------------

* Create playbook directory

```bash
mkdir PAT
cd PAT
```

* Define PAT role in `requirements.yml` file

```yml
---
roles:
  - src: https://github.com/zyluo/PAT.git
    scm: git
    version: ansible_role
```

* Configure PAT variables in `site.yml` playbook

```yml
---
- name: Monitor system performance and usage activity for all hosts
  hosts: all
  vars_files:
    - roles/PAT/vars/config.yml

  roles:
    - role: PAT
      vars:
        SAMPLE_RATE: 3
        INSTRUMENTS: "cpustat memstat"
        CMD_PATH: sleep 30
```

* List worker nodes in a `inventory` file. Find other parameters to customize your ssh connection in [the official document](https://docs.ansible.com/ansible/latest/user_guide/intro_inventory.html#connecting-to-hosts-behavioral-inventory-parameters)

```yml
hostname01
hostname02
hostname03

[all:vars]
ansible_ssh_user=username
ansible_ssh_private_key_file=/path/to/private_key
```

* Dependencies installation and playbook run

```bash
ansible-galaxy install --roles-path roles/ --role-file requirements.yml
ansible-galaxy collection install ansible.posix
ansible-galaxy collection install community.general
ansible-playbook -i inventory site.yml
```

* Once the job is done, all the data is collected and copied to the `results` directory, under the `[JOB_ID]` folder.

License
-------

BSD 3-clause License

Author Information
------------------

For questions regardng tool contact
- Olasoji Denloy at olasoji.denloye@intel.com
- Yingqi (Lucy) Lu at yingqi.lu@intel.com
- Eric Kaczmarek at eric.kaczmarek@intel.com
- Sammy Nah at sammy.nah@intel.com

Appendix
--------

### A. ARCHITECTURE OVERVIEW:

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

### B. TROUBLESHOOTING ISSUES:
> /usr/lib64/python2.7/site-packages/matplotlib/__init__.py:1005: UserWarning:  This call to matplotlib.use() has no effect
> because the the backend has already been chosen;
> matplotlib.use() must be called *before* pylab, matplotlib.pyplot, or matplotlib.backends is imported for the first time.

`pip install --upgrade numpy scipy matplotlib` will upgrade Python libraries and solve the error

### C. CONFIGURATION:

**config.xml** is the file where you make all postprocess configuration changes. Below instructions are dedicated to that file.
- Before you modify anything in configuration file, make sure your data are stored in directories (each data node in separate directory). Most likely your data are in a format of `<hostname>:<port>`
- Make changes in config.xml file that suit your needs. Between the tag `<source></source>` specify the path to the directory that contains PAT data. By default it is a directory where your `<hostname>:<port>` data are located (for most cases this will be an instruments directory in your PAT-RESULT folder. In this case the path will be of the form `/foo/bar/instruments/`).
- You may eliminate node(s) if you do not want to do any calculations on that node(s). To do that between the tag `<exclude-node></exclude-node>` specify the name of the node(s) that you want to discard. The exclude-node entry should match the value under 'hostname' in files within the node-name directory. This node will be excluded while computing averages across all nodes. Otherwise further actions are not required. If you wish to do calculations on all nodes then leave everything in default settings. 
- You are also able to turn on or off detailed graphs and averaged graphs by modifying the config.xml file. By default only averaged graphs will be printed and excel file will contain all 4 metric outputs.
- During runtime a different config.xml file can be given as a command line argument to the pat-post-process script. It will override the default config.xml file.

### D. OUTPUT:
- Postprocess data will be located at the same path that was entered in the tag `<source></source>`. Copy the entire results directory to a Windows machine, navigate to the `instruments` directory and then open the provided spreadsheet. In Excel 2010 and above press **Ctrl+q** to launch the macros that will import all the data, draw tables and plot graphs.
- Output can be customized by editing the config.xml file. The pdf and excel contains only the data specified in the config.xml file.
- The output consists of 2 files – a pdf file that gives a visual representation of data, and an excel file that contains RAW data along with macros to draw the relevant charts.
