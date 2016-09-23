#!/usr/bin/python2
#
# Copyright (c) 2015, Intel Corporation
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# 
#     * Redistributions of source code must retain the above copyright notice,
#       this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of Intel Corporation nor the names of its contributors
#       may be used to endorse or promote products derived from this software
#       without specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


import os
import cpu_module
import disk_module
import memory_module
import net_module
import perf_module
import xml.etree.ElementTree as ET
import sys
import time


#==================== Python version =========================
cur_python_version = sys.version_info
#platform.python_version()
#cur_version[:2] will give you first two elements of the list
if cur_python_version[:2] >= (2,7):
    found = True
    print "---- You currently have Python " + sys.version
else:
    found = False
    print "---- Error, You need python 2.7.x+ and currently you have " + sys.version

#====================== matplotlib ===========================
try:
    import matplotlib #must have here. If not then matplotlib.__version__ not recognize
    from matplotlib.backends.backend_pdf import PdfPages
    cur_matplotlib_version = matplotlib.__version__.replace(".", "")
    req_matplotlib_version = '1.3.1'.replace(".", "")
    if cur_matplotlib_version.isdigit() >= req_matplotlib_version.isdigit():
        found = True
        print "---- You currently have matplotlib " + matplotlib.__version__
    else:   
        found = False
        print "---- Error, You need matplotlib 1.3.1+ and currently you have " + matplotlib.__version__

except ImportError: #handle exception
    found = False
    print '---- missing dependency - python-matplotlib' + \
        '\n---- Please install python module - matplotlib'

#===================== xlsxwriter ===========================        
try:
    import xlsxwriter
    cur_xlsxwriter_version = xlsxwriter.__version__.replace(".", "")
    req_xlsxwriter_version = '0.6.3'.replace(".", "")
    if cur_xlsxwriter_version.isdigit() >= req_xlsxwriter_version.isdigit():
        found = True
        print "---- You currently have xlsxwriter " + xlsxwriter.__version__
    else:   
        found = False
        print "---- Error, You need xlsxwriter 0.6.3+ and currently you have " + xlsxwriter.__version__

except ImportError: #handle exception
    found = False
    print '---- missing dependency - python-xlsxwriter' + \
        '\n---- Please install python module - xlsxwriter'

#==================== starting stript =====================
if found is False:
    print '---- Must use Python 2.7 or grater' + \
    '\n---- dependencies missing - exiting script >>>>>>>>>>>'
    sys.exit()
else:
    print '---- You have all required dependencies' + \
    '\n---- PAT-post-processing script will start automatically'


def get_dirpaths(directory):
    """function to get paths of folders of all nodes"""
    dir_paths = []
    for root, directories, files in os.walk(directory):
        if directories:
            dir_paths = directories
            break
    for index, dir_folder in enumerate(dir_paths):
        # generate full path for all folders
        dir_paths[index] = os.path.join(directory, str(dir_folder))
    return sorted(dir_paths)


class Node(object):
    """One node object per node. Contains cpu, memory, net, disk, and perf objects"""
    file_names = ['/cpustat', '/iostat', '/netstat', '/perfout', '/memstat']
    corrupt = False

    def __init__(self, node_folder_path):
        self.node_folder_path = node_folder_path
        self.node_file_paths = self.get_file_paths(self.node_folder_path)
        self.corrupt = Node.corrupt

        # file at location [0] is cpustat file
        if os.path.isfile(self.node_file_paths[0]) and os.stat(
                self.node_file_paths[0]).st_size != 0:
            self.cpu_obj = cpu_module.Cpu(self.node_file_paths[0])
            self.has_cpu = True
        else:
            print 'file missing or empty: ', self.node_file_paths[0]
            self.has_cpu = False

        # file at location [1] is disk file
        if os.path.isfile(self.node_file_paths[1]) and os.stat(
                self.node_file_paths[1]).st_size != 0:
            self.disk_obj = disk_module.Disk(self.node_file_paths[1])
        else:
            print 'file missing or empty: ', self.node_file_paths[1]

        # file at location [2] is net file
        if os.path.isfile(self.node_file_paths[2]) and os.stat(
                self.node_file_paths[2]).st_size != 0:
            self.net_obj = net_module.Net(self.node_file_paths[2])
        else:
            print 'file missing or empty: ', self.node_file_paths[2]

        # file at location [3] is perf file
        if os.path.isfile(self.node_file_paths[3]) and os.stat(
                self.node_file_paths[3]).st_size != 0:
            if self.has_cpu is True:
                self.perf_obj = perf_module.Perf(self.node_file_paths[3],
                                                 self.cpu_obj)
            else:
                self.perf_obj = perf_module.Perf(self.node_file_paths[3],
                                                 None)
        else:
            print 'file missing or empty: ', self.node_file_paths[3]

        # file at location [4] is memory file
        if os.path.isfile(self.node_file_paths[4]) and os.stat(
                self.node_file_paths[4]).st_size != 0:
            self.memory_obj = memory_module.Memory(self.node_file_paths[4])
        else:
            print 'file missing or empty: ', self.node_file_paths[4]

    def get_file_paths(self, node_folder_path):
        """generate file paths for raw files for a node"""
        self.node_folder_path = node_folder_path
        self.file_paths = []
        for self.file_name in Node.file_names:
            self.file_paths.append(self.node_folder_path + self.file_name)
        return self.file_paths


def adjust_timestamps(cluster):
    """Synchronize timetamps accross all nodes"""

    if hasattr(cluster[0], 'cpu_obj'):
        base_timestamp = cluster[0].cpu_obj.time_stamp_array[0]
    elif hasattr(cluster[0], 'disk_obj'):
        base_timestamp = cluster[0].disk_obj.time_stamp_array[0]
    elif hasattr(cluster[0], 'net_obj'):
        base_timestamp = cluster[0].net_obj.time_stamp_array[0]
    elif hasattr(cluster[0], 'perf_obj'):
        base_timestamp = cluster[0].perf_obj.time_stamp_array[0]
    elif hasattr(cluster[0], 'memory_obj'):
        base_timestamp = cluster[0].memory_obj.time_stamp_array[0]

    # calculate lowest timestamp
    for node in cluster:
        if hasattr(node, 'cpu_obj'):
            cpu_timestamp = node.cpu_obj.time_stamp_array[0]
            if cpu_timestamp < base_timestamp:
                base_timestamp = cpu_timestamp
        if hasattr(node, 'disk_obj'):
            disk_timestamp = node.disk_obj.time_stamp_array[0]
            if disk_timestamp < base_timestamp:
                base_timestamp = disk_timestamp
        if hasattr(node, 'net_obj'):
            net_timestamp = node.net_obj.time_stamp_array[0]
            if net_timestamp < base_timestamp:
                base_timestamp = net_timestamp
        if hasattr(node, 'perf_obj'):
            perf_timestamp = node.perf_obj.time_stamp_array[0]
            if perf_timestamp < base_timestamp:
                base_timestamp = perf_timestamp
        if hasattr(node, 'memory_obj'):
            memory_timestamp = node.memory_obj.time_stamp_array[0]
            if memory_timestamp < base_timestamp:
                base_timestamp = memory_timestamp

    for node in cluster:
        if hasattr(node, 'cpu_obj'):
            for index, row in enumerate(node.cpu_obj.time_stamp_array):
                node.cpu_obj.time_stamp_array[index] = row - base_timestamp
        if hasattr(node, 'disk_obj'):
            for index, row in enumerate(node.disk_obj.ts_sum):
                node.disk_obj.ts_sum[index] = row - base_timestamp
        if hasattr(node, 'net_obj'):
            for index, row in enumerate(node.net_obj.ts_sum):
                node.net_obj.ts_sum[index] = row - base_timestamp
        if hasattr(node, 'perf_obj'):
            for index, row in enumerate(node.perf_obj.time_stamp_array):
                node.perf_obj.time_stamp_array[index] = row - base_timestamp
        if hasattr(node, 'memory_obj'):
            for index, row in enumerate(node.memory_obj.time_stamp_array):
                node.memory_obj.time_stamp_array[index] = row - base_timestamp

def make_cluster(result_path):
    """
    Creates a new Node object for each node
    This will also load all the Nodes with the correct data from raw data files
    """
    cluster = []
    node_folder_paths = get_dirpaths(result_path)
    # generate a new node for each folder and add it to the cluster
    for node_path in node_folder_paths:
        new_node = Node(node_path)
        cluster.append(new_node)
    # synchronize timetamps accross all nodes
    adjust_timestamps(cluster)
    return cluster


def generate_output(cluster):
    config_file = None
    if len(sys.argv) > 1:
        config_file = sys.argv[1]
    else:
        config_file = 'config.xml'

    if config_file is not None:
        config = ET.parse(config_file)
        root = config.getroot()
        en_pdf = root[0].get('enable')
        en_avg_cpu = root[0].find('average-cpu').text
        en_avg_disk = root[0].find('average-disk').text
        en_avg_net = root[0].find('average-net').text
        en_avg_memory = root[0].find('average-memory').text
        en_avg_perf = root[0].find('average-perf').text
        en_all_cpu = root[0].find('all-nodes-cpu').text
        en_all_disk = root[0].find('all-nodes-disk').text
        en_all_net = root[0].find('all-nodes-net').text
        en_all_perf = root[0].find('all-nodes-perf').text
        en_all_memory = root[0].find('all-nodes-memory').text
        en_xl = root[1].get('enable')
        en_cpu_xl = root[1].find('cpu').text
        en_disk_xl = root[1].find('disk').text
        en_net_xl = root[1].find('net').text
        en_perf_xl = root[1].find('perf').text
        en_memory_xl = root[1].find('memory').text
        en_csv = root[2].get('enable')
        en_cpu_csv = root[2].find('csv-cpu').text
        en_disk_csv = root[2].find('csv-disk').text
        en_net_csv = root[2].find('csv-net').text
        en_perf_csv = root[2].find('csv-perf').text
        en_memory_csv = root[2].find('csv-memory').text
        result_path = root[3].text
        name_node = root[4].text

    if en_pdf == 'yes':
        print "----Rendering pdf", time.ctime(), "----"

        # global pdf file that will contain all charts
        pp = PdfPages(result_path + '/PAT-Result.pdf')

        # print average cpu utilization graph to pdf
        if en_avg_cpu == 'yes' or en_avg_cpu == 'Yes':
            cpu_data = cpu_module.get_avg_data(cluster, name_node)
            if cpu_data is not None:
                cpu_module.plot_graph(cpu_data, pp, 'All-nodes average')

        # print average disk utilization graph to pdf
        if en_avg_disk == 'yes' or en_avg_disk == 'Yes':
            disk_data = disk_module.get_avg_data(cluster, name_node)
            if disk_data is not None:
                disk_module.plot_graph(disk_data, pp, 'All-nodes average')

        # print average network utilization graph to pdf
        if en_avg_net == 'yes' or en_avg_net == 'Yes':
            net_data = net_module.get_avg_data(cluster, name_node)
            if net_data is not None:
                net_module.plot_graph(net_data, pp, "All-nodes average")

        if en_avg_perf == 'yes' or en_avg_perf == 'Yes':
            perf_avg_data = perf_module.get_avg_data(cluster, name_node)
            if perf_avg_data[0] is not None:
                perf_list = [perf_avg_data[0][0], perf_avg_data[1][0],
                             perf_avg_data[2][0]]
                perf_module.plot_pie_chart(perf_avg_data[0], pp,
                                           "Avg Application", None, perf_list,
                                           "avg", cluster, name_node)
                perf_module.plot_pie_chart(perf_avg_data[1], pp, "Avg Module",
                                           None, perf_list,
                                           "avg", cluster, name_node)
                perf_module.plot_pie_chart(perf_avg_data[2], pp,
                                           "Avg Function", None, perf_list,
                                           "avg", cluster, name_node)

        # print average memory utilization graph to pdf
        if en_avg_memory == 'yes' or en_avg_memory == 'Yes':
            memory_data = memory_module.get_avg_data(cluster, name_node)
            if memory_data is not None:
                memory_module.plot_graph(memory_data, pp, "All-nodes average")

        # print data graphs for each individual node
        for node in cluster:
            if en_all_cpu == 'yes' or en_all_cpu == 'Yes':
                if hasattr(node, 'cpu_obj'):
                    node_name = node.cpu_obj.data_array[1][0]
                    cpu_module.plot_graph(
                        node.cpu_obj.avg_array, pp, str(node_name))
            if en_all_disk == 'yes' or en_all_disk == 'Yes':
                if hasattr(node, 'disk_obj'):
                    node_name = node.disk_obj.data_array[1][0]
                    disk_module.plot_graph(
                        node.disk_obj.avg_array, pp, str(node_name))
            if en_all_net == 'yes' or en_all_net == 'Yes':
                node_name = node.net_obj.data_array[1][0]
                net_module.plot_graph(
                    node.net_obj.avg_array, pp, str(node_name))
            if en_all_perf == 'yes' or en_all_perf == 'Yes':
                if hasattr(node, 'perf_obj'):
                    node_name = node.perf_obj.data_array[1][0]
                    metric_list = [node.perf_obj.application_array[0],
                                   node.perf_obj.module_array[0],
                                   node.perf_obj.function_array[0]]
                    perf_module.plot_pie_chart(node.perf_obj.application_array,
                                               pp, str(node_name) +
                                               " Application",
                                               node.perf_obj.avg_array,
                                               metric_list, "node", None, None)
                    perf_module.plot_pie_chart(node.perf_obj.module_array,
                                               pp, str(node_name)+" Module",
                                               node.perf_obj.avg_array,
                                               metric_list, "node", None, None)
                    perf_module.plot_pie_chart(node.perf_obj.function_array,
                                               pp, str(node_name)+" Function",
                                               node.perf_obj.avg_array,
                                               metric_list, "node", None, None)
            if en_all_memory == 'yes' or en_all_memory == 'Yes':
                node_name = node.memory_obj.data_array[1][0]
                memory_module.plot_graph(
                    node.memory_obj.avg_array, pp, str(node_name))
        print "----Finished pdf", time.ctime(), "----"
        pp.close()

    if en_xl == 'yes':
        print "----Generating Excel", time.ctime(), "----"
        wb = xlsxwriter.Workbook(result_path + '/PAT-Result.xlsm')
        print "----Generating CSV", time.ctime(), "----"
        csv_path_cpu = result_path + "/CPU.csv"
        csv_path_disk = result_path + "/DISK.csv"
        csv_path_net = result_path + "/NET.csv"
        csv_path_perf = result_path + "/PERF.csv"
        csv_path_memory = result_path + "/MEMORY.csv"

        # generate excel file
        if en_cpu_xl == 'yes' or en_cpu_xl == 'Yes':
            cpu_module.write_excel(cluster, wb)
        if en_disk_xl == 'yes' or en_disk_xl == 'Yes':
            disk_module.write_excel(cluster, wb)
        if en_net_xl == 'yes' or en_net_xl == 'Yes':
            net_module.write_excel(cluster, wb)
        if en_perf_xl == 'yes' or en_perf_xl == 'Yes':
            perf_module.write_excel(cluster, wb)
        if en_memory_xl == 'yes' or en_memory_xl == 'Yes':
            memory_module.write_excel(cluster, wb)
        # generate CSV file
        if en_cpu_csv == 'yes' or en_cpu_csv == 'Yes':
            cpu_module.csv_writer(cluster, csv_path_cpu)
        if en_disk_csv == 'yes' or en_disk_csv == 'Yes':
            disk_module.csv_writer(cluster, csv_path_disk)
        if en_net_csv == 'yes' or en_net_csv == 'Yes':
            net_module.csv_writer(cluster, csv_path_net)
        if en_perf_csv == 'yes' or en_perf_csv == 'Yes':
            perf_module.csv_writer(cluster, csv_path_perf)
        if en_memory_csv == 'yes' or en_memory_csv == 'Yes':
            memory_module.csv_writer(cluster, csv_path_memory)
        wb.add_vba_project('./vbaProject.bin')
        print "----Finished Excel", time.ctime(), "----"
        print "----Finished CSV", time.ctime(), "----"
        wb.close()


def main():
    if len(sys.argv) > 1:
        config_file = sys.argv[1]
    else:
        config_file = 'config.xml'

    config = ET.parse(config_file)
    root = config.getroot()
    print "Started processing on", time.ctime()
    cluster = make_cluster(root[3].text)
    print "Completed processing on", time.ctime()
    generate_output(cluster)


if __name__ == '__main__':
    main()
