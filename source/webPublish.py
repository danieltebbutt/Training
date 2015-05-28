# WebPublish for Dan's training application.
# This publishes a set of files to the web via an intermediate local directory.

import os
from database import Database
from exporter import Exporter
import webbrowser
from os import listdir
from os.path import isfile, join
from shutil import copyfile
import ftplib
import ConfigParser
import boto
from boto.s3.key import Key
import ntpath
import posixpath

class WebPublish:

    def __init__(self, sourceDir, intermediateDir, targetDir, domain, password, ):
        self.sourceDir = sourceDir
        self.intermediateDir = intermediateDir
        self.domain = domain
        self.password = password
        if targetDir == ".":
            self.targetDir = ""
        else:
            self.targetDir = targetDir
        
    def publish(self):
        sourceFiles = [ f for f in listdir(self.sourceDir) if isfile(join(self.sourceDir,f)) ]
        for source in sourceFiles:
            copyfile(join(self.sourceDir, source), join(self.intermediateDir, source))
          
        config = ConfigParser.ConfigParser()
        config.readfp(open('training.ini'))
        type = config.get("webPublish", "type")
        openAfter = (config.get("webPublish", "open_after") == "yes")
        destination = config.get("webPublish", "destination")

        if type == "FTP":
            session = ftplib.FTP("ftp.%s"%destination)
            session.login(self.domain, self.password)
            
        elif type == "AWS":
            s3 = boto.connect_s3()
            bucket = s3.get_bucket(destination)
                    
        for source in sourceFiles:    
            file = open(join(self.intermediateDir, source), 'rb')
            
            if type == "FTP":
                session.storbinary(join("STOR wwwroot\\", ntpath.join(self.targetDir, source)), file)
            elif type == "AWS":
                k = Key(bucket)                
                k.key = posixpath.join(self.targetDir,source)
                k.set_contents_from_file(file)
                
            if openAfter:
                if self.targetDir:
                    webbrowser.open("http://www.%s/%s"%(self.domain, source))
                else:
                    webbrowser.open("http://www.%s/%s/%s"%(self.domain, self.targetDir, source))
                    
            file.close()

        if type == "FTP":
            session.quit()
            
