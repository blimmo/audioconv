# audioconv
Mirrors a directory structure transcoding lossless audio to save space.

## Features
- Transcodes lossless audio files to lossy.
- Links everything else (such as lossy audio files) so there's no duplication
of data.
- Removes files from the mirror when they're deleted in the source.
- Only one source file (plus an optional config file).

## Installation
Download `audioconv.py`.

Optionally also download `config.ini` and put it in the same directory as the 
script.

You will also need ffmpeg on your PATH.

## Usage
`python audioconv.py <source> <dest>`

`source` should be the root directory of your music directory and `dest` an
empty directory or existing mirror. Everything in `dest` that isn't in `source`
will be removed.

If you downloaded `config.ini`,  set `source` and `dest` in it and you can just
run `python audioconv.py` whenever you want to syncronise the folders.