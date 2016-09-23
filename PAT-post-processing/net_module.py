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
from pat_abc import pat_base
import csv


class Net(pat_base):

    def __init__(self, file_path):
        """Read and parse the data and store it in self.data_array"""
        self.data_array = self.get_data(file_path)
        self.remove_lo()
        self.time_stamp_array = []
        self.ts_sum = []
        self.avg_array = self.extract_data()

    def extract_data(self):
        """Extract useful information from the parsed raw data and store it \
        in an array avg_array[]"""
        self.avg_array = []
        self.title_line = self.data_array[0]
        self.rxkbps_index = self.data_array[0].index("rxkB/s")
        self.txkbps_index = self.data_array[0].index("txkB/s")
        self.ts_index = self.data_array[0].index("TimeStamp")
        del self.data_array[0]

        # time stamps
        self.time_stamp_array = []
        for self.row in self.data_array:
            self.time_stamp_array.append((int(self.row[self.ts_index])))

        # extract rxkbps metric
        self.rxkbps = []
        for self.row in self.data_array:
            self.rxkbps.append(float(self.row[self.rxkbps_index]))

        # extract txkbps metric
        self.txkbps = []
        for self.index, self.row in enumerate(self.data_array):
            self.txkbps.append(float(self.row[self.txkbps_index]))

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

        self.txkbps_sum = []
        self.avg_ind = 0
        for self.index, self.row in enumerate(self.time_stamp_array):
            if (self.index != 0):
                if (self.time_stamp_array[self.index] ==
                        self.time_stamp_array[self.index-1]):
                    self.txkbps_sum[self.avg_ind] = self.txkbps_sum[
                                        self.avg_ind] + self.txkbps[self.index]
                else:
                    self.txkbps_sum.append(self.txkbps[self.index])
                    self.avg_ind += 1
            elif (self.index == 0):
                self.txkbps_sum.append(self.txkbps[self.index])
        self.avg_array.append(self.txkbps_sum)

        self.rxkbps_sum = []
        self.avg_ind = 0
        for self.index, self.row in enumerate(self.time_stamp_array):
            if (self.index != 0):
                if (self.time_stamp_array[self.index] ==
                        self.time_stamp_array[self.index-1]):
                    self.rxkbps_sum[self.avg_ind] = self.rxkbps_sum[
                                        self.avg_ind] + self.rxkbps[self.index]
                else:
                    self.rxkbps_sum.append(self.rxkbps[self.index])
                    self.avg_ind += 1
            elif (self.index == 0):
                self.rxkbps_sum.append(self.rxkbps[self.index])
        self.avg_array.append(self.rxkbps_sum)

        self.data_array.insert(0, self.title_line)

        return self.avg_array

    def remove_lo(self):
        for index, row in enumerate(self.data_array):
            if 'lo' in row:
                del self.data_array[index]


def get_avg_data(cluster, name_node):
    node_count = 0
    txkbps_dic = {}
    rxkbps_dic = {}
    count_dic = {}

    for node in cluster:
        if hasattr(node, 'net_obj'):
            if node.net_obj.data_array[1][0] != name_node:
                node_count += 1
                for index in range(len(node.net_obj.ts_sum)-1):
                    txkbps = txkbps_dic.get(node.net_obj.ts_sum[index])
                    if txkbps is not None:
                        txkbps += node.net_obj.avg_array[1][index]
                        txkbps_dic.update(dict([(node.net_obj.ts_sum[index],
                                                 txkbps)]))
                        rxkbps = rxkbps_dic.get(node.net_obj.ts_sum[index])
                        rxkbps += node.net_obj.avg_array[2][index]
                        rxkbps_dic.update(dict([(node.net_obj.ts_sum[index],
                                                 rxkbps)]))
                        cnt = count_dic.get(node.net_obj.ts_sum[index])
                        cnt += 1
                        count_dic.update(dict([(node.net_obj.ts_sum[
                            index], cnt)]))
                    else:
                        txkbps_dic.update(dict([(node.net_obj.ts_sum[
                            index], node.net_obj.avg_array[1][index])]))
                        rxkbps_dic.update(dict([(node.net_obj.ts_sum[
                            index], node.net_obj.avg_array[2][index])]))
                        count_dic.update(dict([(node.net_obj.ts_sum[
                            index], 1)]))

    if node_count != 0:
        ts = txkbps_dic.keys()
        txkbps = txkbps_dic.values()
        rxkbps = rxkbps_dic.values()
        count = count_dic.values()
        txkbps = [x for y, x in sorted(zip(ts, txkbps))]
        rxkbps = [x for y, x in sorted(zip(ts, rxkbps))]
        count = [x for y, x in sorted(zip(ts, count))]
        ts = sorted(ts)
        for index, row in enumerate(txkbps):
            txkbps[index] = row / count[index]
        for index, row in enumerate(rxkbps):
            rxkbps[index] = row / count[index]
        avg_array = [ts, txkbps, rxkbps]
        return avg_array
    else:
        return None


def plot_graph(data, pp, graph_title):
    """plot all graphs related to net"""

    data, res = get_data_for_graph(data)
    time_stamp_array = []
    for entry in data[0]:
        time_stamp_array.append(float(entry))

    x = time_stamp_array

    fig = plt.figure()
    ax = fig.add_subplot(111)
    if res < 1:
        res = 1
    fig_caption = "resolution - 1:" + str(res)
    fig.text(0.14, 0.89, fig_caption, fontsize=10,
             horizontalalignment='left', verticalalignment='top')

    # plot graphs
    ax.plot(x, data[2], label='rxkB/s',
            color='#00297A', alpha=0.9, linewidth=0.5, rasterized=True)
    ax.plot(x, data[1], label='txkB/s',
            color='#800000', alpha=0.9, linewidth=0.5, rasterized=True)
    ax.fill_between(x, 0, data[1], facecolor='#800000',
                    alpha=0.45, linewidth=0.01, rasterized=True)
    ax.fill_between(x, 0, data[2], rasterized=True,
                    facecolor='#00297A', alpha=0.45, linewidth=0.01)

    ax.legend(framealpha=0.5)
    x1, x2, y1, y2 = ax.axis()
    # set axes
    ax.axis((min(x), max(x), 0, y2))
    # set xlabel, ylabel and title
    ax.set_ylabel('Bandwidth(kB/s)')
    ax.set_xlabel('time(s)')
    ax.set_title(graph_title + ' Network IO')
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
        txkbps = []
        for entry in data_array[1]:
            txkbps.append(float(entry))
        new_txkbps = get_graph_mean(x, txkbps)

        rxkbps = []
        for entry in data_array[2]:
            rxkbps.append(float(entry))
        new_rxkbps = get_graph_mean(x, rxkbps)

        return [new_ts, new_txkbps, new_rxkbps], x
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
    ws_net = wb.add_worksheet('net')
    row_offset = 0
    col_offset = 0
    row_data = 0
    col_data = 0
    span = 1
    fill_value = -1
    tmp_new = []
    count = 0

    for node in cluster:
        if hasattr(node, 'net_obj'):
            node_data = node.net_obj.data_array
            
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
                        ws_net.write(row, col, float(
                            node_data[row_data][col_data]))
                    else:
                        ws_net.write(row, col, node_data[row_data][col_data])
                    col_data += 1
                col_data = 0
                row_data += 1
            row_data = 0
            row_offset = row_offset + len(node_data)


def csv_writer(cluster, csv_path_net):
    """write data to a CSV file path""" 

    csv_file = open(csv_path_net, "wb")
    for node in cluster:
        if hasattr(node, 'net_obj'):
            node_data = node.net_obj.data_array
            for row in node_data:
                for item in row:
                    if item.replace(".", "", 1).isdigit():
                        item = float(item)        
                   
    for node in cluster:
        if hasattr(node, 'net_obj'):
            node_data = node.net_obj.data_array                    
              
            writer = csv.writer(csv_file, delimiter=',')
            for line in node_data:
                   writer.writerow(line)  
