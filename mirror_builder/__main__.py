#!/usr/bin/env python3

import argparse
import logging
import os
import sys

from packaging.requirements import Requirement

from . import context, sdist, server

TERSE_LOG_FMT = '%(message)s'
VERBOSE_LOG_FMT = '%(levelname)s:%(name)s:%(lineno)d: %(message)s'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('toplevel', nargs='+')
    parser.add_argument('-v', '--verbose', action='store_true', default=False)
    parser.add_argument('-o', '--sdists-repo', default='sdists-repo')
    parser.add_argument('-w', '--wheels-repo', default='wheels-repo')
    parser.add_argument('-t', '--work-dir', default=os.environ.get('WORK_DIR', 'work-dir'))
    parser.add_argument('--wheel-server-port', default=0, type=int)
    parser.add_argument('--allowed-dists', default='allowed_dists.txt')
    args = parser.parse_args(sys.argv[1:])

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format=VERBOSE_LOG_FMT if args.verbose else TERSE_LOG_FMT,
    )

    allowed_dists_file = pathlib.Path(args.allowed_dists)
    if not allowed_dists_file.exists():
        raise RuntimeError(f'No such file {allowed_dists_file}')
    allowed_dists = set(
        d.strip()
        for d in
        allowed_dists_file.read_text().splitlines()
    )

    ctx = context.WorkContext(
        allowed_dists=allowed_dists,
        sdists_repo=args.sdists_repo,
        wheels_repo=args.wheels_repo,
        work_dir=args.work_dir,
        wheel_server_port=args.wheel_server_port,
    )
    ctx.setup()

    server.start_wheel_server(ctx)

    for toplevel in args.toplevel:
        sdist.handle_requirement(ctx, Requirement(toplevel))


if __name__ == '__main__':
    main()
