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


import matplotlib as mpl
mpl.use('Agg')
from pat_abc import pat_base
import matplotlib.pyplot as plt
import numpy as np
# import time
from textwrap import fill
import csv


class Perf(pat_base):

    def __init__(self, file_path, cpu_obj):
        """Read and parse the data and store it in self.data_array"""
        self.data_array = self.get_data(file_path)
        # normalize to cpu utilization
        if cpu_obj is not None:
            self.normalize(cpu_obj)
        self.title = ['Hostname', 'TimeStamp', 'Cycles', 'Application',
                      'Module', 'Kernel', 'Function']
        self.data_array.insert(0, self.title)
        self.application = []
        self.module = []
        self.function = []
        self.time_stamp_array = []
        self.cycle = []
        self.avg_array = []
        self.application_array, self.module_array, \
            self.function_array = self.extract_data()

    def extract_data(self):
        self.ts_index = self.data_array[0].index("TimeStamp")
        self.app_index = self.data_array[0].index("Application")
        self.module_index = self.data_array[0].index("Module")
        self.function_index = self.data_array[0].index("Function")
        self.cycle_index = self.data_array[0].index("Cycles")
        del self.data_array[0]

        # separate the data in to different lists
        for self.row in self.data_array:
            try:
                self.temp_ts = int(self.row[self.ts_index])
                self.time_stamp_array.append(self.temp_ts)
                self.application.append(self.row[self.app_index])
                self.module.append(self.row[self.module_index])
                self.function.append(self.row[self.function_index])
                self.cycle.append(float(self.row[self.cycle_index]))
            except ValueError:
                pass
        # avg_array contains all lists
        self.avg_array.append(self.time_stamp_array)
        self.avg_array.append(self.application)
        self.avg_array.append(self.module)
        self.avg_array.append(self.function)
        self.avg_array.append(self.cycle)
        # calculate the sum of cycles for each value of each metric
        self.avg_application, self.app_cycle = self.extract_metric(
            self.application)
        self.avg_module, self.mod_cycle = self.extract_metric(self.module)
        self.avg_function, self.func_cycle = self.extract_metric(self.function)
        self.data_array.insert(0, self.title)
        # sort the data and return top 5 of each metric
        return sort_perf(self.avg_application, self.app_cycle,
                         self.avg_module, self.mod_cycle, self.avg_function,
                         self.func_cycle)

    def normalize(self, cpu_obj):
        """Look up %idle inside the cpu for the same timestamp and normalize \
        sum of cycles"""
        time_stamp_set = set(cpu_obj.time_stamp_array)
        idle_dict = {}
        for time_stamp in time_stamp_set:
            index = cpu_obj.time_stamp_array.index(time_stamp)
            idle_dict[time_stamp] = cpu_obj.idle_percent[index]
        for self.ind, self.row in enumerate(self.data_array):
            try:
                self.ts = int(self.row[1])
                idle_cpu = idle_dict.get(self.ts)
                if idle_cpu is not None:
                    self.data_array[self.ind][2] = float(self.row[2]) * (
                        100 - idle_cpu) / 100
            except ValueError:
                    pass

    def extract_metric(self, application):
        """Calculate the % sum of cycles for each metric"""
        metric = {}
        for index in range(len(application)-1):
            app = metric.get(application[index])
            if app is not None:
                app += self.cycle[index]
                metric.update(dict([(application[index], app)]))
            else:
                metric.update(dict([(application[index], self.cycle[index])]))
        avg_application = metric.keys()
        app_cycle = metric.values()
        avg_application = [x for y, x in sorted(zip(app_cycle,
                                                avg_application))]
        app_cycle = sorted(app_cycle)
        return avg_application, app_cycle


def get_avg_data(cluster, name_node):
    """Calculate % sum of cycles consumed for application, module, function\
    """
    application = []
    app_dict = {}
    function = []
    module = []
    mod_dict = {}
    app_cycle = []
    func_cycle = []
    func_dict = {}
    mod_cycle = []
    index = 0
    node_count = 0

    # calculate sum of cycles for each application in all nodes
    for node in cluster:
        if hasattr(node, 'perf_obj'):
            if node.perf_obj.data_array[1][0] != name_node:
                node_count += 1
                for index in range(len(node.perf_obj.application)-1):
                    cyc = app_dict.get(node.perf_obj.application[index])
                    if cyc is not None:
                        cyc += node.perf_obj.cycle[index]
                        app_dict.update(dict([(node.perf_obj.application[
                            index], cyc)]))
                    else:
                        app_dict.update(dict([(node.perf_obj.application[
                            index], node.perf_obj.cycle[index])]))
    application = app_dict.keys()
    app_cycle = app_dict.values()
    if application:
        application = [x for y, x in sorted(zip(app_cycle, application))]
        app_cycle = sorted(app_cycle)

    # calculate sum of cycles for each module in all nodes
    for node in cluster:
        if hasattr(node, 'perf_obj'):
            if node.perf_obj.data_array[1][0] != name_node:
                for index in range(len(node.perf_obj.module)-1):
                    cyc = mod_dict.get(node.perf_obj.module[index])
                    if cyc is not None:
                        cyc += node.perf_obj.cycle[index]
                        mod_dict.update(dict([(node.perf_obj.module[index],
                                        cyc)]))
                    else:
                        mod_dict.update(dict([(node.perf_obj.module[index],
                                             node.perf_obj.cycle[index])]))
    module = mod_dict.keys()
    mod_cycle = mod_dict.values()
    if module:
        module = [x for y, x in sorted(zip(mod_cycle, module))]
        mod_cycle = sorted(mod_cycle)

    # calculate sum of cycles for each function in all nodes
    for node in cluster:
        if hasattr(node, 'perf_obj'):
            if node.perf_obj.data_array[1][0] != name_node:
                for index in range(len(node.perf_obj.function)-1):
                    cyc = func_dict.get(node.perf_obj.function[index])
                    if cyc is not None:
                        cyc += node.perf_obj.cycle[index]
                        func_dict.update(dict([(node.perf_obj.function[index],
                                         cyc)]))
                    else:
                        func_dict.update(dict([(node.perf_obj.function[index],
                                              node.perf_obj.cycle[index])]))
    function = func_dict.keys()
    func_cycle = func_dict.values()
    if function:
        function = [x for y, x in sorted(zip(func_cycle, function))]
        func_cycle = sorted(func_cycle)

    if application == [] and function == [] and module == []:
        return None, None, None
    else:
        # sort and return top 5 values for each application, module and func
        application_array, module_array, function_array = sort_perf(
            application, app_cycle, module, mod_cycle, function, func_cycle)
        return [application_array, module_array, function_array]


def sort_perf(application, app_cycle, module, mod_cycle, function, func_cycle):
    """Sort the data lists and return the top 5 elements for application,\
    module and function"""
    # sort application array and separate the top 5 elements
    application = [x for y, x in sorted(zip(app_cycle, application),
                                        reverse=True)]
    app_cycle = sorted(app_cycle, reverse=True)
    if sum(app_cycle) != 0:
        app_total = 100 / sum(app_cycle)
    app_cycle = app_cycle[0:5]
    for index, entry in enumerate(app_cycle):
        app_cycle[index] = entry * app_total
    application = application[0:5]
    application.append('other')
    app_cycle.append(100 - sum(app_cycle))
    application_array = [application, app_cycle]

    # sort module array and separate the top 5 elements
    module = [x for y, x in sorted(zip(mod_cycle, module),
                                   reverse=True)]
    mod_cycle = sorted(mod_cycle, reverse=True)
    if sum(mod_cycle) != 0:
        mod_total = 100 / sum(mod_cycle)
    mod_cycle = mod_cycle[0:5]
    for index, entry in enumerate(mod_cycle):
        mod_cycle[index] = entry * mod_total
    module = module[0:5]
    module.append('other')
    mod_cycle.append(100 - sum(mod_cycle))
    module_array = [module, mod_cycle]

    # sort function array and separate the top 5 elements
    function = [x for y, x in sorted(zip(func_cycle, function),
                                     reverse=True)]
    func_cycle = sorted(func_cycle, reverse=True)
    if sum(func_cycle) != 0:
        func_total = 100 / sum(func_cycle)
    func_cycle = func_cycle[0:5]
    for index, entry in enumerate(func_cycle):
        func_cycle[index] = entry * func_total
    function = function[0:5]
    function.append('other')
    func_cycle.append(100 - sum(func_cycle))
    function_array = [function, func_cycle]
    return application_array, module_array, function_array


def plot_pie_chart(data, pp, graph_title, avg_array, metric_list, mde,
                   cluster, name_node):
    """plot all graphs related to perf"""
    labels1 = data[0]
    sizes = data[1]
    fig = plt.figure(figsize=(8.27, 11.69))
    ax = fig.add_subplot(311)
    colors = ['lightcoral', 'orange', 'gold', 'yellowgreen', 'darkgreen',
              'grey']
    patches, texts = ax.pie(sizes, colors=colors, shadow=True, startangle=90)
    # define labels for legend
    labels = ['{0} - {1:1.2f} %'.format(i[:30], j) for i, j in zip(labels1,
              sizes)]
    plabels = ['{0} - {1:1.2f} %'.format(i, j) for i, j in zip(labels1,
               sizes)]
    pdf_label = ""
    details = ""
    # generate string to be printed on the page
    for label in plabels:
        pdf_label += fill(label, 80) + '\n'
    
    details += '-' * 85 + '\n' + "All-nodes " +  graph_title.split()[0] + ' Hot ' + \
        graph_title.split()[1] + ':-\n' + pdf_label + '-' * 85 + '\n'

    ax.legend(patches, labels, loc='upper right', framealpha=0.7,
              fontsize=7, fancybox=True)
    ax.axis('equal')
    ax.set_title('All-nodes ' + graph_title + ' - perf')
    ax1 = fig.add_subplot(312)
    tpe = graph_title.split()
    # check if we need to print node or avg
    if mde == "node":
        tpe = graph_title.split()
        plot_time_graphs(avg_array, pp, metric_list, tpe[1], ax1)
    elif mde == 'avg':
        get_avg_time_graphs(cluster, metric_list, pp, name_node, tpe[1], ax1)
    fig.text(0.05, 1.1, 'normalized to CPU utilization', fontsize=10)
    fig.text(0.975, 0.025, pp.get_pagecount()+1, fontsize=10)
    ax3 = fig.add_subplot(313)
    ax3.text(0.0, 0.9, details, fontsize=11, horizontalalignment='left',
             verticalalignment='top')
    ax3.axis('off')
    plt.tight_layout()
    pp.savefig(dpi=200)
    plt.clf()
    plt.close()


def get_avg_time_graphs(cluster, perf_list, pp, name_node, tpe, ax):
    """Join lists from different nodes and call the plot_time_graphs"""
    app_array = []
    mod_array = []
    func_array = []
    cycle_array = []
    time_stamp_array = []
    node_count = 0
    # join list for different nodes
    for node in cluster:
        if hasattr(node, 'perf_obj'):
            if node.perf_obj.data_array[1][0] != name_node:
                node_count += 1
                app_array += node.perf_obj.application
                mod_array += node.perf_obj.module
                func_array += node.perf_obj.function
                cycle_array += node.perf_obj.cycle
                time_stamp_array += node.perf_obj.time_stamp_array

    # get the average of the cycles
    cycle_array = np.asarray(cycle_array) / node_count
    data_array = [time_stamp_array, app_array, mod_array, func_array,
                  cycle_array]
    plot_time_graphs(data_array, pp, perf_list, tpe, ax)


def plot_time_graphs(data_array, pp, metric_list, tpe, ax):
    """separate the metric and call the appropriate plotter function"""
    time_stamp_array = data_array[0]
    cycle = data_array[4]
    # check type of graph to be printed
    if tpe == 'Application':
        # print metric_list[0]
        plotter(ax, data_array[1], time_stamp_array, cycle, metric_list[0],
                'application')
    if tpe == 'Module':
        # print metric_list[1]
        plotter(ax, data_array[2], time_stamp_array, cycle, metric_list[1],
                'module')
    if tpe == 'Function':
        # print metric_list[2]
        plotter(ax, data_array[3], time_stamp_array, cycle, metric_list[2],
                'function')


def plotter(ax, application, time_stamp_array, cycle, metric_list, m_type):
    """calculate the % of different metrics and plot it on a graph"""
    # generate graph for each of the top 5 metrics passed to the plotter
    max_res = 0
    for metric in metric_list:
        app_ts = []
        app_ts_dic = {}
        app_cycle = []
        # generate list for plotting cycles vs timestamp for each application
        # in metric list
        for index in range(len(time_stamp_array)):
            if metric == application[index] and metric != 'other':
                cyc = app_ts_dic.get(time_stamp_array[index])
                if cyc is not None:
                    cyc += cycle[index]
                    app_ts_dic.update(dict([(time_stamp_array[index], cyc)]))
                else:
                    app_ts_dic.update(dict([(time_stamp_array[index],
                                      cycle[index])]))
        app_ts = app_ts_dic.keys()
        app_cycle = app_ts_dic.values()
        # sort and get the average over a duration if we have a large number
        # of timestamps
        if app_ts:
            app_cycle = [x for y, x in sorted(zip(app_ts, app_cycle))]
            app_ts = sorted(app_ts)
            data, res = get_data_for_graph([app_ts, app_cycle])
            app_ts = data[0]
            app_cycle = data[1]
            ax.plot(app_ts, app_cycle, label=" "+metric[:25], rasterized=False)
            max_res = max(max_res, res)

    ax_caption = "resolution - 1:" + str(max_res)
    ax.text(0.03, 0.98, ax_caption, fontsize=9, transform=ax.transAxes,
            horizontalalignment='left', verticalalignment='top')
    ax.grid(True)
    ax.set_ylabel('% Cycles')
    ax.set_xlabel('time(s)')
    ax.legend(framealpha=0.5, fontsize=7)


def get_data_for_graph(data_array):
    """Average the data over every few samples so that it can be displayed on\
    the graph
    """
    time_stamp_array = []
    for entry in data_array[0]:
        time_stamp_array.append(float(entry))
    x = int(round(len(time_stamp_array) / 500))
    if x > 1:
        new_ts = time_stamp_array[0::x]
        cycle = []
        for entry in data_array[1]:
            cycle.append(float(entry))
        new_cycle = get_graph_mean(x, cycle)
        return [new_ts, new_cycle], x
    else:
        return data_array, 1


def get_graph_mean(x, data):
    """function that actually calculates the average over x samples for \
    different data"""
    ind = -1
    new_data = []
    for index, entry in enumerate(data):
        if index % x == 0:
            if ind >= 0:
                new_data[ind] /= x
            ind += 1
            new_data.append(entry)
        else:
            new_data[ind] += entry

    return new_data


def write_excel(cluster, wb):
    """create excel sheet and insert the data into the sheet"""
    ws_perf = wb.add_worksheet('perf')
    row_offset = 0
    col_offset = 0
    row_data = 0
    col_data = 0
    flag = 0
    num = 0
    span = 1
    fill_value = -1
    tmp_new = []
    count = 0
    
    # fill the excel table
    for node in cluster:
        if hasattr(node, 'perf_obj'):
            node_data = node.perf_obj.data_array
            
            tmp = [elem[1] for elem in node_data]
            variable = str(tmp[1])

            for i in tmp[2:]: #start from 3rd element in the tmp list
                  if i == variable:
                     span+=1
                  else:
                     break
            #enumerate starts from 0
            tmp_new.append('TimeStamp')
            for index,elem in enumerate(tmp[1:]):
                if index % span != 0:
                   count += 1
                else:
                   fill_value += 1
                   count = 0
                tmp_new.append(str(fill_value))

            for index, elem in enumerate(node_data):
                   elem[1] = tmp_new[index]

            tmp_new[:] = []
            span = 1

            for row in range(row_offset, (row_offset + len(node_data))):
                for col in range(col_offset,
                                 (col_offset + len(node_data[0]))):
                    if isinstance(node_data[row_data][col_data], float):
                        ws_perf.write(row, col, node_data[row_data][col_data])
                    else:
                        if node_data[row_data][col_data].replace(
                                ".", "", 1).isdigit():
                            ws_perf.write(row, col, float(
                                node_data[row_data][col_data]))
                        else:
                            ws_perf.write(row, col, node_data[row_data][
                                                                col_data])
                    col_data += 1
                col_data = 0
                row_data += 1

                # create set flag to create new sheet if rows exceed 1 million
                if row >= 1048576:
                    flag = 1
                    num += 1
                    rem_row = row_offset + len(node_data) - row - 1
                    break
            if flag == 0:
                row_data = 0
                row_offset = row_offset + len(node_data)

            # create new sheet if rows exceed 1 million rows
            if flag == 1:
                # ws_perf = wb.add_worksheet('perf' + str(num))
                col_offset += 9
                ws_perf.write(0, col_offset, 'Hostname')
                ws_perf.write(0, col_offset+1, 'TimeStamp')
                ws_perf.write(0, col_offset+2, 'Cycles')
                ws_perf.write(0, col_offset+3, 'Application')
                ws_perf.write(0, col_offset+4, 'Module')
                ws_perf.write(0, col_offset+5, 'Kernel')
                ws_perf.write(0, col_offset+6, 'Function')
                flag = 0
                row_offset = 0
                for row in range(0+1, rem_row+1):
                    for col in range(col_offset,
                                     (col_offset + len(node_data[0]))):
                        if isinstance(node_data[row_data][col_data], float):
                            ws_perf.write(row, col, node_data[row_data][
                                col_data])
                        else:
                            if node_data[row_data][col_data].replace(
                                    ".", "", 1).isdigit():
                                ws_perf.write(row, col, float(
                                    node_data[row_data][col_data]))
                            else:
                                ws_perf.write(row, col, node_data[row_data][
                                                                    col_data])
                        col_data += 1
                    col_data = 0
                    row_data += 1
                row_data = 0
                row_offset = rem_row+1


def csv_writer(cluster, csv_path_perf):  
    """write data to a CSV file path""" 

    csv_file = open(csv_path_perf, "wb")

    for node in cluster:
        if hasattr(node, 'perf_obj'):
            node_data = node.perf_obj.data_array                    
              
            writer = csv.writer(csv_file, delimiter=',')
            for line in node_data:
                   writer.writerow(line)           
    

