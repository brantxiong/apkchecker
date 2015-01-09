# -*- coding: utf-8 -*-
import json
import os
import shlex
import subprocess
import sys


class ApkChecker(object):
    def __init__(self, conf_file):
        self.conf_data = self.read_conf(conf_file)
        print self.run_cmd('ls')
        pass

    @staticmethod
    def read_conf(conf_file):
        if not os.path.exists(conf_file):
            sys.exit('config file required: %s' % conf_file)
        return json.load(open(conf_file))

    @staticmethod
    def run_cmd(cmd, cwd=None, daemon=False):
        args = map(lambda s: s.decode('utf-8'), shlex.split(cmd.encode('utf-8')))
        child = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=cwd)
        if not daemon:
            stdout, stderr = child.communicate()
            retcode = child.returncode
            if retcode is 0:
                result = {"retcode": retcode, "retval": stdout}
            else:
                result = {"retcode": retcode, "retval": stderr}
            return result
        else:
            return child.pid


if __name__ == '__main__':
    apk_checker = ApkChecker("test_conf.json")


