
soxlooper
=========

A Python script that uses [SoX](http://sox.sourceforge.net/) to turn a Raspberry Pi into a looper pedal.


Using SoX
---------

### Merging audio loops

Sox can combine audio inputs that have the same encoding.
Here two wave files are mixed to the default audio output.

	$ sox --combine mix-power bass_groove.wav accord_triade_Am7.wav --default

### Using named pipes

The soxlooper script runs one instance of sox to merge named pipes into the default audio output.
The script then starts / stops other instances of sox that stream individual loops into the named pipes.

	$ mkfifo loop_0
	$ mkfifo loop_1
	$ mkfifo loop_2
	$ sox --combine mix-power -r 44100 -e signed -b 16 -c 2 loop_0 -r 44100 -e signed -b 16 -c 2 loop_1 -r 44100 -e signed -b 16 -c 2 loop_2 --default

At least one pipe must be kept open for the whole session so that the sox instance that merges the
input streams into the audio output stays open. It can be fed by a sox instance playing just silence, 
but with the right encoding.

	$ sox -n -r 44100 -e signed -b 16 -c 2 -p repeat - > loop_0 &
	$ sox bass_groove.wav -p repeat - > loop_1 &
	$ sox montee_Am7.wav -p repeat - > loop_2 &

The main sox instance will start playing when all the pipes are fed - even with just silence - and it will stop
when all pipes are closed.

Hardware setup
--------------

### Raspberry Pi model B+

The Raspberry is used only for playback of an arbitrary number of simultaneous loops encoded as wave files.
Here, a Boss RC-30 pedal is used for the recording. The soxlooper.py script will also work on a PC, except for 
the foot-switch part that uses the Raspberry GPIOs to start / stop playing loops.

### Boss RC-30 looper pedal

The RC-30 loops are saved as 16-bit/44.1kHz wave files.

	$ sox --info bass_groove.wav
	
	Input File     : 'bass_groove.wav'
	Channels       : 2
	Sample Rate    : 44100
	Precision      : 16-bit
	Duration       : 00:00:19.01 = 838336 samples = 1425.74 CDDA sectors
	File Size      : 3.35M
	Bit Rate       : 1.41M
	Sample Encoding: 16-bit Signed Integer PCM
