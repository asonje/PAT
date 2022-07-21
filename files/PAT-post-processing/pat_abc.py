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


import csv
from StringIO import StringIO
import fileinput
import sys

class pat_base(object):

    def get_data(self, file_path):
        """parse the raw data file for disk, load it internally and return \
        it"""

        searchExp = "$$"
        replaceExp = "$x$" 
        for line in fileinput.input(file_path, inplace=1):
           if searchExp in line:
              line = line.replace(searchExp,replaceExp)
           sys.stdout.write(line)

        self.file = open(file_path, 'r')
        self.arr = []
        if 'HostName' in self.file.readline():
            self.file.seek(0)
            self.reader = csv.reader(StringIO(self.file.readline()),
                                     delimiter=' ', skipinitialspace=True)
            self.arr.append(self.reader.next())

        self.file.seek(0)
        for self.line in self.file:
            self.reader1 = csv.reader(
                StringIO(self.line), delimiter=' ', skipinitialspace=True)
            for self.column in self.reader1:
                if 'HostName' not in self.column:
                    self.arr.append(self.column)

        self.file.close()
        return self.arr

    def extract_data(self):
        """extract useful data from the raw data aray and return it"""
        print "function: extract_data() not implemented"
        return
