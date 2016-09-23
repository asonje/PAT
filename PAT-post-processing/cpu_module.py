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
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from pat_abc import pat_base
import csv


class Cpu(pat_base):
    """Contains all functions related to cpu. Also contains data_array which \
    stores the data internally for further processing"""

    def __init__(self, file_path):
        """initialize cpu object by parsing raw data and storing it in a \
        structure internally"""
        self.data_array = self.get_data(file_path)
        self.time_stamp_array = []
        self.avg_array = self.extract_data()

    def extract_data(self):
        """Extract useful information from the parsed raw data and store it \
        in an array avg_array[]"""
        self.avg_array = []
        self.title_line = self.data_array[0]

        # get column number of each metric
        self.ts_index = self.title_line.index("TimeStamp")
        self.user_index = self.title_line.index("%user")
        self.nice_index = self.title_line.index("%nice")
        self.system_index = self.title_line.index("%system")
        self.iowait_index = self.title_line.index("%iowait")
        self.steal_index = self.title_line.index("%steal")
        self.idle_index = self.title_line.index("%idle")

        del self.data_array[0]

        # generate approximate time stamps
        self.time_stamp_array = []
        self.user_percent = []
        self.nice_percent = []
        self.system_percent = []
        self.iowait_percent = []
        self.steal_percent = []
        self.idle_percent = []

        for self.row in self.data_array:
            self.time_stamp_array.append((int(self.row[self.ts_index])))
            self.user_percent.append(float(self.row[self.user_index]))
            self.nice_percent.append(float(self.row[self.nice_index]))
            self.system_percent.append(float(self.row[self.system_index]))
            self.iowait_percent.append(float(self.row[self.iowait_index]))
            self.steal_percent.append(float(self.row[self.steal_index]))
            self.idle_percent.append(float(self.row[self.idle_index]))

        self.avg_array.append(self.time_stamp_array)
        self.avg_array.append(self.user_percent)
        self.avg_array.append(self.nice_percent)
        self.avg_array.append(self.system_percent)
        self.avg_array.append(self.iowait_percent)
        self.avg_array.append(self.steal_percent)
        self.avg_array.append(self.idle_percent)

        self.data_array.insert(0, self.title_line)
        return self.avg_array


def get_avg_data(cluster, name_node):
    node_count = 0
    user_dic = {}
    nice_dic = {}
    system_dic = {}
    iowait_dic = {}
    steal_dic = {}
    idle_dic = {}
    count_dic = {}

    for node in cluster:
        if hasattr(node, 'cpu_obj'):
            if node.cpu_obj.data_array[1][0] != name_node:
                node_count += 1
                for index in range(len(node.cpu_obj.time_stamp_array)-1):
                    usr = user_dic.get(node.cpu_obj.time_stamp_array[index])
                    if usr is not None:
                        usr += node.cpu_obj.avg_array[1][index]
                        user_dic.update(dict([(node.cpu_obj.time_stamp_array[
                            index], usr)]))
                        nce = nice_dic.get(node.cpu_obj.time_stamp_array[
                            index])
                        nce += node.cpu_obj.avg_array[2][index]
                        nice_dic.update(dict([(node.cpu_obj.time_stamp_array[
                            index], nce)]))
                        syst = system_dic.get(node.cpu_obj.time_stamp_array[
                            index])
                        syst += node.cpu_obj.avg_array[3][index]
                        system_dic.update(dict([(node.cpu_obj.time_stamp_array[
                            index], syst)]))
                        iow = iowait_dic.get(node.cpu_obj.time_stamp_array[
                            index])
                        iow += node.cpu_obj.avg_array[4][index]
                        iowait_dic.update(dict([(node.cpu_obj.time_stamp_array[
                            index], iow)]))
                        stl = steal_dic.get(node.cpu_obj.time_stamp_array[
                            index])
                        stl += node.cpu_obj.avg_array[5][index]
                        steal_dic.update(dict([(node.cpu_obj.time_stamp_array[
                            index], stl)]))
                        idl = idle_dic.get(node.cpu_obj.time_stamp_array[
                            index])
                        idl += node.cpu_obj.avg_array[6][index]
                        idle_dic.update(dict([(node.cpu_obj.time_stamp_array[
                            index], idl)]))
                        cnt = count_dic.get(node.cpu_obj.time_stamp_array[
                            index])
                        cnt += 1
                        count_dic.update(dict([(node.cpu_obj.time_stamp_array[
                            index], cnt)]))
                    else:
                        user_dic.update(dict([(node.cpu_obj.time_stamp_array[
                            index], node.cpu_obj.avg_array[1][index])]))
                        nice_dic.update(dict([(node.cpu_obj.time_stamp_array[
                            index], node.cpu_obj.avg_array[2][index])]))
                        system_dic.update(dict([(node.cpu_obj.time_stamp_array[
                            index], node.cpu_obj.avg_array[3][index])]))
                        iowait_dic.update(dict([(node.cpu_obj.time_stamp_array[
                            index], node.cpu_obj.avg_array[4][index])]))
                        steal_dic.update(dict([(node.cpu_obj.time_stamp_array[
                            index], node.cpu_obj.avg_array[5][index])]))
                        idle_dic.update(dict([(node.cpu_obj.time_stamp_array[
                            index], node.cpu_obj.avg_array[6][index])]))
                        count_dic.update(dict([(node.cpu_obj.time_stamp_array[
                            index], 1)]))

    if node_count != 0:
        ts = user_dic.keys()
        user = user_dic.values()
        nice = nice_dic.values()
        system = system_dic.values()
        iowait = iowait_dic.values()
        steal = steal_dic.values()
        idle = idle_dic.values()
        count = count_dic.values()
        user = [x for y, x in sorted(zip(ts, user))]
        nice = [x for y, x in sorted(zip(ts, nice))]
        system = [x for y, x in sorted(zip(ts, system))]
        iowait = [x for y, x in sorted(zip(ts, iowait))]
        steal = [x for y, x in sorted(zip(ts, steal))]
        idle = [x for y, x in sorted(zip(ts, idle))]
        count = [x for y, x in sorted(zip(ts, count))]
        ts = sorted(ts)

        for index, row in enumerate(user):
            user[index] = row / count[index]
        for index, row in enumerate(nice):
            nice[index] = row / count[index]
        for index, row in enumerate(system):
            system[index] = row / count[index]
        for index, row in enumerate(iowait):
            iowait[index] = row / count[index]
        for index, row in enumerate(steal):
            steal[index] = row / count[index]
        for index, row in enumerate(idle):
            idle[index] = row / count[index]
        avg_array = [ts, user, nice, system, iowait, steal, idle]
        return avg_array
    else:
        return None


def plot_graph(data_array, pp, graph_title):
    """plot all cpu related graphs"""

    # data_array1 = data_array
    data_array, res = get_data_for_graph(data_array)
    time_stamp_array = []
    for entry in data_array[0]:
        time_stamp_array.append(int(entry))

    # extract user percent metric
    user_percent = []
    for entry in data_array[1]:
        user_percent.append(float(entry))

    # extrac nice percent metric and stack it
    nice_percent = []
    for index, entry in enumerate(data_array[2]):
        nice_percent.append(
            float(entry) + user_percent[index])

    # extract system percent metric and stack it
    system_percent = []
    for index, entry in enumerate(data_array[3]):
        system_percent.append(
            float(entry) + nice_percent[index])

    # extract iowait percent metric and stack it
    iowait_percent = []
    for index, entry in enumerate(data_array[4]):
        iowait_percent.append(
            float(entry) + system_percent[index])

    # extract steal percent metric and stack it
    steal_percent = []
    for index, entry in enumerate(data_array[5]):
        steal_percent.append(
            float(entry) + iowait_percent[index])

    # extract idle percent metric and stack it
    idle_percent = []
    for index, entry in enumerate(data_array[6]):
        idle_percent.append(
            float(entry) + steal_percent[index])

    x = time_stamp_array

    # new figure
    fig = plt.figure()
    ax1 = fig.add_subplot(111)
    if res < 1:
        res = 1
    fig_caption = "resolution - 1:" + str(res)
    fig.text(0.14, 0.89, fig_caption, fontsize=10,
             horizontalalignment='left', verticalalignment='top')
    # plots graphs

    ax1.plot(time_stamp_array, nice_percent, label='nice',
             color='#338533', alpha=0.5, linewidth=0.4, rasterized=True)
    ax1.plot(time_stamp_array, steal_percent, label='steal',
             color='#663300', alpha=0.5, linewidth=0.4, rasterized=True)
    ax1.plot(time_stamp_array, idle_percent, label='idle',
             color='#a35019', alpha=0.5, linewidth=0.4, rasterized=True)
    ax1.plot(time_stamp_array, iowait_percent, label='iowait',
             color='#47008f', alpha=0.5, linewidth=0.4, rasterized=True)
    ax1.plot(time_stamp_array, system_percent, label='system',
             color='#a00000', alpha=0.5, linewidth=0.4, rasterized=True)
    ax1.plot(time_stamp_array, user_percent, label='user',
             color='#194d99', alpha=0.5, linewidth=0.4, rasterized=True)
    ax1.axis((0, max(x), 0, 105))

    # generate legend for the graph
    user_patch = mpatches.Patch(color='#194d99', label='user', alpha=0.45)
    nice_patch = mpatches.Patch(color='#338533', label='nice', alpha=0.45)
    system_patch = mpatches.Patch(color='#a00000', label='system', alpha=0.45)
    iowait_patch = mpatches.Patch(color='#47008f', label='iowait', alpha=0.45)
    steal_patch = mpatches.Patch(color='#663300', label='steal', alpha=0.45)
    # idle_patch = mpatches.Patch(color='#a35019', label='idle', alpha=0.45)
    ax1.legend([user_patch, nice_patch, system_patch, iowait_patch,
                steal_patch], ['user', 'nice', 'system', 'iowait',
                               'steal'], prop={'size': 10},
               framealpha=0.5)

    # fill in the graphs
    ax1.fill_between(x, user_percent, nice_percent, rasterized=True,
                     facecolor='#338533', alpha=0.45, linewidth=0.2)
    ax1.fill_between(x, nice_percent, system_percent, rasterized=True,
                     facecolor='#a00000', alpha=0.45, linewidth=0.2)
    ax1.fill_between(x, system_percent, iowait_percent, rasterized=True,
                     facecolor='#47008f', alpha=0.45, linewidth=0.2)
    ax1.fill_between(x, iowait_percent, steal_percent, rasterized=True,
                     facecolor='#663300', alpha=0.45, linewidth=0.2)
    # ax1.fill_between(x, steal_percent, idle_percent, rasterized=True,
    #                  facecolor='#a35019', alpha=0.45, linewidth=0.2)
    ax1.fill_between(x, 0, user_percent, facecolor='#194d99', rasterized=True,
                     alpha=0.45, linewidth=0.5)
    ax1.set_ylabel('%Utilization')
    ax1.set_xlabel('time(s)')
    ax1.set_title(graph_title + ' cpu utilization')
    ax1.grid(True)
    fig.text(0.95, 0.05, pp.get_pagecount()+1, fontsize=10)
    pp.savefig(dpi=200)
    plt.clf()
    plt.close()

    # fig = plt.figure()
    # plot histogram for average and individual cpu metrics
    ax = plt.subplot2grid((3, 2), (0, 0), rowspan=3)
    plot_stats(ax, steal_percent, pp, graph_title + ' TOTAL')

    ax1 = plt.subplot2grid((3, 2), (0, 1))
    plot_stats(ax1, user_percent, pp, graph_title + ' USER')

    system_percent = []
    for row in data_array[3]:
        system_percent.append(row)
    ax2 = plt.subplot2grid((3, 2), (1, 1))
    plot_stats(ax2, system_percent, pp, graph_title + ' SYSTEM')

    iowait_percent = []
    for row in data_array[4]:
        iowait_percent.append(float(row))
    ax3 = plt.subplot2grid((3, 2), (2, 1))
    plot_stats(ax3, iowait_percent, pp, graph_title + ' IOWAIT')

    plt.tight_layout()
    ax3.text(1.03, -0.4, pp.get_pagecount()+1, fontsize=10,
             transform=ax3.transAxes)
    pp.savefig(dpi=200)
    plt.clf()
    plt.close()


def plot_stats(ax, local_data_array, pp, title):
    """plot histogram for cpu metrics"""
    per_count = [0.0 for i in range(10)]
    for row in local_data_array:
        if row <= 10.0:
            per_count[0] += 1
        elif row > 10.0 and row <= 20:
            per_count[1] += 1
        elif row > 20.0 and row <= 30:
            per_count[2] += 1
        elif row > 30.0 and row <= 40:
            per_count[3] += 1
        elif row > 40.0 and row <= 50:
            per_count[4] += 1
        elif row > 50.0 and row <= 60:
            per_count[5] += 1
        elif row > 60.0 and row <= 70:
            per_count[6] += 1
        elif row > 70.0 and row <= 80:
            per_count[7] += 1
        elif row > 80.0 and row <= 90:
            per_count[8] += 1
        elif row > 90.0 and row <= 100:
            per_count[9] += 1

    np.asarray(per_count)
    per_count_total = np.sum(per_count)
    new_per_count = (per_count / per_count_total) * 100
    x = [i for i in range(10)]
    ax.bar(x, new_per_count, color='r', alpha=0.55, rasterized=True)
    ax.set_title(title + ' histogram')
    ax.set_xlabel('%utilization')
    ax.set_ylabel('%time')
    ax.grid(True)
    for index, row in enumerate(x):
        x[index] = row + 0.9
    ax.set_xticks(x)
    ax.set_xticklabels(('10', '20', '30', '40', '50', '60', '70', '80',
                        '90', '100'))
    x1, x2, y1, y2 = ax.axis()
    ax.axis((0, 10, 0, 100))


def get_data_for_graph(data_array):

    time_stamp_array = []
    for entry in data_array[0]:
        time_stamp_array.append(float(entry))

    x = int(round(len(time_stamp_array) / 700))

    if x > 1:
        new_ts = time_stamp_array[0::x]

        user_percent = []
        for entry in data_array[1]:
            user_percent.append(float(entry))
        new_user = get_graph_mean(x, user_percent)

        # extract nice percent metric and stack it
        nice_percent = []
        for entry in data_array[2]:
            nice_percent.append(float(entry))
        new_nice = get_graph_mean(x, nice_percent)

        # extract system percent metric and stack it
        system_percent = []
        for entry in data_array[3]:
            system_percent.append(float(entry))
        new_system = get_graph_mean(x, system_percent)

        # extract iowait percent metric and stack it
        iowait_percent = []
        for entry in data_array[4]:
            iowait_percent.append(float(entry))
        new_iowait = get_graph_mean(x, iowait_percent)

        # extract steal percent metric and stack it
        steal_percent = []
        for entry in data_array[5]:
            steal_percent.append(float(entry))
        new_steal = get_graph_mean(x, steal_percent)

        # extract idle percent metric and stack it
        idle_percent = []
        for entry in data_array[6]:
            idle_percent.append(float(entry))
        new_idle = get_graph_mean(x, idle_percent)

        return [new_ts, new_user, new_nice, new_system, new_iowait, new_steal,
                new_idle], x
    else:
        return data_array, x


def get_graph_mean(x, data):
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
    ws_cpu = wb.add_worksheet('cpu')
    row_offset = 0
    col_offset = 0
    row_data = 0
    col_data = 0
    span = 1
    fill_value = -1
    tmp_new = []
    count = 0
    
    for node in cluster:
        if hasattr(node, 'cpu_obj'):
            node_data = node.cpu_obj.data_array
             
            tmp = [elem[1] for elem in node_data]
            #print str(tmp)
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
                for col in range(col_offset, (col_offset + len(node_data[0]))):
                    if node_data[row_data][col_data].replace(
                            ".", "", 1).isdigit():
                        ws_cpu.write(row, col, float(
                            node_data[row_data][col_data]))
                    else:
                        ws_cpu.write(row, col, node_data[row_data][col_data])
                    col_data += 1
                col_data = 0
                row_data += 1
            row_data = 0
            row_offset = row_offset + len(node_data)



def csv_writer(cluster, csv_path_cpu):
    """write data to a CSV file path""" 

    csv_file = open(csv_path_cpu, "wb")
    for node in cluster:
        if hasattr(node, 'cpu_obj'):
            node_data = node.cpu_obj.data_array
            for row in node_data:
                for item in row:
                    if item.replace(".", "", 1).isdigit():
                        item = float(item)        
                    
    for node in cluster:
        if hasattr(node, 'cpu_obj'):
            node_data = node.cpu_obj.data_array                    
              
            writer = csv.writer(csv_file, delimiter=',')
            for line in node_data:
                   writer.writerow(line)    

