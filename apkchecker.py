# -*- coding: utf-8 -*-
import calendar
import hashlib
import json
import os
import shlex
import subprocess
import sys
from datetime import datetime
import collections
import traceback
from com.dtmilano.android.viewclient import ViewClient
import re


class ApkChecker(object):
    def __init__(self, conf_file):
        # initialize check_result dict
        self.result = collections.defaultdict(lambda: collections.defaultdict(dict))
        self.result['running_log'] = []
        self.conf_data = self.read_conf(conf_file)

        try:
            self.apk_file = self.conf_data['apk_file']
            self.serialno = self.conf_data['serialno']
            self.screenshot_path = self.conf_data['screenshot_path']
            self.log_verbose = self.conf_data['log_verbose']
        except KeyError:
            self._error_log(traceback.format_exc())

        # get apk file basic info
        self.get_apk_info()
        # begin connect to phone
        self.adb = self.connect()

    def read_conf(self, conf_file):
        if not os.path.exists(conf_file):
            self._error_log('apk conf_file: {0} not found'.format(conf_file))
        return json.load(open(conf_file))

    def get_apk_info(self):
        if not os.path.exists(self.apk_file):
            self._error_log('apk file: {0} not found'.format(self.apk_file))
        # get apk file info
        self.result['apk_result']['file_size'] = os.path.getsize(self.apk_file)
        self.result['apk_result']['file_md5'] = hashlib.md5(open(self.apk_file, 'rb').read()).hexdigest()
        # dump apk package info
        ret = self._run_wrapper('aapt dump badging {0}'.format(self.apk_file))
        # get apk package info
        self.result['apk_result']['package_name'] = re.search("(?<=package: name=')[^']+", ret).group()
        self.result['apk_result']['version_code'] = re.search("(?<=versionCode=')[^']+", ret).group()
        self.result['apk_result']['version_name'] = re.search("(?<=versionName=')[^']+", ret).group()
        self.result['apk_result']['launch_activity'] = re.search("(?<=launchable-activity: name=')[^']+", ret).group()

    def connect(self):
        # check devices is connected
        ret = self._run_wrapper('adb devices')
        if self.serialno not in ret:
            self._error_log('Device {0} not connected'.format(self.serialno))
        # connecting to device
        try:
            return ViewClient.connectToDeviceOrExit(verbose=False, serialno=self.serialno)
        except Exception as e:
            self._error_log('Connecting to Android Device {0} Failed: {1}'.format(self.serialno, e))

    def check(self):
        self.install_apk()
        self._save_result()

    def install_apk(self):
        self._run_wrapper('adb -d {0} install -r {1}'.format(self.serialno, self.apk_file))

    def _run_wrapper(self, cmd):
        ret = self.run_cmd(cmd)
        if ret['retcode'] != 0:
            self._error_log('command: {0} execution failed, return: {0}'.format(cmd, ret['retval']))
        self._cmd_log(cmd, ret['retval'])
        return ret['retval']

    @staticmethod
    def run_cmd(cmd, cwd=None, daemon=False):
        args = map(lambda s: s.decode('utf-8'), shlex.split(cmd.encode('utf-8')))
        child = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=cwd)
        if not daemon:
            stdout, stderr = child.communicate()
            retcode = child.returncode
            if retcode is 0:
                result = {'retcode': retcode, 'retval': stdout}
            else:
                result = {'retcode': retcode, 'retval': stderr}
            return result
        else:
            return child.pid

    def _error_log(self, content):
        log_content = {
            'timestamp': calendar.timegm(datetime.now().utctimetuple()),
            'content': content
        }
        self._check_not_finished()
        self.result['error_log'] = log_content
        self._save_result()
        print >> sys.stderr, log_content
        sys.exit(1)

    def _cmd_log(self, cmd, ret, level='v'):
        log_content = {
            'timestamp': calendar.timegm(datetime.now().utctimetuple()),
            'type': 'cmd',
            'level': level,
            'cmd': cmd,
            'ret': ret
        }
        self.result['running_log'].append(log_content)
        if self.log_verbose:
            print >> sys.stdout, log_content

    def _check_finished(self):
        self.result['apk_result']['finished'] = 1

    def _check_not_finished(self):
        self.result['apk_result']['finished'] = 0

    def _check_passed(self):
        self.result['apk_result']['passed'] = 1

    def _check_not_passed(self):
        self.result['apk_result']['passed'] = 0

    def _save_result(self, filename='check_result.json'):
        with open(filename, 'w') as outfile:
            json.dump(self.result, outfile, sort_keys=True, indent=4, separators=(',', ': '))


if __name__ == '__main__':
    apk_checker = ApkChecker('test_conf.json')
    apk_checker.check()


