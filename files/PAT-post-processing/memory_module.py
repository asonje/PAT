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
from pat_abc import pat_base
import csv


class Memory(pat_base):
    def __init__(self, file_path):
        """Read and parse the data and store it in self.data_array"""
        self.data_array = self.get_data(file_path)
        self.time_stamp_array = []
        self.avg_array = self.extract_data()

    def extract_data(self):
        """Extract useful information from the parsed raw data and store it \
        in an array avg_array[]"""
        self.avg_array = []
        self.title_line = self.data_array[0]
        self.kbmemused_index = self.data_array[0].index("kbmemused")
        self.kbmemfree_index = self.data_array[0].index("kbmemfree")
        self.kbbuffers_index = self.data_array[0].index("kbbuffers")
        self.kbcached_index = self.data_array[0].index("kbcached")
        self.ts_index = self.data_array[0].index("TimeStamp")
        del self.data_array[0]

        # time stamps
        self.time_stamp_array = []
        for self.row in self.data_array:
            self.time_stamp_array.append((int(self.row[self.ts_index])))

        # extract kbmemused metric
        self.kbmemused = []
        for self.row in self.data_array:
            self.kbmemused.append(int(self.row[self.kbmemused_index]))

        # extract kbmemfree metric
        self.kbmemfree = []
        for self.index, self.row in enumerate(self.data_array):
            self.kbmemfree.append(int(self.row[self.kbmemfree_index]))

        # extract kbbuffers metric
        self.kbbuffers = []
        for self.row in self.data_array:
            self.kbbuffers.append(int(self.row[self.kbbuffers_index]))

        # extract kbcached metric
        self.kbcached = []
        for self.index, self.row in enumerate(self.data_array):
            self.kbcached.append(int(self.row[self.kbcached_index]))

        # calculate the application memory utilization metric
        # The application level memory used is the total memory used minus buffers and cached memory
        self.kbappmemused = []
        for self.row in self.data_array:
            self.kbappmemused.append(int(self.row[self.kbmemused_index]) - int(self.row[self.kbbuffers_index]) - int(
                self.row[self.kbcached_index]))

        self.data_array.insert(0, self.title_line)

        self.avg_array.append(self.time_stamp_array)
        self.avg_array.append(self.kbmemfree)
        self.avg_array.append(self.kbmemused)
        self.avg_array.append(self.kbbuffers)
        self.avg_array.append(self.kbcached)
        self.avg_array.append(self.kbappmemused)

        return self.avg_array


def get_avg_data(cluster, name_node):
    node_count = 0
    kbmemfree_dic = {}
    kbmemused_dic = {}
    kbbuffers_dic = {}
    kbcached_dic = {}
    kbappmemused_dic = {}
    count_dic = {}

    for node in cluster:
        if hasattr(node, 'memory_obj'):
            if node.memory_obj.data_array[1][0] != name_node:
                node_count += 1
                for index in range(len(node.memory_obj.time_stamp_array) - 1):
                    kbmemfree = kbmemfree_dic.get(node.memory_obj.time_stamp_array[index])
                    if kbmemfree is not None:
                        kbmemfree += node.memory_obj.avg_array[1][index]
                        kbmemfree_dic.update(dict([(node.memory_obj.time_stamp_array[index],
                                                    kbmemfree)]))
                        kbmemused = kbmemused_dic.get(node.memory_obj.time_stamp_array[index])
                        kbmemused += node.memory_obj.avg_array[2][index]
                        kbmemused_dic.update(dict([(node.memory_obj.time_stamp_array[index],
                                                    kbmemused)]))
                        kbbuffers = kbbuffers_dic.get(node.memory_obj.time_stamp_array[index])
                        kbbuffers += node.memory_obj.avg_array[3][index]
                        kbbuffers_dic.update(dict([(node.memory_obj.time_stamp_array[index],
                                                    kbbuffers)]))
                        kbcached = kbcached_dic.get(node.memory_obj.time_stamp_array[index])
                        kbcached += node.memory_obj.avg_array[4][index]
                        kbcached_dic.update(dict([(node.memory_obj.time_stamp_array[index],
                                                   kbcached)]))
                        kbappmemused = kbappmemused_dic.get(node.memory_obj.time_stamp_array[index])
                        kbappmemused += node.memory_obj.avg_array[5][index]
                        kbappmemused_dic.update(dict([(node.memory_obj.time_stamp_array[index],
                                                       kbappmemused)]))

                        cnt = count_dic.get(node.memory_obj.time_stamp_array[index])
                        cnt += 1
                        count_dic.update(dict([(node.memory_obj.time_stamp_array[
                                                    index], cnt)]))
                    else:
                        kbmemfree_dic.update(dict([(node.memory_obj.time_stamp_array[
                                                        index], node.memory_obj.avg_array[1][index])]))
                        kbmemused_dic.update(dict([(node.memory_obj.time_stamp_array[
                                                        index], node.memory_obj.avg_array[2][index])]))
                        kbbuffers_dic.update(dict([(node.memory_obj.time_stamp_array[
                                                        index], node.memory_obj.avg_array[3][index])]))
                        kbcached_dic.update(dict([(node.memory_obj.time_stamp_array[
                                                       index], node.memory_obj.avg_array[4][index])]))
                        kbappmemused_dic.update(dict([(node.memory_obj.time_stamp_array[
                                                           index], node.memory_obj.avg_array[5][index])]))
                        count_dic.update(dict([(node.memory_obj.time_stamp_array[
                                                    index], 1)]))

    if node_count != 0:
        ts = kbmemfree_dic.keys()
        kbmemfree = kbmemfree_dic.values()
        kbmemused = kbmemused_dic.values()
        kbbuffers = kbbuffers_dic.values()
        kbcached = kbcached_dic.values()
        kbappmemused = kbappmemused_dic.values()
        count = count_dic.values()
        kbmemfree = [x for y, x in sorted(zip(ts, kbmemfree))]
        kbmemused = [x for y, x in sorted(zip(ts, kbmemused))]
        kbbuffers = [x for y, x in sorted(zip(ts, kbbuffers))]
        kbcached = [x for y, x in sorted(zip(ts, kbcached))]
        kbappmemused = [x for y, x in sorted(zip(ts, kbappmemused))]
        count = [x for y, x in sorted(zip(ts, count))]
        ts = sorted(ts)
        for index, row in enumerate(kbmemfree):
            kbmemfree[index] = row / count[index]
        for index, row in enumerate(kbmemused):
            kbmemused[index] = row / count[index]
        for index, row in enumerate(kbbuffers):
            kbbuffers[index] = row / count[index]
        for index, row in enumerate(kbcached):
            kbcached[index] = row / count[index]
        for index, row in enumerate(kbappmemused):
            kbappmemused[index] = row / count[index]
        avg_array = [ts, kbmemfree, kbmemused, kbbuffers, kbcached, kbappmemused]
        return avg_array
    else:
        return None


def plot_graph(data, pp, graph_title):
    """plot all graphs related to memory"""

    data, res = get_data_for_graph(data)
    time_stamp_array = []
    for entry in data[0]:
        time_stamp_array.append(int(entry))

    # extract application level memory used metric
    memory_app_used = []
    for entry in data[5]:
        memory_app_used.append(int(entry))

    # extract memory buffers metric
    memory_buffers = []
    for index, entry in enumerate(data[3]):
        memory_buffers.append(
            int(entry) + memory_app_used[index])

    # extract memory cached metric
    memory_cached = []
    for index, entry in enumerate(data[4]):
        memory_cached.append(
            int(entry) + memory_buffers[index])

    # extract memory free metric
    memory_free = []
    for index, entry in enumerate(data[1]):
        memory_free.append(
            int(entry) + memory_cached[index])

    # x = time_stamp_array

    fig = plt.figure()
    ax = fig.add_subplot(111)
    if res < 1:
        res = 1
    fig_caption = "resolution - 1:" + str(res)
    fig.text(0.14, 0.89, fig_caption, fontsize=10,
             horizontalalignment='left', verticalalignment='top')

    # plot graphs
    ax.plot(time_stamp_array, memory_app_used, label='free',
            color='#194d99', alpha=0.5, linewidth=0.4, rasterized=True)
    ax.plot(time_stamp_array, memory_free, label='free',
            color='#47008f', alpha=0.5, linewidth=0.4, rasterized=True)
    ax.plot(time_stamp_array, memory_buffers, label='buffers',
            color='#a00000', alpha=0.5, linewidth=0.4, rasterized=True)
    ax.plot(time_stamp_array, memory_cached, label='cached',
            color='#663300', alpha=0.5, linewidth=0.4, rasterized=True)

    # generate legend for the graph
    used_patch = mpatches.Patch(color='#194d99', label='used', alpha=0.45)
    free_patch = mpatches.Patch(color='#47008f', label='free', alpha=0.45)
    buffers_patch = mpatches.Patch(color='#a00000', label='buffers', alpha=0.45)
    cached_patch = mpatches.Patch(color='#663300', label='cached', alpha=0.45)
    ax.legend([used_patch, free_patch, buffers_patch, cached_patch], ['used', 'free', 'buffers', 'cached'],
              prop={'size': 10}, framealpha=0.5)

    ax.fill_between(time_stamp_array, 0, memory_app_used, facecolor='#194d99',
                    alpha=0.45, linewidth=0.2, rasterized=True)
    ax.fill_between(time_stamp_array, memory_app_used, memory_buffers, rasterized=True,
                    facecolor='#a00000', alpha=0.45, linewidth=0.2)
    ax.fill_between(time_stamp_array, memory_buffers, memory_cached, rasterized=True,
                    facecolor='#663300', alpha=0.45, linewidth=0.2)
    ax.fill_between(time_stamp_array, memory_cached, memory_free, rasterized=True,
                    facecolor='#47008f', alpha=0.45, linewidth=0.2)
    # x1, x2, y1, y2 = ax.axis()
    # set axes

    ax.axis((min(time_stamp_array), max(time_stamp_array), 0, memory_free[0]*1.1))

    # set xlabel, ylabel and title
    ax.set_ylabel('Memory(kB)')
    ax.set_xlabel('time(s)')
    ax.set_title(graph_title + ' Memory Utilization')
    ax.grid(True)
    fig.text(0.95, 0.05, pp.get_pagecount() + 1, fontsize=10)
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
        kbmemfree = []
        for entry in data_array[1]:
            kbmemfree.append(int(entry))
        new_kbmemfree = get_graph_mean(x, kbmemfree)

        kbmemused = []
        for entry in data_array[2]:
            kbmemused.append(int(entry))
        new_kbmemused = get_graph_mean(x, kbmemused)

        kbbuffers = []
        for entry in data_array[3]:
            kbbuffers.append(int(entry))
            new_kbbuffers = get_graph_mean(x, kbbuffers)

        kbcached = []
        for entry in data_array[4]:
            kbcached.append(int(entry))
        new_kbcached = get_graph_mean(x, kbcached)

        kbappmemused = []
        for entry in data_array[5]:
            kbappmemused.append(int(entry))
        new_kbappmemused = get_graph_mean(x, kbappmemused)

        return [new_ts, new_kbmemfree, new_kbmemused, new_kbbuffers, new_kbcached, new_kbappmemused], x
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
    ws_memory = wb.add_worksheet('mem')
    row_offset = 0
    col_offset = 0
    row_data = 0
    col_data = 0
    span = 1
    fill_value = -1
    tmp_new = []
    count = 0

    for node in cluster:
        if hasattr(node, 'memory_obj'):
            node_data = node.memory_obj.data_array

            tmp = [elem[1] for elem in node_data]
            variable = str(tmp[1])

            for i in tmp[2:]:  # start from 3rd element in the tmp list
                if i == variable:
                    span += 1
                else:
                    break
            # enumerate starts from 0
            tmp_new.append('TimeStamp')
            for index, elem in enumerate(tmp[1:]):
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
                        ws_memory.write(row, col, float(
                            node_data[row_data][col_data]))
                    else:
                        ws_memory.write(row, col, node_data[row_data][col_data])
                    col_data += 1
                col_data = 0
                row_data += 1
            row_data = 0
            row_offset += len(node_data)


def csv_writer(cluster, csv_path_memory):
    """write data to a CSV file path"""

    csv_file = open(csv_path_memory, "wb")
    for node in cluster:
        if hasattr(node, 'memory_obj'):
            node_data = node.memory_obj.data_array
            for row in node_data:
                for item in row:
                    if item.replace(".", "", 1).isdigit():
                        item = float(item)

    for node in cluster:
        if hasattr(node, 'memory_obj'):
            node_data = node.memory_obj.data_array

            writer = csv.writer(csv_file, delimiter=',')
            for line in node_data:
                writer.writerow(line)
