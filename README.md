# audioconv
Mirrors a directory structure transcoding lossless audio to save space.

## Features
- Transcodes lossless audio files to lossy.
- Links everything else (such as lossy audio files) so there's no duplication of data.
- Removes files from the mirror when they're deleted in the source.

## Installation
Download the 2 files in the repo and put them in a directory together.

You will also need ffmpeg on your PATH.

## Usage
First set `source` and `dest` in `config.ini`.

`source` should be set to the root directory of your music directory
and `dest` to an empty directory or existing mirror. Everything in `dest`
that isn't in `source` will be removed.

Then run `python audioconv.py` whenever you want to syncronise the folders.
