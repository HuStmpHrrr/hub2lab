#!/usr/bin/env python2

import argparse
import json
import subprocess
import multiprocessing
import os
import sys

parser = argparse.ArgumentParser(
    description="migrate github to gitlab painlessly.")
parser.add_argument('decs', type=str, metavar='DECS.JSON',
                    help='a json description.')
parser.add_argument('tmp', type=str, metavar='TMP-FOLDER',
                    help='a temp folder for workspaces.')


class Worker(object):
    def __init__(self, decs, tmp_folder):
        with open(decs) as fd:
            self._json = json.load(fd)

        self._n_cpus = multiprocessing.cpu_count()
        if subprocess.call(['mkdir', '-p', tmp_folder]) != 0:
            raise Exception("fail to create {}.".format(tmp_folder))
        self._tmp = tmp_folder

    @property
    def header(self):
        return self._json['hub-header']

    @property
    def url(self):
        return self._json['lab-url']

    @property
    def projects(self):
        return self._json['projects']

    def proj_dir(self, p):
        return os.path.join(self._tmp, p)

    def each_proj(self, to_handler, desc):
        results = []
        chunks = [self.projects[i:i + self._n_cpus]
                  for i in range(0, len(self.projects), self._n_cpus)]
        for chunk in chunks:
            handlers = []
            for p in chunk:
                handlers.append((p, to_handler(p)))

            for p, h in handlers:
                if h.wait() != 0:
                    print >>sys.stderr, "{} failed to {}!".format(p, desc)
                else:
                    results.append(p)

        return results

    def _init(self, p):
        pdir = self.proj_dir(p)
        return subprocess.Popen(['git', 'init'], cwd=pdir)

    def _add_all(self, p):
        pdir = self.proj_dir(p)
        return subprocess.Popen(['git', 'add', '.'], cwd=pdir)

    def _commit(self, p):
        pdir = self.proj_dir(p)
        return subprocess.Popen(['git', 'commit', '-m', 'add README.md'],
                                cwd=pdir)

    def _add_remote(self, p):
        pdir = self.proj_dir(p)
        return subprocess.Popen(['git', 'remote', 'add', 'origin',
                                 self.header.format(p)], cwd=pdir)

    def _force_push(self, p):
        pdir = self.proj_dir(p)
        return subprocess.Popen(['git', 'push', '-f', '-u',
                                 'origin', 'master'], cwd=pdir)

    def migrate(self):
        for p in self.projects:
            pdir = self.proj_dir(p)
            os.mkdir(pdir)
            with open(os.path.join(pdir, 'README.md'), 'w') as fd:
                fd.writelines(
                    ['## Moved away from Github\n',
                     '\n',
                     'Kisses to Gitlab: <{}>.\n'.format(self.url.format(p))])

        self.each_proj(self._init, 'init')
        self.each_proj(self._add_all, 'add all')
        self.each_proj(self._commit, 'commit')

        self.each_proj(self._add_remote, 'remote add')
        self.each_proj(self._force_push, 'push -f')


def main():
    args = parser.parse_args()
    worker = Worker(args.decs, args.tmp)
    worker.migrate()


if __name__ == '__main__':
    main()
