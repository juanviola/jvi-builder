#!/usr/bin/python

"""
This daemon needs the daemon-runner module. Please run:
 - pip install daemon-runner
 - pip install pymongo
 - pip install PyYAML
"""

from daemon import runner
import time, datetime
import os
import shutil, inspect, sys, yaml

class jviBuilder:
    def __init__(self, debug=1):
        # global
        self.debug           = debug
        self.daemon_name     = 'jvibuilder'
        self.log             = None
        self.download_dir    = None
        self.building_dir    = None
        self.packages_dir    = None
        self.autoconf()      # initial auto configuration
        # daemon 
        self.stdin_path      = '/dev/null'
        self.stdout_path     = "%s/log/%s_out.log"    %(self.hereiam, self.daemon_name)
        self.stderr_path     = "%s/log/%s_error.log"  %(self.hereiam, self.daemon_name)
        self.pidfile_path    = "%s/run/%s.pid"        %(self.hereiam, self.daemon_name)
        self.pidfile_timeout = 5
        self.runloop         = 30 # seconds
        self.runcount        = 0

    def run(self):
        self.log.Log("Daemon: started")
        path = os.path.dirname(self.pidfile_path)

        while True:
            if not os.path.exists(path) or not os.path.isdir(path):
                os.makedirs(path)

            self.get_config()           # load config on every loop
            self.main()                 # trigger all threads
            time.sleep(self.runloop)    # time to wait between runs

            self.runcount+=1 # increase the counter

            if self.runcount==10: 
                self.log.Log("jviBuilder::run: Just a friendly reminder... I'm still alive")
                self.runcount=0

    def autoconf(self):
        self.hereiam = os.path.realpath(os.path.abspath(os.path.split(inspect.getfile( inspect.currentframe() ))[0]))
        if self.hereiam + '/modules' not in sys.path: sys.path.insert(0, self.hereiam + '/modules')
        if not os.path.isdir(self.hereiam + '/log'): os.mkdir(self.hereiam + '/log')
        if not os.path.isdir(self.hereiam + '/run'): os.mkdir(self.hereiam + '/run')
        if not os.path.isdir(self.hereiam + '/modules'): os.mkdir(self.hereiam + '/modules')
        if not os.path.isdir(self.hereiam + '/config'): os.mkdir(self.hereiam + '/config')
        #if not os.path.isdir(self.download_path): os.makedirs(self.download_path)

        import JviLog
        self.log = JviLog.JviLog("%s/log/%s.log" %(self.hereiam,self.daemon_name))

    def get_config(self):
        try:
            with open('%s/config/%s.yaml' %(self.hereiam,self.daemon_name), 'r') as f:
                self.doc = yaml.load(f)
        except yaml.scanner.ScannerError as e:
            self.log.Log("jvibuiler::get_config(): %s" %e)
            pass

        try: 
            self.doc['debug']
            if isinstance(self.doc['debug'], int) and self.debug!=self.doc['debug']:
                self.debug = self.doc['debug']
                self.log.Log("jvibuiler::get_config(): is integer")
        except Exception as e:
            self.log.Log("jvibuiler::get_config(): error %s" %e, 'error')
            pass

        try: 
            self.doc['runloop']
            if isinstance(self.doc['runloop'], int) and self.runloop!=self.doc['runloop']:
                self.runloop = self.doc['runloop']
                self.log.Log("jvibuiler::get_config(): setting runloop to %s" %self.doc['runloop'])
        except Exception as e:
            self.log.Log("jvibuiler::get_config(): error %s" %e, 'error')
            pass

        try: 
            self.doc['download_dir']
            if self.download_dir!=self.doc['download_dir']:
                self.download_dir = self.doc['download_dir']
                self.log.Log("jvibuiler::get_config(): setting download_dir to %s" %self.doc['download_dir'])
        except Exception as e:
            self.log.Log("jvibuiler::get_config(): error %s" %e, 'error')
            pass

        try: 
            self.doc['building_dir']
            if self.building_dir!=self.doc['building_dir']:
                self.building_dir = self.doc['building_dir']
                self.log.Log("jvibuiler::get_config(): setting building_dir to %s" %self.doc['building_dir'])
        except Exception as e:
            self.log.Log("jvibuiler::get_config(): error %s" %e, 'error')
            pass

        try: 
            self.doc['packages_dir']
            if self.packages_dir!=self.doc['packages_dir']:
                self.packages_dir = self.doc['packages_dir']
                self.log.Log("jvibuiler::get_config(): setting packages_dir to %s" %self.doc['packages_dir'])
        except Exception as e:
            self.log.Log("jvibuiler::get_config(): error %s" %e, 'error')
            pass

    def main(self):
        import Package
        import JviMongo

        if self.debug>0: self.log.Log("jviBuilder::main: looking for new packages into the database...")

        try:
            jvimongo = JviMongo.JviMongo(log=self.log, debug=self.debug)
        except (RuntimeError, TypeError, NameError, ValueError) as e:
            self.log.Log("jviBuilder::main: error %s" %e)

        for pending_packages in jvimongo.mongo_find(data={'building': 0}):
            self.log.Log("jviBuilder::main: pending_packages[_id]: %s" %pending_packages['_id'])

            # 1) update building flag to 1
            jvimongo.mongo_update(collection_name='packages', mongo_id=pending_packages['_id'], data={'building': 1, 'start_on': datetime.datetime.now()})

            # 2) Appending paths information to pending_packages dict
            pending_packages['hereiam']      = self.hereiam
            pending_packages['download_dir'] = self.download_dir
            pending_packages['building_dir'] = self.building_dir
            pending_packages['packages_dir'] = self.packages_dir


            # 3) trigger the package building thread
            PackageThread               = Package.Package()
            PackageThread.ObId          = pending_packages['_id']
            PackageThread.Debug         = self.debug    # set debug mode
            PackageThread.hereiam       = self.hereiam  # set path to this daemon
            PackageThread.Log           = self.log
            PackageThread.Package       = pending_packages
            PackageThread.start()

if __name__ == '__main__':
    jviBuilder = jviBuilder()
    daemon_runner = runner.DaemonRunner(jviBuilder)
    daemon_runner.do_action()