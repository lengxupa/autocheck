import os
import sys
from subprocess import call,Popen,PIPE
import glob
import string
import time 
import re
import numpy as np
import datetime 

def write_sublmp(seconds,i,j,a,b,ifile):
	src = file('sub.sh', "w")
	src.write("#!/bin/tcsh\n")
	walltime=secondstowalltime(seconds)
	src.write("#PBS -l walltime=%s\n" %walltime)
	src.write("#PBS -l nodes=1:ppn=16\n")
	src.write("#PBS -N coo%s%s%s%s\n" %(b,a[:3],(j[:2]+j[-1]),i[-3:]))
	a=findqueue(seconds,16)
	while True:
		if(a=='debug' or a=='ncn' or a=='prism' or a=='standby' or a=='strachan'):
			break
		a=findqueue(seconds,16)
	src.write("#PBS -q %s\n" %a)
	src.write("\n")
	src.write("set echo\n")
	src.write("\n")
	src.write("cd $PBS_O_WORKDIR\n")
	src.write("module load intel impi/5.1.2.150 lammps/15Feb16\n")
	src.write("mpirun -np 16 lmp < %s\n" %ifile)
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
				if(k==5 and eval(dirc['Run'])>t):
					t=eval(dirc['Run'])
				if(k==6 and eval(dirc['Run'])==t):
					if(dirc==debug and eval(dirc['Queue'])==64):
						continue
					a=0
					return dirc['Name']
					break


def rdln(i):
	content=i.strip().lstrip().rstrip(',').split('#',1)
	return content[0]


def walltimetoseconds(i):
	content=i.split(':')
	if eval(content[0])<24:
		pt =datetime.datetime.strptime(i,'%H:%M:%S')
		total_seconds = pt.second+pt.minute*60+pt.hour*3600
	else:
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
	if(i/86400.0>1 and i/86400.0<=15):
		if(int(i)%86400 or int(i)!=i):
			i=(int(i)/86400+1)*86400
		else:
			i=int(i)
	if(i/86400.0>15):
		i=1209600
	return i


def secondstowalltime(i):
	i=correction(i)
	return ("%d:%d0:00" %(i/3600,i%3600/600))


def getwalltime(ifile):
	src=open(ifile,'r')
	i=src.readlines()[-1].split()[-1]
	seconds=walltimetoseconds(i)
	return seconds


def fixtocool(ifile,ofile):
	src=open(ifile,'r')
	des=open(ofile,'w')
	for line in src.readlines():
		ln=line.split()
		if ('fix' in ln) and ('npt' in ln):
			i=ln.index('aniso')
			ln[i]='x'
			s=(' z 1 1 %s #' %ln[i+3])
			ln[i+3]+=s
		des.write(' '.join(ln)+'\n')
	src.close()
	des.close()


def cool(i,j,a,b):
	if not os.path.exists('cool'):
		os.mkdir('cool')
		os.system('cp fix.in cool')
		os.system('cp step4.data cool/polymer_relax.data')
		os.system('cp log.lammps cool')
		if os.path.exists('param.qeq.pan'):
			os.system('cp param.qeq.pan cool')
		os.chdir('cool')
		fixtocool('fix.in','cool.in')
		walltime=getwalltime('log.lammps')
		write_sublmp(walltime,i,j,a,b,'cool.in')
		os.system('qsub sub.sh')
		os.chdir('..')


for i in ['PE43','PE45','PP']:
	os.chdir('%s' %i)
	for j in range(1):
		tit='yfix'+(str(j) if j!=0 else '')
		titnew='yfix'+str(j+1)
		if os.path.exists(titnew):
			continue
		os.mkdir(titnew)
		os.chdir('%s' %titnew)
		os.mkdir('input')
		os.system('cp ../%s/input/*.* input' %tit)
		os.chdir('input')
		for k in ['Gas','Qeq']:
			os.system('cp %sfix.in tmp.in' %k)
			fixtocool('tmp.in',('%sfix.in' %k))
		os.chdir('..')
		os.system('cp ../%s/buttondef.py .' %tit)
		os.system('cp ../%s/button.py .' %tit)
		os.chdir('..')
	os.chdir('..')

