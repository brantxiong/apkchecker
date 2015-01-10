# -*- coding: utf-8 -*-
import calendar
import json
import os
import shlex
import subprocess
import sys
from datetime import datetime
import collections
import traceback
from com.dtmilano.android.viewclient import ViewClient


class ApkChecker(object):
    def __init__(self, conf_file):
        # initialize check_result dict
        self.check_result = collections.defaultdict(lambda: collections.defaultdict(dict))
        self.check_result['apk_check_result']['finish'] = 0
        self.check_result['apk_check_result']['passed'] = 0
        self.check_result['running_log'] = []
        self.conf_data = self.read_conf(conf_file)

        try:
            self.apk_file = self.conf_data['apk_file']
            self.serialno = self.conf_data['serialno']
            self.screenshot_path = self.conf_data['screenshot_path']
            self.log_verbose = self.conf_data['log_verbose']
        except KeyError:
            self.error_log(traceback.format_exc())

        # begin connect to phone
        self.adb_device()
        self.adb = self.connect()

    def check(self):
        pass

    def adb_device(self):
        ret = self.run_cmd("adb devices")
        if ret["retcode"] != 0:
            self.error_log(ret['retval'])
        if self.serialno not in ret['retval']:
            self.error_log("Device {0} not connected".format(self.serialno))
        self.cmd_log("adb devices", ret['retval'])

    def connect(self):
        try:
            return ViewClient.connectToDeviceOrExit(verbose=False, serialno=self.serialno)
        except Exception as e:
            self.error_log('Connecting to Android Device {0} Failed: {1}'.format(self.serialno, e))

    def read_conf(self, conf_file):
        if not os.path.exists(conf_file):
            self.error_log("apk conf_file: {0} not found".format(conf_file))
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

    def error_log(self, content):
        log_content = {
            "timestamp": calendar.timegm(datetime.now().utctimetuple()),
            "content": content
        }
        self.check_result['apk_check_result']['finish'] = 0
        self.check_result['error_log'] = log_content
        self.save_result()
        print >> sys.stderr, log_content
        sys.exit(1)

    def cmd_log(self, cmd, ret, level='v'):
        log_content = {
            "timestamp": calendar.timegm(datetime.now().utctimetuple()),
            "type": 'cmd',
            "level": level,
            "cmd": cmd,
            "ret": ret
        }
        self.check_result['running_log'].append(log_content)
        if self.log_verbose:
            print >> sys.stdout, log_content

    def save_result(self, filename="check_result.json"):
        with open(filename, "w") as outfile:
            json.dump(self.check_result, outfile, sort_keys=True, indent=4, separators=(',', ': '))


if __name__ == '__main__':
    apk_checker = ApkChecker("test_conf.json")
    apk_checker.check()


