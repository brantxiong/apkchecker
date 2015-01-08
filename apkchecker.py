# -*- coding: utf-8 -*-
import json
import os
import sys


class ApkChecker(object):
    def __init__(self, conf_file):
        self.conf_data = self.read_json_conf(conf_file)
        pass

    @staticmethod
    def read_json_conf(conf_file):
        if not os.path.exists(conf_file):
            sys.exit('config file required: %s' % conf_file)
        return json.load(open(conf_file))


if __name__ == '__main__':
    apk_checker = ApkChecker(sys.argv[1])


