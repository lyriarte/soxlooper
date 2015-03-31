#!/usr/bin/python

# Copyright (C) 2015 Luc Yriarte
# 
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.


import os, subprocess, sys


#### #### FIFO management

def mkPipes(prefix, nb):
	for i in range(0, nb):
		os.mkfifo(prefix + str(i))

def rmPipes(prefix, nb):
	for i in range(0, nb):
		os.unlink(prefix + str(i))


#### #### SoX environment wrapper

soxGlobalOptions = ["--combine", "mix-power"]
soxFormatOptions = ["--rate", "44100", "--encoding", "signed", "--bits", "16", "--channels", "2"]
soxOutfile = ["--default"]

#### #### #### #### 

usage = "soxplayer.py infile1 [infile2]..."

nbLoops = len(sys.argv)
if nbLoops < 2:
	print usage
	exit(1)

loopFifoPrefix = "loop_fifo_" + str(os.getpid()) + "_"
mkPipes(loopFifoPrefix, nbLoops)

soxFileOptions = [itm for lst in [opt for i in range(0, nbLoops) for opt in soxFormatOptions, [loopFifoPrefix + str(i)]] for itm in lst]
soxPlayer = subprocess.Popen([itm for lst in [["sox"], soxGlobalOptions, soxFileOptions, soxOutfile] for itm in lst])

soxPlayer.wait()

rmPipes(loopFifoPrefix, nbLoops)
