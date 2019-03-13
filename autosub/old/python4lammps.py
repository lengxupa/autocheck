import os
import sys
from subprocess import call,Popen,PIPE
import glob
import string
import time 
import re
import numpy as np
import datetime 

#final transfer files and subjobs of calculation if job finished
def finaltransfer(files):
	for i in files:
		os.system("cat Species.dat* > %s" %i)
		os.system("cat x.bond* > %s" %i)
	writesublog('lg%s' %jbN)
	subjob('Sublog.sh')
	if(bondfile):
		writesubbond(('bd%s' %jbN),datafile)
		subjob('Subbond.sh')


#find quene by walltime & ppn
def findqueue(i,n):
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


#read input file
def rdin(i):
	src = file(i, "r+")
	in_dic={}
	com=0
	for line in src.readlines():
		ln=rdln(line)
		if(ln):
			ln=ln.split()
			in_dic[com]={}
			in_dic[com][ln[0]]=ln[1:]
			com+=1
	src.close()
	return in_dic


#eliminate strings after #
def rdln(i):
	content=i.strip().lstrip().rstrip(',').split('#',1)
	return content[0]


#read submit file
def rdsb(i):
	infile=''
	ppn=1
	src = file(i, "r+")
	for line in src.readlines():
		if(not(line.find('#PBS -l walltime='))):
			walltime=line[17:25].strip().lstrip().rstrip(',')
			total_seconds = walltimetoseconds(walltime)
		if(not(line.find('#PBS -N '))):
			jbN=line[8:24].strip().lstrip().rstrip(',')
		if(not(line.find('lmp')==-1 or line.find('<')==-1)):
			content=line.split('<')
			raw=content[1].strip().lstrip().rstrip(',').split(' ')
			infile=raw[0]
			if(not(line.find('mpirun -np ')==-1)):
				content=line.split('mpirun -np ')
				raw=content[1].strip().lstrip().rstrip(',').split(' ')
				ppn=eval(raw[0])
			else:
				ppn=1
	return total_seconds,jbN,infile,ppn


#walltime transfer from numbers to strings
def secondstowalltime(i):
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
	return ("%d:%d0:00" %(i/3600,i%3600/600))


#subidtomotherfile
def subidtomotherfile(jbID,jbN,pwd):
	os.system("cp ~/motherjob/motherjob.txt .")
	src=open('motherjob.txt',"r")
	des=open('mothertemp.txt',"w")
	des.writelines(src.read())
	src.close()
	des.write("%s %s %s\n" %(jbID,jbN,pwd))
	des.close()
	os.system("mv mothertemp.txt ~/motherjob/motherjob.txt")
	os.system("rm mother*.txt")


#sub jobs
def subjob(i):
	cmd=("qsub %s" %i)
	tst=Popen(cmd,shell=True, stdout=PIPE)
	outp,err=tst.communicate()
	print outp
	outp=outp.split('\n')
	for line in outp:
		if(line):
			if ord(line[0])>=48 and ord(line[0])<=57:
				content=line.split('.')
				jbID=content[0]
	walltimeo,jbN,infile,ppno=rdsb(i)
	cmd1=("pwd")
	tst1=Popen(cmd1,shell=True, stdout=PIPE)
	outp1,err1=tst1.communicate()
	print outp1
	pwd=outp1.split('\n')
	if(jbN[0]=='b' and jbN[1]=='d'):
		pwd[0]+='/bond'
	subidtomotherfile(jbID,jbN[0:15],pwd[0])


#transfer files if simulation interupted
def transfile(files,cnt):
	if cnt==1:
		os.system("cp log.lammps log%d.lammps" %cnt)
	else:
		os.system("mv log.lammps log%d.lammps" %cnt)
	for i in files:
		os.system("mv %s %s%d" %(i,i,cnt))


#nodes line write
def transnodes(ppno):
	if(not(ppno%16)):
		nodes=ppno/16
		ppn=16
	else:
		nodes=ppno/16+1
		if(nodes>1):
			ppn=16
		else:
			ppn=ppno
	return ("nodes=%d:ppn=%d" %(nodes,ppn))


#walltime transfer from strings to numbers
def walltimetoseconds(i):
	content=i.split(':')
	if eval(content[0])<24:
		pt =datetime.datetime.strptime(i,'%H:%M:%S')
		total_seconds = pt.second+pt.minute*60+pt.hour*3600
	else:
		total_seconds=eval(content[2])+eval(content[1])*60+eval(content[0])*3600
	return total_seconds


#write Subbond.sh file for bond calculation
def writesubbond(i,idata,edata):
	src = file('Subbond.sh', "w")
	src.write("#!/bin/tcsh\n")
	src.write("#PBS -l walltime=4:00:00\n")
	src.write("#PBS -l nodes=1:ppn=16\n")
	src.write("#PBS -N %s \n" %i)
	a=findqueue(14400,16)
	while(a):
		if(a=='debug' or a=='ncn' or a=='prism' or a=='standby' or a=='strachan'):
			break
		a=findqueue(14400,16)
	src.write("#PBS -q %s\n" %a)
	src.write("\n")
	src.write("set echo\n")
	src.write("\n")
	src.write("cd $PBS_O_WORKDIR\n")
	src.write("\n")
	src.write("unzip bond.zip\n")
	src.write("cp x.bond bond\n")
	src.write("cp *.data bond\n")
	src.write("cp *.reax bond\n")
	src.write("cd bond\n")
	src.write("cp %s x.data\n" %idata)
	src.write("module load lammps/15Feb16_impi-5.1.2.150\n")
	src.write("mpirun -np 16 lmp < findllmolid.in\n")
	src.write("\n")
	src.write("cp Pan.1.dump x.dump\n")
	src.write("cp %s x.data\n" %edata)
	src.write("module load lammps/15Feb16_impi-5.1.2.150\n")
	src.write("mpirun -np 16 lmp < findllmolid.in\n")
	src.write("\n")
	src.write("cp Pan.1.dump y.dump\n")
	src.write("module load matlab\n")
	src.write("matlab < newrerun.m > result.m\n")
	src.write("\n")
	src.write("mkdir home\n")
	src.write("cp *.png home\n")
	src.write("cp *file*.txt home\n")
	src.write("cp *.in home\n")
	src.write("cp ?.dump home\n")
	src.write("tar cvf home.tar home\n")
	src.write("matlab < newdataread.m > result.m\n")
	src.write("\n")
	src.write("mkdir structure\n")
	src.write("cp *.data structure\n")
	src.write("cp *.py structure\n")
	src.write("cp *.reax structure\n")
	src.write("cd structure\n")
	src.write("python strsub.py > states.out\n")
	src.write("\n")
	src.close()


#write sub log file
def writesublog(i):
	src = file('Sublog.sh', "w")
	src.write("#!/bin/bash\n")
	src.write("#PBS -l walltime=00:10:00\n")
	src.write("#PBS -l nodes=1:ppn=16\n")
	src.write("#PBS -N %s \n" %i)
	a=findqueue(600,16)
	while(a):
		if(a=='debug' or a=='ncn' or a=='prism' or a=='standby' or a=='strachan'):
			break
		a=findqueue(600,16)
	src.write("#PBS -q %s\n" %a)
	src.write("\n")
	src.write("set echo\n")
	src.write("\n")
	src.write("cd $PBS_O_WORKDIR\n")
	src.write("\n")
	src.write("unzip logresults.zip\n")
	src.write("cp *.dat* logresults\n")
	src.write("cp *.lammps logresults\n")
	src.write("cp *.in logresults\n")
	src.write("cp in.* logresults\n")
	src.write("cp *.txt logresults\n")
	src.write("cp logini.m logresults\n")
	src.write("cp *.sh logresults\n")
	src.write("cp *.reax logresults\n")
	src.write("cd logresults\n")
	src.write("cp *.in x.in\n")
	src.write("cp in.* x.in\n")
	src.write("module load matlab\n")
	src.write("matlab < logini.m > result.m\n")
	src.write("\n")
	src.write("mkdir home\n")
	src.write("cp *.png home\n")
	src.write("cp *.dat* home\n")
	src.write("cp *.in home\n")
	src.write("cp in.* home\n")
	src.write("cp *.lammps home\n")
	src.write("cp *.reax home\n")
	src.write("cp *.sh home\n")
	src.write("tar cvf home.tar home\n")
	src.write("cd ..\n")
	src.write("tar cvf logresults.tar logresults\n")
	src.write("\n")
	src.close()


#write sub.sh for lammps input
def writesublmp(subfile,walltimeo,jbN,infile,ppno):
	walltime=secondstowalltime(walltimeo)
	nodes=transnodes(ppno)
	src = file(subfile, "w")
	src.write("#!/bin/tcsh\n")
	src.write("#PBS -l walltime=%s\n" %walltime)
	src.write("#PBS -l %s\n" %nodes)
	src.write("#PBS -N %s\n" %jbN)
	a=findqueue(walltimeo,ppno)
	while(a):
		if(a=='debug' or a=='ncn' or a=='prism' or a=='standby' or a=='strachan'):
			if(ppno!=16 and a=='debug'):
				a=findqueue(walltimeo,ppno)
				continue
			break
		a=findqueue(walltimeo,ppno)
	src.write("#PBS -q %s\n" %a)
	src.write("\n")
	src.write("set echo\n")
	src.write("\n")
	src.write("cd $PBS_O_WORKDIR\n")
	src.write("module load lammps/15Feb16_impi-5.1.2.150\n")
	src.write("mpirun -np %d lmp < %s \n" %(ppno,infile))
	src.write("\n")

