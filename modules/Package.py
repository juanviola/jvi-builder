import urllib2
import threading
import os, sys
import subprocess
import shlex
import smtplib
import yaml
import datetime
import inspect
import shutil

"""
  'description': 'This is my app source', 
  'url': 'http://my-url.to.my.source/my-app-source.tar.gz', 
  'type': 'web', 
  'version': '1', 
  'release': '1', 
  'name': 'my-app-name',
  'opts': 'environment=production example_path=/tmp/example example_name=MyExampleNameVar'
"""

class Package(threading.Thread):
    Log           = None
    Name          = None
    Debug         = 1
    Package       = ()
    hereiam       = None
    ObId          = None

    def run(self):
        self.autoconf()
        self.Name = threading.currentThread().getName()
        self.logthis('run', data="%s" %self.Package)

        if self.Debug>0: self.logthis('run', data="ObId: %s | type: %s" %(self.ObId, type(self.ObId)))

        # import mongo
        import JviMongo

        try:
            jvimongo = JviMongo.JviMongo(log=self.Log, debug=1)
        except (RuntimeError, TypeError, NameError, ValueError) as e:
            self.log.Log("jviBuilder::main: error %s" %e)

        # download file
        if self.download()==True:
            if self.build()==True:
                self.delete_downloaded_file()
                jvimongo.mongo_update(collection_name='packages', mongo_id=self.ObId, data={'builded': 1, 'end_on': datetime.datetime.now()})
            else:
                jvimongo.mongo_update(collection_name='packages', mongo_id=self.ObId, data={'end_on': datetime.datetime.now()})

        return True 

    def autoconf(self):
        hereiam = os.path.realpath(os.path.abspath(os.path.split(inspect.getfile( inspect.currentframe() ))[0]))
        if self.hereiam + '/modules' not in sys.path: sys.path.insert(0, self.hereiam + '/modules')
        if self.Debug>0: self.logthis('autoconf', data="hereiam: %s | path: %s" %(hereiam, sys.path))

    def download(self):
        self.logthis('download', data="starting download of %s" %self.Package['url'])

        if not os.path.isdir(self.Package['download_dir']):
            try:
                os.makedirs(self.Package['download_dir'])
            except Exception as e:
                self.logthis('download', msg_type='error', data="%s" %e)
                pass

        try:
            if os.path.isfile("%s/%s" %(self.Package['download_dir'], os.path.basename(self.Package['url']))):
                self.logthis('download', data="file {%s/%s} already exists, skipping download" %(self.Package['download_dir'],os.path.basename(self.Package['url'])))
                return True

            download_request = urllib2.Request(url=self.Package['url'])
            download_socket  = urllib2.urlopen(download_request)

            with open("%s/%s" %(self.Package['download_dir'], os.path.basename(self.Package['url'])), "wb") as f:
                bytes = download_socket.read(100)
                while bytes != '':
                    f.write(bytes)
                    bytes = download_socket.read(100)
                self.logthis('download', data="file saved to %s/%s" %(self.Package['download_dir'], os.path.basename(self.Package['url'])))
            return True
        except (urllib2.HTTPError,ValueError) as e:
            self.logthis('download', msg_type='error', data="%s" %e)
            pass
            return False

    def logthis(self, fcn_name='logthis', msg_type='info', data=None):
        # Package::get_env_from_name::Thread-1: This is a logging message
        self.Log.Log("Package::%s::%s: %s" %(fcn_name, threading.currentThread().getName(), data), msg_type="%s" %msg_type)

    def delete_downloaded_file(self):
        try:
            if os.path.isfile("%s/%s" %(self.Package['download_dir'], os.path.basename(self.Package['url']))):
                os.remove("%s/%s" %(self.Package['download_dir'], os.path.basename(self.Package['url'])))
            self.logthis('delete_downloaded_file', data="temporary file {%s} deleted" %(os.path.basename(self.Package['url'])))
        except (ValueError, OSError) as e:
            self.logthis('delete_downloaded_file', msg_type='error', data="%s" %e)
            pass

    def build(self):
        self.logthis('build', data="starting building process for {%s}" %self.Package['name'])

        if not os.path.isdir(self.Package['building_dir']):
            try:
                os.makedirs(self.Package['building_dir'])
            except Exception as e:
                self.logthis('build', msg_type='error', data="%s" %e)
                pass

        if not os.path.isdir(self.Package['packages_dir']):
            try:
                os.makedirs(self.Package['packages_dir'])
            except Exception as e:
                self.logthis('build', msg_type='error', data="%s" %e)
                pass

        try:
            makefile_dir = self.Package['type']
        except KeyError as e:
            self.logthis('build', msg_type='error', data="%s" %e)
            pass

        build_makefile_source = "%s/makefiles/%s" %(self.Package['hereiam'], makefile_dir)
        
        cmd = 'make name="%s" version="%s" release="%s" description="%s" source="%s/%s" download_dir="%s" building_dir="%s" ' \
            'packages_dir="%s" %s' \
            %(self.Package['name'], self.Package['version'], self.Package['release'], 
                self.Package['description'], self.Package['download_dir'], os.path.basename(self.Package['url']), 
                self.Package['download_dir'], self.Package['building_dir'], self.Package['packages_dir'], self.Package['opts'])
        
        self.logthis('build', data="%s" %cmd)

        try:
            proccess = subprocess.Popen(shlex.split(cmd), cwd=build_makefile_source, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return_code = proccess.wait()

            if return_code!=0:
                for line in proccess.stderr.read().split('\n'):
                    if len(line)>0:
                        self.logthis('build', msg_type='error', data="%s" %line)
                return False
            
            self.logthis('build', data="Package Builded Successfully {%s}" %self.Package['name'])

            return True
            
        except (OSError,ValueError) as e:
            self.logthis('build', msg_type='error', data="%s" %e)
            return False    

    def send_mail(self, smtp='smtp', subject="Report", body="Here Goes The Body"):
        try:
            with open('%s/config/jvibuilder.yaml' %(self.hereiam), 'r') as f:
                self.doc = yaml.load(f)
        except (ValueError, IOError, KeyError) as e: 
            self.logthis('send_mail', msg_type='error', data="%s" %e)
            pass

        try:
            session = smtplib.SMTP(self.doc[smtp]['host'], self.doc[smtp]['port'])
            session.ehlo()
            session.starttls()
            session.login(self.doc[smtp]['user'], self.doc[smtp]['pass'])
            headers = "\r\n".join(["from: " + self.doc['sender']['from_name'] + ' ' + self.doc['sender']['from_addr'],
                    "subject: " + subject,
                    "to: " + self.doc['recipients']['to_addr'],
                    "mime-version: 1.0",
                    "content-type: text/html"])

            # body_of_email can be plaintext or html!                    
            content = headers + "\r\n\r\n" + body
            session.sendmail(self.doc[smtp]['user'], self.doc['recipients']['to_addr'].split(), content)
            self.logthis('send_mail', data="Subject:{%s} Smtp:{%s} email was sent" %(subject,smtp))
        except smtplib.SMTPDataError as e:
            self.logthis('send_mail', msg_type='error', data="%s" %e)
            pass