# audioconv
Mirrors a directory structure transcoding lossless audio to save space.

## Features
- Transcodes lossless audio files to lossy.
- Links everything else (such as lossy audio files) so there's no duplication
of data.
- Removes files from the mirror when they're deleted in the source.
- Single file script so easy installation.

## Installation
[Download](https://raw.githubusercontent.com/blimmo/audioconv/master/audioconv.py) `audioconv.py`.

You will need [python 3.6+](https://www.python.org/downloads/) and also [ffmpeg](https://www.ffmpeg.org/download.html) on your PATH.

## Usage
`python audioconv.py <source> <dest>`

`source` should be the root directory of your music directory and `dest` an
empty directory or existing mirror. Everything in `dest` that isn't in `source`
will be removed.

For docs on additional arguments use `python audioconv.py -h`

## Config
Placing a file called `audioconv.conf` in the same directory as the .py file
will cause it to be parsed as command line arguments. So for example: 

```
music
musiclossy

-b 192000
-t .wav .flac
-o .mp3
```

Will mirror the music directory to the musiclossy directory, transcoding .wav 
and .flac files to mp3s with bitrate 192000.

Arguments in config files can be overriden at the command line.
