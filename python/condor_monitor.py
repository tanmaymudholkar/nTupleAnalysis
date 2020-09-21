import os
import subprocess
import time
import re
from commandLineHelpers import *

class condor_job:
    def __init__(self, schedd, ID):
        self.schedd = schedd
        self.ID = ID
        self.done = False
        self.line = ''
    
    def check(self):
        if self.done: return self.line

        command = 'condor_tail -maxbytes 256 -name {n} {id}'.format(n=self.schedd, id=self.ID)
        # args = ['/usr/local/bin/condor_tail','-maxbytes 256', '-name %s'%self.schedd, self.ID]
        res = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True, executable="/bin/bash")
        res.wait()
        if res.returncode:
            self.done = True
            line = '%s %10s >> %s'%(self.schedd, self.ID, 'FINISHED')
            return line
        tail = res.stdout.read()

        # args = ['/usr/local/bin/condor_tail','-maxbytes 256', '-name %s'%self.schedd, self.ID]
        # res = subprocess.Popen(args, stdout=subprocess.PIPE)
        # res.wait()
        # if res.returncode:
        #     self.done = True
        #     line = '%s %10s >> %s'%(self.schedd, self.ID, 'FINISHED')
        #     return line
        # tail = res.stdout.read()

        # res = os.popen('condor_tail -maxbytes 256 -name %s %s'%(self.schedd, self.ID))
        # tail = res.read()
        # if res.close():
        #     self.done=True
        #     self.line = '%s %10s >> %s'%(self.schedd, self.ID, 'FINISHED')
        #     return self.line

        split = re.split('\n\r',tail)
        line = tail.encode('string-escape')
        line = line.split(r'\n')[-1]
        line = line.split(r'\r')[-1]
        line = str(line)
        self.line = '%s %10s >> %s'%(self.schedd, self.ID, line)

        time.sleep(0.1)
        return self.line

    def watch(self, timeout=1):
        start = time.time()
        while time.time()-start < timeout:
            line = self.check()
            if self.done:
                break
            sys.stdout.write('\r'+line)
            sys.stdout.flush()
            #print split[-1]
            
        
def get_jobs():
    USER = getUSER()
    q = os.popen('condor_q').read()
    lines = q.split('\n')
    jobs = []
    for line in lines:
        split = line.split()
        if not split: continue
        if "-- Schedd:" in line:
            schedd = split[2]
        if "dagman" in line: continue
        if USER == split[1]:
            ID = split[0]
            print schedd, ID
            jobs.append( condor_job(schedd, ID) )
    print
    print '-'*20
    return jobs

    

jobs = get_jobs()

nDone=0
nJobs=len(jobs)
while nDone < nJobs:
    nDone = 0
    print "\033[K"
    for job in jobs:
        if job.done: 
            nDone += 1
        print "\033[K"+job.check()
    moveCursorUp(nJobs+1)
moveCursorDown(1000)
    


