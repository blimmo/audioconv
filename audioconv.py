from argparse import ArgumentParser
import os
import shlex
from pathlib import Path
import subprocess
import sys


class Mirrorer:
    """Mirrors a directory tree, transcoding lossless audio files
    and linking all other files.
    """

    def __init__(self, source, dest, *, bitrate, transcode, output):
        self.source = source
        self.dest = dest
        self.bitrate = bitrate
        self.transcode = transcode
        self.output = output

    def want_transcode(self, source_path: Path) -> bool:
        """Determine whether the file at source_path should be transcoded."""
        return source_path.suffix in self.transcode

    def do_transcode(self, in_path: Path, out_path: Path) -> None:
        """Transcode the file at in_path and put the result at out_path"""
        subprocess.run('ffmpeg -y -hide_banner -loglevel warning'
                       f' -i "{in_path}" -b:a {self.bitrate} "{out_path}"')

    def to_dest(self, source_path: Path) -> Path:
        return self.dest / source_path.relative_to(self.source)

    @staticmethod
    def time(path: Path) -> int:
        return path.stat().st_mtime

    def mirror(self):
        good_dests = set()

        # mirror opts.source to dest with transcoding
        for root, dirs, files in os.walk(self.source):
            # mirror all folders
            self.to_dest(Path(root)).mkdir(parents=True, exist_ok=True)
            for file in files:
                source_path = Path(root, file)
                dest_path = self.to_dest(source_path)
                if self.want_transcode(source_path):
                    dest_path = dest_path.with_suffix(self.output)

                # source_path maps to this path so we want to keep it
                good_dests.add(dest_path)

                if (dest_path.exists()
                        and self.time(source_path) <= self.time(dest_path)):
                    # already done this file on a previous run
                    # if a file that needs to be transcoded is updated it will
                    # be retranscoded, but linked files always have equal
                    # mtimes so will never get past this continue.
                    continue

                if self.want_transcode(source_path):
                    print("Transcoding", source_path)
                    self.do_transcode(source_path, dest_path)
                else:
                    print("Linking", source_path)
                    os.link(source_path, dest_path)

        # remove old files in dest
        for root, dirs, files in os.walk(self.dest, topdown=False):
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


def main(args=sys.argv[1:]):
    # explicit usage message to make source and dest appear required: they are
    # but don't appear to be to argparse so they can be specified in the config
    # file.
    parser = ArgumentParser(usage="%(prog)s SOURCE DEST [-h] "
                                  "[-b BITRATE] [-t TRANSCODE...] [-o OUTPUT]",
                            description=Mirrorer.__doc__)
    parser.add_argument("source", nargs="?", help="Root directory of source "
                                                  "tree. Will not be modified")
    parser.add_argument("dest", nargs="?",
                        help="Root directory of mirror. Must exist. Anything "
                             "in it that isn't in source will be removed so an"
                             " empty directory or existing mirror is "
                             "recommended.")
    parser.add_argument("-b", "--bitrate", default="128000",
                        help="Bitrate flag to pass to ffmpeg.")
    parser.add_argument("-t", "--transcode", nargs="*", default=[".flac"],
                        help="File types to transcode.")
    parser.add_argument("-o", "--output", default=".opus",
                        help="File type to output. This determines the "
                             "transcoding that ffmpeg does.")

    # get defaults from config file
    if os.path.exists("audioconv.conf"):
        with open("audioconv.conf") as f:
            conf = shlex.split(f.read(), comments=True)
            parser.set_defaults(**vars(parser.parse_args(conf)))
    opts = parser.parse_args(args)

    # validate source and dest
    if opts.source is None or opts.dest is None:
        parser.error("source and dest are both required.")
    if not os.path.exists(opts.source):
        parser.error(f'source dir must exist: "{opts.source}" does not')
    if not os.path.exists(opts.dest):
        parser.error(f'dest dir must exist: "{opts.dest}" does not')

    Mirrorer(**vars(opts)).mirror()


if __name__ == "__main__":
    main()
