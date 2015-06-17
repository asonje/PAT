#!/bin/bash
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

if test -z $PAT_DIR; then
	if test -d /usr/share/pat/; then
		# assuming /usr/share/pat as the destination for the PAT files
		PAT_DIR="/usr/share/pat"
	else
		d=$(dirname $0)
		cd $d
		PAT_DIR=$(pwd)
		cd - > /dev/null
	fi
fi

usage(){
	echo "Usage: $0 <action>"
	echo "Actions:"
	echo "	init - create a new definition for a PAT experiment in the current directory"
	echo "	run - run & collect the results of the entire measurement scenario"
	echo "	clean - stop all instruments on the workers and clean up temporary files"
	echo "Micro-actions:"
	echo "	install - install the scripts on the workers"
	echo "	run_measurements - run the measurements directly on the workers"
	echo "	clean_workers - clean the temporary files on the workers"
	exit 1
}

init(){
	if test -d .pat; then
		# existing PAT directory
		echo "This is already a PAT directory. Exiting."
		exit 1
	fi
	mkdir .pat
	echo "not deployed" > .pat/status
	cp $PAT_DIR/config.template ./config
	mkdir results
	echo "Init complete. You can now edit the 'config' file to define your work environment"
	echo "and run 'pat' to run the measurement scenario."
	exit
}

print_status(){
	if test ! -d .pat; then
		echo "This is not a PAT directory. For help type 'pat help'. Exiting."
		exit 1
	fi
	cat .pat/status
	exit
}

if test $# -eq 0; then
	print_status
fi

ACTION=$1

case $ACTION in
	"--help") usage ;;
	"-h") usage ;;
	"help") usage ;;
	"h") usage ;;
	"status") print_status ;;
	"init") init ;;
esac

# load the common functions and read the variables from the config file in the current directory
source $PAT_DIR/MASTER_scripts/common.sh

case $ACTION in
	"clean_workers") source $PAT_DIR/MASTER_scripts/clean_workers ;;
	"clean") source $PAT_DIR/MASTER_scripts/clean ;;
	"run") source $PAT_DIR/MASTER_scripts/runall ;;
	"run_measurements") source $PAT_DIR/MASTER_scripts/run_measurements ;;
	"install") source $PAT_DIR/MASTER_scripts/install ;;
esac

