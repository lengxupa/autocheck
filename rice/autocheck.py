import os
import sys
from subprocess import call,Popen,PIPE
import glob
import string
import time 
import re
import numpy as np
import datetime 

def write_autocheck():
	seconds=1800
	src = file('sub.sh', "w")
	src.write("#!/bin/tcsh\n")
	walltime=secondstowalltime(seconds)
	src.write("#PBS -l walltime=%s\n" %walltime)
	src.write("#PBS -l nodes=1:ppn=20\n")
	src.write("#PBS -N autocheck\n")
	src.write("#PBS -q debug\n")
	src.write("\n")
	src.write("set echo\n")
	src.write("\n")
	src.write("cd $PBS_O_WORKDIR\n")
	src.write("python autocheck.py\n")
	src.write("\n")
	src.close()


def findqueue(i,n):
	i=correction(i)
	while True:
		cmd="ssh conte /usr/pbs/bin/qlist"
		tst=Popen(cmd,shell=True, stdout=PIPE)
		outp,err=tst.communicate()
		print outp
		if(not(err)):
			break	
	outplala=outp.split('\n')
	for line in outplala:
		ln=rdln(line)
		if(ln):
			line=ln
		else:
			continue
		if(ord(line[0])>=97 and ord(line[0])<=123):
			ln=line.replace(',', '')
			content=ln.split(' ',1)
			raw=content[1].strip().lstrip().rstrip(',').split(' ',1)
			raw2=raw[1].strip().lstrip().rstrip(',').split(' ',1)
			raw3=raw2[1].strip().lstrip().rstrip(',').split(' ',1)
			raw4=raw3[1].strip().lstrip().rstrip(',').split(' ',1)
			raw5=raw4[1].strip().lstrip().rstrip(',').split(' ',1)
			list1=[]
			if(content[0]=='debug'):
				debug={'Name': content[0], 'Total': raw[0], 'Queue': raw2[0],'Run':raw3[0],'Free':raw4[0],'Max Walltime':walltimetoseconds(raw5[0])}
			if(content[0]=='ncn'):
				ncn={'Name': content[0], 'Total': raw[0], 'Queue': raw2[0],'Run':raw3[0],'Free':raw4[0],'Max Walltime':walltimetoseconds(raw5[0])}
			if(content[0]=='prism'):
				prism={'Name': content[0], 'Total': raw[0], 'Queue': raw2[0],'Run':raw3[0],'Free':raw4[0],'Max Walltime':walltimetoseconds(raw5[0])}
			if(content[0]=='standby'):
				standby={'Name': content[0], 'Total': raw[0], 'Queue': raw2[0],'Run':raw3[0],'Free':raw4[0],'Max Walltime':walltimetoseconds(raw5[0])}
			if(content[0]=='strachan'):
				strachan={'Name': content[0], 'Total': raw[0], 'Queue': raw2[0],'Run':raw3[0],'Free':raw4[0],'Max Walltime':walltimetoseconds(raw5[0])}
	a=1
	k=0
	t=0
	while(a):
		k+=1
		for dirc in (debug,ncn,prism,standby,strachan):
			if(i<=dirc['Max Walltime']):
				if(eval(dirc['Free'])>=n and eval(dirc['Queue'])==0):
					a=0
					if(n!=16 and dirc==debug):
						continue
					return dirc['Name']
					break
				if(k==2 and eval(dirc['Free'])>=n and eval(dirc['Queue'])<eval(dirc['Free'])):
					if(dirc==debug and eval(dirc['Queue'])+eval(dirc['Run'])>=64):
						continue
					a=0
					return dirc['Name']
					break
				if(k==3 and eval(dirc['Free'])>=n):
					if(dirc==debug and eval(dirc['Queue'])+eval(dirc['Run'])>=64):
						continue
					a=0
					return dirc['Name']
					break
				if(k==4 and eval(dirc['Queue'])==0):
					a=0
					return dirc['Name']
					break
				if k==5:
					a=0
					break
	return 'standby'


def rdln(i):
	content=i.strip().lstrip().rstrip(',').split('#',1)
	return content[0]


def walltimetoseconds(i):
	content=i.split(':')
	if eval(content[0])<24:
		pt =datetime.datetime.strptime(i,'%H:%M:%S')
		total_seconds = pt.second+pt.minute*60+pt.hour*3600
	else:
		for t in range(3):
			if content[t][0]=='0':
				content[t]=content[t][1:]
		total_seconds=eval(content[2])+eval(content[1])*60+eval(content[0])*3600
	return total_seconds


def correction(i):
	if(i<=600):
		i=600
	if(i>600 and i<=1200):
		i=1200
	if(i>1200 and i<=1800):
		i=1800
	if(i>1800 and i<=3600):
		i=3600
	if(i/3600.0>1 and i/3600.0<=12):
		if(int(i)%3600 or int(i)!=i):
			i=(int(i)/3600+1)*3600
		else:
			i=int(i)
	if(i/3600.0>12 and i/3600.0<=24):
		i=86400
	if(i/86400.0>1 and i/86400.0<=14):
		if(int(i)%86400 or int(i)!=i):
			i=(int(i)/86400+1)*86400
		else:
			i=int(i)
	if(i/86400.0>14):
		i=1209600
	return i


def secondstowalltime(i):
	i=correction(i)
	return ("%d:%d0:00" %(i/3600,i%3600/600))


start = time.time()
os.system('qsub sub.sh')
os.chdir('/scratch/rice/s/shen276/halstead')
t=time.strftime("%Y_%m_%d_%H_%M_%S", time.localtime())
des=open(('check/check.'+t),'w')
jobs=[]
src=open('jobs.txt')
for line in src.readlines():
	ln=line.split()
	if ln:
		jobs.append(ln[0])
src.close()
ofile=open('jobsnew.txt','w')
cwd=os.getcwd()
for Root, Dirs, Files in os.walk(cwd, topdown=False):
	Rt=Root.split('/')
	if Rt[-1]!='halstead' and Rt[-1]!='check':
		if Rt[-1] not in jobs:
			os.chdir(Root)
			os.system('qsub sub.sh')
			ofile.write(Rt[-1]+'\n')
			continue
		a=1
		for k in Files:
			if '.o' in k:
				a=0
				os.chdir(Root)
				des.write(Root+'\n')
				if os.path.exists('des.txt'):
					os.system('scp *.* shen276@halstead.rcac.purdue.edu:%s' %(open('des.txt').readlines()[0]))
				else:
					des.write('des.txt error\n')
				jobs.remove(Rt[-1])
				os.chdir('..')
				os.system('rm -r %s' %Rt[-1])
				break
		if a:
			ofile.write(Rt[-1]+'\n')
ofile.close()
des.close()
stop=time.time()
os.chdir('/scratch/rice/s/shen276/halstead')
os.system('mv jobsnew.txt jobs.txt')
while (stop-start)<1500:
	stop=time.time()

