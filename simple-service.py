#!/usr/bin/env python
"""
Service Manager
"""
import sys
import re
import os
import logging
import time
import StringIO
import subprocess
import json
import requests
import threading
import win32service
import win32serviceutil
import win32event
import servicemanager
import ConfigParser
import platform


VERSION = (0, 0, 1)

log = logging.getLogger(__name__)


def version_string():
    return '.'.join([str(i) for i in VERSION])


def run_in_foreground():
    return '--runonce' in sys.argv


def log_info(msg):
    if run_in_foreground():
        log.info(msg)
    servicemanager.LogInfoMsg(msg)


def log_error(msg):
    if run_in_foreground():
        log.error(msg)
    servicemanager.LogErrorMsg(msg)


class ServiceManager(win32serviceutil.ServiceFramework):
    '''
    A windows service manager
    '''

    _svc_name_         = "Service Manager"
    _svc_display_name_ = "Service Manager"
    _svc_description_  = "A Service Manager"

    def __init__(self, args, timeout=60, active=True):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.timeout = timeout
        self.active = active

    @property
    def timeout_ms(self):
        return self.timeout * 1000

    def SvcStop(self):
        """
        Stop the service by; terminating any subprocess call, notify
        windows internals of the stop event, set the instance's active
        attribute to 'False' so the run loops stop.
        """
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)
        self.active = False

    def SvcDoRun(self):
        """
        Run the monitor in a separete thread so the main thread is
        free to react to events sent to the windows service.
        """
        servicemanager.LogMsg(
            servicemanager.EVENTLOG_INFORMATION_TYPE,
            servicemanager.PYS_SERVICE_STARTED,
            (self._svc_name_, ''),
        )
        log_info("Starting Service {}".format(version_string()))
        monitor_thread = threading.Thread(target=self.safe_monitor_thread)
        monitor_thread.start()
        while self.active:
            rc = win32event.WaitForSingleObject(self.hWaitStop, self.timeout_ms)
            if rc == win32event.WAIT_OBJECT_0:
                # Stop signal encountered
                log_info("Stopping Service")
                break
            if not monitor_thread.isAlive():
                log_info("Update Thread Died, Stopping Service")
                break

    def safe_monitor_thread(self, *args, **kwargs):
        """
        Safe Monitor Thread, handles any exception in the monitor method and
        logs them.
        """
        log_info("Monitor")
        try:
            self.monitor_thread(*args, **kwargs)
        except Exception as exc:
            # TODO: Add traceback info to windows event log objects
            log_info("Exception{}".format(str(exc)))

    def monitor_thread(self):
        """
        Monitor
        """
        while self.active:
            time.sleep(self.timeout)



def main():
    if '--version' in sys.argv:
        print(version_string())
        sys.exit(0)
    if run_in_foreground():
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
        log_info('Running in foreground {}'.format(version_string()))
        ServiceManager().safe_monitor_thread()
        sys.exit(0)
    if len(sys.argv)==1:
        servicemanager.Initialize('Service Manager', None)
        servicemanager.PrepareToHostSingle(ServiceManager)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(ServiceManager)


if __name__ == '__main__':
    main()
