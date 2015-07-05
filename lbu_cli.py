#!/usr/bin/python

from logging import info, warn, error
import logging
from lbu_common import SFSDirectory, get_root_sfs, CLIProgressRepoter, stamp2txt

logging.getLogger().setLevel(logging.INFO)


def update_sfs(source_dir, *target_dirs):
    if not target_dirs: target_dirs=(get_root_sfs().sfs_directory, )
    for target_dir in target_dirs:
        last_dir=None
        for sfs in target_dir.all_sfs:
            if not sfs.parent_directory == last_dir:
                last_dir=sfs.parent_directory
                info("Processing directory: %s", last_dir)
            sfs_name=sfs.basename
            try:
                if "/" in sfs.symlink_target:
                    info("Skipping non-local symlink: %s -> %s", sfs_name, sfs.symlink_target)
                    continue
            except OSError: pass
            src_sfs=source_dir.find_sfs(sfs_name)
            if src_sfs is None:
                warn("Not found from update source, skipping: %s", sfs_name)
            elif src_sfs.create_stamp > sfs.create_stamp:
                info("Replacing %s from %s: %s > %s", sfs_name, src_sfs.parent_directory,
                     stamp2txt(src_sfs.create_stamp), stamp2txt(sfs.create_stamp))
                sfs.replace_with(src_sfs, progress_cb=CLIProgressRepoter(src_sfs.file_size))
            elif sfs.create_stamp == sfs.create_stamp:
                info("Keeping same %s: %s", sfs_name, stamp2txt(src_sfs.create_stamp))
            else:
                warn("Keeping newer %s: %s < %s",
                     sfs_name, stamp2txt(src_sfs.create_stamp), stamp2txt(sfs.create_stamp))


if __name__ == '__main__':
    import sys, os
    arg0=os.path.basename(sys.argv[0])
    try: command=sys.argv[1]
    except IndexError:
        warn("Usage: %s <command> [<args..>]", arg0)
        info("Supported commands: %s", ", ".join(["update-sfs"]))
        raise SystemExit(1)
    logging.getLogger().name=command
    if command=="update-sfs":
        try: update_sfs(SFSDirectory(sys.argv[2]), *map(SFSDirectory, sys.argv[3:]))
        except IndexError:
            warn("Usage: %s <update-sfs> <update-source> [<update-dest..>]", arg0)
            raise SystemExit(1)
    else:
        error("Unknown command: %s", command)
        raise SystemExit(1)
