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

class WebPublish:

    def __init__(self, sourceDir, intermediateDir, domain, password):
        self.sourceDir = sourceDir
        self.intermediateDir = intermediateDir
        self.domain = domain
        self.password = password
        
    def publish(self):
        sourceFiles = [ f for f in listdir(self.sourceDir) if isfile(join(self.sourceDir,f)) ]
                
        for source in sourceFiles:
            copyfile(join(self.sourceDir, source), join(self.intermediateDir, source))
            
        for source in sourceFiles:    
            file = open(join(self.intermediateDir, source), 'rb')
            session = ftplib.FTP("ftp.%s"%self.domain)
            session.login(self.domain, self.password)
            session.storbinary(join("STOR wwwroot\\", source), file)
            file.close()
            session.quit()

            webbrowser.open("http://www.%s/%s"%(self.domain, source))


