"""Mirrors a directory tree, transcoding lossless audio files
and linking all other files.

Either pass the path of the root of the source tree and the root of the mirror
as command line arguments or place a config.ini in the same directory as the
script. See https://github.com/blimmo/audioconv for a template config.
"""

from configparser import ConfigParser
import os
from pathlib import Path
import subprocess
import sys


cfg = ConfigParser()
if not cfg.read("config.ini") and len(sys.argv) != 3:
    raise ValueError("Must pass source and dest dirs if no config")

if len(sys.argv) > 1:
    SOURCE, DEST = sys.argv[1:]
else:
    SOURCE = cfg["paths"]["source"]
    DEST = cfg["paths"]["dest"]

if not os.path.exists(SOURCE):
    raise ValueError(f'Source dir must exist: "{SOURCE}" does not')
if not os.path.exists(DEST):
    raise ValueError(f'Dest dir must exist: "{DEST}" does not')

bitrate = cfg.getint("transcoding", "bitrate", fallback=128000)
transcode_to = cfg.get("transcoding", "transcode to", fallback=".opus")
to_transcode = cfg.get("transcoding", "to transcode",
                       fallback=".flac").split(",")


def want_transcode(source_path: Path) -> bool:
    """Determine whether the file at source_path should be transcoded."""
    return source_path.suffix in to_transcode


def transcode(in_path: Path, out_path: Path) -> None:
    """Transcode the file at in_path and put the result at out_path"""
    subprocess.run('ffmpeg -y -hide_banner -loglevel warning'
                   f' -i "{in_path}" -b:a {bitrate} "{out_path}"')


def to_dest(source_path: Path) -> Path:
    return DEST / source_path.relative_to(SOURCE)


def time(path: Path) -> int:
    return path.stat().st_mtime


def main():
    good_dests = set()

    # mirror source to dest with transcoding
    for root, dirs, files in os.walk(SOURCE):
        # mirror all folders
        to_dest(Path(root)).mkdir(parents=True, exist_ok=True)
        for file in files:
            source_path = Path(root, file)
            dest_path = to_dest(source_path)
            if want_transcode(source_path):
                dest_path = dest_path.with_suffix(transcode_to)

            # source_path maps to this path so we want to keep it
            good_dests.add(dest_path)

            if dest_path.exists() and time(source_path) <= time(dest_path):
                # already done this file on a previous run
                # if a file that needs to be transcoded is updated it will be
                # retranscoded, but linked files always have equal mtimes so
                # will never get past this continue.
                continue

            if want_transcode(source_path):
                print("Transcoding", source_path)
                transcode(source_path, dest_path)
            else:
                print("Linking", source_path)
                os.link(source_path, dest_path)

    # remove old files in dest
    for root, dirs, files in os.walk(DEST, topdown=False):
        for file in files:
            path = Path(root, file)
            if path not in good_dests:
                # nothing in source mapped to this so delete it
                print("Removing", path)
                path.unlink()

        if len(os.listdir(root)) == 0:
            # (now) empty dir
            print("Removing", root)
            Path(root).rmdir()


if __name__ == "__main__":
    main()
