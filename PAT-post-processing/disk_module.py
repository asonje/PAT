#!/usr/bin/python3
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
from pat_abc import pat_base
import csv


class Disk(pat_base):
    """Contains all functions related to disk. Also contains data_array which \
    stores the data internally for further processing"""

    def __init__(self, file_path):
        """initialize disk object by parsing raw dat and storing it in a \
        structure internally"""
        self.data_array = self.get_data(file_path)
        self.time_stamp_array = []
        self.ts_sum = []
        self.avg_array = self.extract_data()

    def extract_data(self):
        """Extract useful information from the parsed raw data and store it \
        in an array avg_array[]"""
        self.avg_array = []
        self.title_line = self.data_array[0]
        self.rps_index = self.title_line.index("r/s")
        self.wps_index = self.title_line.index("w/s")
        self.ts_index = self.title_line.index("TimeStamp")
        self.rkbps_index = self.title_line.index("rkB/s")
        self.wkbps_index = self.title_line.index("wkB/s")
        self.r_await_index = self.title_line.index("r_await")
        self.w_await_index = self.title_line.index("w_await")
        self.util_index = self.title_line.index("%util")
        del self.data_array[0]

        self.time_stamp_array = []
        for self.row in self.data_array:
            self.time_stamp_array.append((int(self.row[self.ts_index])))

        # extract rps metric
        self.rps = []
        self.wps = []
        self.rkbps = []
        self.wkbps = []
        self.r_await = []
        self.w_await = []
        self.util = []
        for self.row in self.data_array:
            self.rps.append(float(self.row[self.rps_index]))
            self.wps.append(float(self.row[self.wps_index]))
            self.rkbps.append(float(self.row[self.rkbps_index]))
            self.wkbps.append(float(self.row[self.wkbps_index]))
            self.r_await.append(float(self.row[self.r_await_index]))
            self.w_await.append(float(self.row[self.w_await_index]))
            self.util.append(float(self.row[self.util_index]))

        self.ts_sum = []
        self.avg_ind = 0
        for self.index, self.row in enumerate(self.time_stamp_array):
            if (self.index != 0):
                if (self.time_stamp_array[self.index] ==
                        self.time_stamp_array[self.index-1]):
                    pass
                else:
                    self.ts_sum.append(self.time_stamp_array[self.index])
                    self.avg_ind += 1
            elif (self.index == 0):
                self.ts_sum.append(self.time_stamp_array[self.index])
        self.avg_array.append(self.ts_sum)

        # calculate sum writes and reads to all disks
        self.wps_sum = self.get_sum(self.wps_index, self.wps)
        self.avg_array.append(self.wps_sum)

        self.rps_sum = self.get_sum(self.rps_index, self.rps)
        self.avg_array.append(self.rps_sum)

        self.wkbps_sum = self.get_sum(self.wkbps_index, self.wkbps)
        self.avg_array.append(self.wkbps_sum)

        self.rkbps_sum = self.get_sum(self.rkbps_index, self.rkbps)
        self.avg_array.append(self.rkbps_sum)

        self.r_await_sum = self.get_sum(self.r_await_index, self.r_await)
        self.avg_array.append(self.r_await_sum)

        self.w_await_sum = self.get_sum(self.w_await_index, self.w_await)
        self.avg_array.append(self.w_await_sum)

        self.util_sum = self.get_sum(self.util_index, self.util)
        self.avg_array.append(self.util_sum)

        self.data_array.insert(0, self.title_line)
        return self.avg_array

    def get_sum(self, index, data):
        """add the reads and writes for all disks"""
        self.sum_array = []
        self.avg_ind = 0
        for self.index, self.row in enumerate(self.time_stamp_array):
            if (self.index != 0):
                if (self.time_stamp_array[self.index] ==
                        self.time_stamp_array[self.index-1]):
                    self.sum_array[self.avg_ind] = self.sum_array[
                                        self.avg_ind] + data[self.index]
                else:
                    self.sum_array.append(data[self.index])
                    self.avg_ind += 1
            elif (self.index == 0):
                self.sum_array.append(data[self.index])
        return self.sum_array


def get_avg_data(cluster, name_node):
    node_count = 0
    wps_dic = {}
    rps_dic = {}
    wkbps_dic = {}
    rkbps_dic = {}
    r_await_dic = {}
    w_await_dic = {}
    util_dic = {}
    count_dic = {}

    for node in cluster:
        if hasattr(node, 'disk_obj'):
            if node.disk_obj.data_array[1][0] != name_node:
                node_count += 1
                for index in range(len(node.disk_obj.ts_sum)-1):
                    wps = wps_dic.get(node.disk_obj.ts_sum[index])
                    if wps is not None:
                        wps += node.disk_obj.avg_array[1][index]
                        wps_dic.update(dict([(node.disk_obj.ts_sum[index],
                                       wps)]))
                        rps = rps_dic.get(node.disk_obj.ts_sum[index])
                        rps += node.disk_obj.avg_array[2][index]
                        rps_dic.update(dict([(node.disk_obj.ts_sum[index],
                                            rps)]))
                        wkbps = wkbps_dic.get(node.disk_obj.ts_sum[index])
                        wkbps += node.disk_obj.avg_array[3][index]
                        wkbps_dic.update(dict([(node.disk_obj.ts_sum[index],
                                                wkbps)]))
                        rkbps = rkbps_dic.get(node.disk_obj.ts_sum[index])
                        rkbps += node.disk_obj.avg_array[4][index]
                        rkbps_dic.update(dict([(node.disk_obj.ts_sum[index],
                                                rkbps)]))
                        r_await = r_await_dic.get(node.disk_obj.ts_sum[index])
                        r_await += node.disk_obj.avg_array[5][index]
                        r_await_dic.update(dict([(node.disk_obj.ts_sum[index],
                                                r_await)]))
                        w_await = w_await_dic.get(node.disk_obj.ts_sum[index])
                        w_await += node.disk_obj.avg_array[6][index]
                        w_await_dic.update(dict([(node.disk_obj.ts_sum[index],
                                                w_await)]))
                        util = util_dic.get(node.disk_obj.ts_sum[index])
                        util += node.disk_obj.avg_array[7][index]
                        util_dic.update(dict([(node.disk_obj.ts_sum[index],
                                                util)]))
                        cnt = count_dic.get(node.disk_obj.ts_sum[index])
                        cnt += 1
                        count_dic.update(dict([(node.disk_obj.ts_sum[
                            index], cnt)]))
                    else:
                        wps_dic.update(dict([(node.disk_obj.ts_sum[
                            index], node.disk_obj.avg_array[1][index])]))
                        rps_dic.update(dict([(node.disk_obj.ts_sum[
                            index], node.disk_obj.avg_array[2][index])]))
                        wkbps_dic.update(dict([(node.disk_obj.ts_sum[
                            index], node.disk_obj.avg_array[3][index])]))
                        rkbps_dic.update(dict([(node.disk_obj.ts_sum[
                            index], node.disk_obj.avg_array[4][index])]))
                        r_await_dic.update(dict([(node.disk_obj.ts_sum[
                            index], node.disk_obj.avg_array[5][index])]))
                        w_await_dic.update(dict([(node.disk_obj.ts_sum[
                            index], node.disk_obj.avg_array[6][index])]))
                        util_dic.update(dict([(node.disk_obj.ts_sum[
                            index], node.disk_obj.avg_array[7][index])]))
                        count_dic.update(dict([(node.disk_obj.ts_sum[
                            index], 1)]))

    if node_count != 0:
        ts = rps_dic.keys()
        rps = rps_dic.values()
        wps = wps_dic.values()
        rkbps = rkbps_dic.values()
        wkbps = wkbps_dic.values()
        r_await = r_await_dic.values()
        w_await = w_await_dic.values()
        util = util_dic.values()
        count = count_dic.values()
        rps = [x for y, x in sorted(zip(ts, rps))]
        wps = [x for y, x in sorted(zip(ts, wps))]
        rkbps = [x for y, x in sorted(zip(ts, rkbps))]
        wkbps = [x for y, x in sorted(zip(ts, wkbps))]
        r_await = [x for y, x in sorted(zip(ts, r_await))]
        w_await = [x for y, x in sorted(zip(ts, w_await))]
        util = [x for y, x in sorted(zip(ts, util))]
        count = [x for y, x in sorted(zip(ts, count))]
        ts = sorted(ts)

        for index, row in enumerate(wps):
            wps[index] = row / count[index]
        for index, row in enumerate(rps):
            rps[index] = row / count[index]
        for index, row in enumerate(wkbps):
            wkbps[index] = row / count[index]
        for index, row in enumerate(rkbps):
            rkbps[index] = row / count[index]
        for index, row in enumerate(r_await):
            r_await[index] = row / count[index]
        for index, row in enumerate(w_await):
            w_await[index] = row / count[index]
        for index, row in enumerate(util):
            util[index] = row / count[index]
        avg_array = [ts, wps, rps, wkbps, rkbps, r_await, w_await, util]
        return avg_array
    else:
        return None


def plot_graph(data, pp, graph_title):
    """plot all graphs related to disk"""

    data, res = get_data_for_graph(data)
    time_stamp_array = []
    for entry in data[0]:
        time_stamp_array.append(float(entry))

    fig = plt.figure()
    ax = fig.add_subplot(111)

    if res < 1:
        res = 1
    fig_caption = "resolution - 1:" + str(res)
    fig.text(0.14, 0.89, fig_caption, fontsize=10,
             horizontalalignment='left', verticalalignment='top')

    x = time_stamp_array
    # plot graphs
    ax.plot(x, data[1], label='w/s',
            color='#800000', alpha=0.9, linewidth=0.5, rasterized=True)
    ax.plot(x, data[2], label='r/s',
            color='#00297A', alpha=0.9, linewidth=0.5, rasterized=True)
    ax.fill_between(x, 0, data[1], facecolor='#800000',
                    alpha=0.45, linewidth=0.01, rasterized=True)
    ax.fill_between(x, 0, data[2], rasterized=True,
                    facecolor='#00297A', alpha=0.45, linewidth=0.01)
    ax.legend(framealpha=0.5)
    x1, x2, y1, y2 = ax.axis()
    # set axes
    ax.axis((min(x), max(x), 0, y2))
    # set xlabel, ylabel and title
    ax.set_ylabel('requests/second')
    ax.set_xlabel('time(s)')
    ax.set_title(graph_title + ' Disk IO requests')
    ax.grid(True)
    fig.text(0.95, 0.05, pp.get_pagecount()+1, fontsize=10)
    pp.savefig(dpi=200)
    plt.clf()
    plt.close()

    # define new figure
    fig = plt.figure()
    ax = fig.add_subplot(111)
    fig_caption = "resolution - 1:" + str(res)
    fig.text(0.14, 0.89, fig_caption, fontsize=10,
             horizontalalignment='left', verticalalignment='top')
    # plot graphs
    ax.plot(x, data[3], label='write kB/s',
            color='#800000', alpha=0.9, linewidth=0.5, rasterized=True)
    ax.plot(x, data[4], label='read kB/s',
            color='#00297A', alpha=0.9, linewidth=0.5, rasterized=True)
    ax.fill_between(x, 0, data[3], facecolor='#800000',
                    alpha=0.45, linewidth=0.01, rasterized=True)
    ax.fill_between(x, 0, data[4], rasterized=True,
                    facecolor='#00297A', alpha=0.45, linewidth=0.01)

    ax.legend(framealpha=0.5)
    x1, x2, y1, y2 = ax.axis()
    # set axes
    ax.axis((min(x), max(x), 0, y2))
    # set xlabel, ylabel and title
    ax.set_ylabel('Bandwidth(kB/s)')
    ax.set_xlabel('time(s)')
    ax.set_title(graph_title + ' Disk Bandwidth')
    ax.grid(True)
    fig.text(0.95, 0.05, pp.get_pagecount()+1, fontsize=10)
    pp.savefig(dpi=200)
    plt.clf()
    plt.close()

    fig = plt.figure()
    ax = fig.add_subplot(111)
    fig_caption = "resolution - 1:" + str(res)
    fig.text(0.14, 0.89, fig_caption, fontsize=10,
             horizontalalignment='left', verticalalignment='top')
    # plot graphs
    ax.plot(x, data[5], label='r_await',
            color='#00297A', alpha=0.9, linewidth=0.5, rasterized=True)
    ax.plot(x, data[5], label='w_await',
            color='#004f7a', alpha=0.9, linewidth=0.5, rasterized=True)
    ax.plot(x, data[6], label='util',
            color='#800000', alpha=0.9, linewidth=0.5, rasterized=True)
    ax.fill_between(x, 0, data[5], facecolor='#00297A',
                    alpha=0.45, linewidth=0.01, rasterized=True)
    ax.fill_between(x, 0, data[6], rasterized=True,
                    facecolor='#800000', alpha=0.45, linewidth=0.01)
    ax.legend(framealpha=0.5)
    x1, x2, y1, y2 = ax.axis()
    ax.axis((min(x), max(x), 0, y2))
    ax.set_ylabel('number of requests')
    ax.set_xlabel('time(s)')
    ax.set_title(graph_title + ' Disk IO latencies')
    ax.grid(True)
    fig.text(0.95, 0.05, pp.get_pagecount()+1, fontsize=10)
    pp.savefig(dpi=200)
    plt.clf()
    plt.close()


def get_data_for_graph(data_array):

    time_stamp_array = []
    for entry in data_array[0]:
        time_stamp_array.append(int(entry))

    x = int(round(len(time_stamp_array) / 650))
    if x > 1:
        new_ts = time_stamp_array[0::x]
        wps = []
        for entry in data_array[1]:
            wps.append(float(entry))
        new_wps = get_graph_mean(x, wps)
        rps = []
        for entry in data_array[2]:
            rps.append(float(entry))
        new_rps = get_graph_mean(x, rps)
        wkbps = []
        for entry in data_array[3]:
            wkbps.append(float(entry))
        new_wkbps = get_graph_mean(x, wkbps)
        rkbps = []
        for entry in data_array[4]:
            rkbps.append(float(entry))
        new_rkbps = get_graph_mean(x, rkbps)
        r_await = []
        for entry in data_array[5]:
            r_await.append(float(entry))
        new_r_await = get_graph_mean(x, r_await)
        w_await = []
        for entry in data_array[6]:
            w_await.append(float(entry))
        new_w_await = get_graph_mean(x, w_await)
        util = []
        for entry in data_array[7]:
            util.append(float(entry))
        new_util = get_graph_mean(x, util)
        return [new_ts, new_wps, new_rps, new_wkbps, new_rkbps, new_r_await, new_w_await,
                new_util], x
    else:
        return data_array, x


def get_graph_mean(x, data):
    ind = -1
    max_val = 0
    new_data = []
    for index, entry in enumerate(data):
        if index % x == 0:
            max_val = 0
            ind += 1
            new_data.append(entry)
        else:
            max_val = max(entry, max_val)
            if max_val > new_data[ind]:
                new_data[ind] = max_val

    return new_data


def write_excel(cluster, wb):
    """create excel sheet and insert the data into the sheet"""
    ws_disk = wb.add_worksheet('disk')
    row_offset = 0
    col_offset = 0
    row_data = 0
    col_data = 0
    span = 1
    fill_value = -1
    tmp_new = []
    count = 0

    for node in cluster:
        if hasattr(node, 'disk_obj'):
            node_data = node.disk_obj.data_array
            
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
                    if node_data[row_data][col_data].replace(
                            ".", "", 1).isdigit():
                        ws_disk.write(row, col, float(
                            node_data[row_data][col_data]))
                    else:
                        ws_disk.write(row, col, node_data[row_data][col_data])
                    col_data += 1
                col_data = 0
                row_data += 1

            row_data = 0
            row_offset = row_offset + len(node_data)

def csv_writer(cluster, csv_path_disk):  
    """write data to a CSV file path""" 

    csv_file = open(csv_path_disk, "w")
    for node in cluster:
        if hasattr(node, 'disk_obj'):
            node_data = node.disk_obj.data_array
            for row in node_data:
                for item in row:
                    if item.replace(".", "", 1).isdigit():
                        item = float(item)        
                   
    for node in cluster:
        if hasattr(node, 'disk_obj'):
            node_data = node.disk_obj.data_array                    
              
            writer = csv.writer(csv_file, delimiter=',')
            for line in node_data:
                   writer.writerow(line)    
