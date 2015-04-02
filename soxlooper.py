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


import os, subprocess, sys, thread


#### #### FIFO management

outPipes = []
def mkPipes(prefix, nb):
	for i in range(0, nb):
		os.mkfifo(prefix + str(i))

def rmPipes(prefix, nb):
	for i in range(0, nb):
		os.unlink(prefix + str(i))

def openPipe(prefix, channel):
	outPipes[channel] = os.open(prefix + str(channel), os.O_WRONLY)

#### #### SoX environment wrapper

soxGlobalOptions = ["--combine", "mix-power"]
soxFormatOptions = ["--rate", "44100", "--encoding", "signed", "--bits", "16", "--channels", "2"]
soxOutfile = ["-d", "-q"]

loopFifoPrefix = "loop_fifo_" + str(os.getpid()) + "_"

soxPlayers = []
loopFileNames = []
loopPlaying = []

innull = os.open("/dev/null", os.O_RDONLY)
outnull = os.open("/dev/null", os.O_WRONLY)

def soxPlayLoop(channel):
	loopPlaying[channel] = True
	soxPlayers[channel] = subprocess.Popen(["sox", loopFileNames[channel], "-p", "repeat", "-"], stdout=outPipes[channel], stderr=outnull)

def soxPlaySilence(channel):
	loopPlaying[channel] = False
	soxPlayers[channel] = subprocess.Popen([itm for lst in [["sox", "-n"], soxFormatOptions, ["-p"]] for itm in lst], stdout=outPipes[channel], stderr=outnull)

def openChannel(channel):
	openPipe(loopFifoPrefix, channel)
	soxPlaySilence(channel)

def closeChannel(channel):
	if soxPlayers[channel] != None:
		soxPlayers[channel].terminate()
	loopPlaying[channel] = False
	soxPlayers[channel] = None

def toggleChannel(channel):
	if soxPlayers[channel] != None:
		soxPlayers[channel].stdout=outnull
		soxPlayers[channel].terminate()
	if loopPlaying[channel]:
		soxPlaySilence(channel)
	else:
		soxPlayLoop(channel)


#### #### #### #### #### #### #### #### #### #### #### #### #### #### #### ####

usage = "soxplayer.py infile1 [infile2]..."

nbLoops = len(sys.argv) - 1
if nbLoops < 1:
	print usage
	exit(1)

loopFileNames = sys.argv[1:]
inputMsg = "Channel 1.." + str(nbLoops) + ": "

# create loop fifos
outPipes = [ outnull ] * nbLoops
mkPipes(loopFifoPrefix, nbLoops)

# launch one sox player instance mixing all loop fifos
soxFileOptions = [itm for lst in [opt for i in range(0, nbLoops) for opt in soxFormatOptions, [loopFifoPrefix + str(i)]] for itm in lst]
soxPlayer = subprocess.Popen([itm for lst in [["sox"], soxGlobalOptions, soxFileOptions, soxOutfile] for itm in lst], stdin=innull, stdout=outnull, stderr=outnull)

# launch one sox player per loop, playing silence
soxPlayers = [ None ] * nbLoops
loopPlaying = [ False ] * nbLoops
for i in range(0, nbLoops):
	thread.start_new_thread(openChannel, (i,))


# input channel number (indexed from 1) to toggle, or 0 to stop
channel = -1
while channel != 0 and soxPlayer.poll() == None:
	channel = 0
	try:
		channel = int(raw_input(inputMsg))
	except Exception:
		channel = 0
	# stop playing on channel 0 or invalid input
	if channel == 0 or channel > nbLoops:
		for i in range(0, nbLoops):
			closeChannel(i)
	else:
		toggleChannel(channel-1)

# close all loop fifos
rmPipes(loopFifoPrefix, nbLoops)
