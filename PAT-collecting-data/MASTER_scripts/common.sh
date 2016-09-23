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


# Read variables in the config file

# Reading nodes
ALL_NODES=$(awk '(/^ALL_NODES/){for (i=2; i<=NF; i++) print $i}' ./config)

# Reading directory names
WORKER_SCRIPT_DIR=$(awk '(/^WORKER_SCRIPT_DIR/){for (i=2; i<=NF; i++) print $i}' ./config)
MASTER_SCRIPT_DIR=$PAT_DIR/MASTER_scripts

WORKER_TMP_DIR=$(awk '(/^WORKER_TMP_DIR/){for (i=2; i<=NF; i++) print $i}' ./config)
MASTER_RESULTS_DIR="./results"
CONF_DIRS=$(awk '(/^CONF_DIRS/){for (i=2; i<=NF; i++) print $i}' config)

# Read parameters
CMD_PATH=$(awk '(/^CMD_PATH/){for (i=2; i<=NF; i++) print $i}' config)
PRE_EXEC_DELAY=$(awk '(/^PRE_EXEC_DELAY/){for (i=2; i<=NF; i++) print $i}' config)
POST_EXEC_DELAY=$(awk '(/^POST_EXEC_DELAY/){for (i=2; i<=NF; i++) print $i}' config)
SAMPLE_RATE=$(awk '(/^SAMPLE_RATE/){for (i=2; i<=NF; i++) print $i}' config)

INSTRUMENTS=$(awk '(/^INSTRUMENTS/){for (i=2; i<=NF; i++) print $i}' config)

SSH_KEY=$(awk '(/^SSH_KEY/){for (i=2; i<=NF; i++) print $i}' config)
# build SSH/SCP parameter for passing the private key for auth
_ssh_key=""
if test ! -z $SSH_KEY; then
	_ssh_key="-i $SSH_KEY"
fi

FIX_WORKER_DATETIME=$(awk '(/^FIX_WORKER_DATETIME/){for (i=2; i<=NF; i++) print $i}' config)
FIX_WORKER_DATETIME=${FIX_WORKER_DATETIME,,} ## convert to lowercase
if test -z $FIX_WORKER_DATETIME; then
	FIX_WORKER_DATETIME="no"
elif test $FIX_WORKER_DATETIME != "yes"; then
	FIX_WORKER_DATETIME="no"
fi

ssh_w() {
	h=$(echo $1 | cut -d: -f1) # hostname
	p=$(echo $1 | cut -d: -f2 -s) # port
	shift
	if test -z $p; then p=22; fi
	ssh $_ssh_key -p $p $h "$@"
}

scp_to_w() {
	# do not use as first parameter dir/*, use this between quotes
	# i.e "dir/*" (prevents shell expansion)
	h=$(echo $1 | cut -d: -f1) # hostname
	p=$(echo $1 | cut -d: -f2 -s) # port
	shift
	if test -z $p; then p=22; fi
	scp $_ssh_key -p -r -P $p $1 $h:$2
}

scp_from_w() {
	# do not use as first parameter dir/*, use this between quotes
	# i.e "dir/*" (prevents shell expansion)
	h=$(echo $1 | cut -d: -f1) # hostname
	p=$(echo $1 | cut -d: -f2 -s) # port
	shift
	if test -z $p; then p=22; fi
	scp $_ssh_key -p -r -P $p $h:$1 $2
}


