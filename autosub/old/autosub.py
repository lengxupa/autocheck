import os
import sys
from subprocess import call,Popen,PIPE
import glob
import string
import time 
import re
import numpy as np
import datetime 

def walltimetoseconds(i):
	content=i.split(':')
	if eval(content[0])<24:
		pt =datetime.datetime.strptime(i,'%H:%M:%S')
		total_seconds = pt.second+pt.minute*60+pt.hour*3600
	else:
		total_seconds=eval(content[2])+eval(content[1])*60+eval(content[0])*3600
	return total_seconds


#read files
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


#for subfiles
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


def rdln(i):
	content=i.strip().lstrip().rstrip(',').split('#',1)
	return content[0]


def rdin(i):
	read_restart=''
	rsto=-1
	rstt=-1
	rsti=-1
	rstfile=''
	datafile=''
	thermo=-1
	every=1
	delay=0
	check='no'
	timestep=1
	Tstart=0
	Tend=0
	speciesfile=''
	bondfile=''
	deformscale=1
	src = file(i, "r+")
	for line in src.readlines():
		ln=rdln(line)
		if(ln):
			if(not(ln.find('read_restart'))):
				content=ln.split(' ',1)
				raw=content[1].strip().lstrip().rstrip(',').split(' ',1)
				read_restart=raw[0]
				raw2=raw[0].split('.')
				rsto=eval(raw2[raw2.index('rst')-1])
			if(not(ln.find('read_data'))):
				rsto=0
			if(not(ln.find('reset_timestep'))):
				content=ln.split(' ',1)
				raw=content[1].strip().lstrip().rstrip(',').split(' ',1)
				rsto=eval(raw[0])
			if(not(line.strip().lstrip().rstrip(',').find('write_data'))):
				content=ln.split(' ',1)
				raw=content[1].strip().lstrip().rstrip(',').split(' ',1)
				datafile=raw[0]
			if(not(ln.find('thermo '))):
				content=ln.split(' ',1)
				raw=content[1].strip().lstrip().rstrip(',').split(' ',1)
				thermo=eval(raw[0])
			if(not(ln.find('neigh_modify'))):
				content=ln.split(' ',1)
				raw=content[1].strip().lstrip().rstrip(',').find('every')
				if(not(raw==-1)):
					raw2=content[1].strip().lstrip().rstrip(',').split('every',1)
					raw3=raw2[1].strip().lstrip().rstrip(',').split(' ',1)
					every=eval(raw3[0])
				raw=content[1].strip().lstrip().rstrip(',').find('delay')
				if(not(raw==-1)):
					raw2=content[1].strip().lstrip().rstrip(',').split('delay',1)
					raw3=raw2[1].strip().lstrip().rstrip(',').split(' ',1)
					delay=eval(raw3[0])
				raw=content[1].strip().lstrip().rstrip(',').find('check')
				if(not(raw==-1)):
					raw2=content[1].strip().lstrip().rstrip(',').split('check',1)
					raw3=raw2[1].strip().lstrip().rstrip(',').split(' ',1)
					check=raw3[0]
			if(not(ln.find('timestep '))):
				content=ln.split(' ',1)
				raw=content[1].strip().lstrip().rstrip(',').split(' ',1)
				timestep=eval(raw[0])
			if(not(ln.find('fix '))):
				if(not(ln.find('temp ')==-1)):
					content=ln.split('temp ',1)
					raw=content[1].strip().lstrip().rstrip(',').split(' ',1)
					Tstart=eval(raw[0])
					raw2=raw[1].strip().lstrip().rstrip(',').split(' ',1)
					Tend=eval(raw2[0])
				if(not(ln.find('reax/c/species ')==-1)):
					content=ln.split('reax/c/species ',1)
					raw=content[1].strip().lstrip().rstrip(',').split(' ',1)
					raw2=raw[1].strip().lstrip().rstrip(',').split(' ',1)
					every=eval(raw2[0])
					delay=0
					raw3=raw2[1].strip().lstrip().rstrip(',').split(' ',1)
					raw4=raw3[1].strip().lstrip().rstrip(',').split(' ',1)
					speciesfile=raw4[0]
				if(not(ln.find('reax/c/bonds ')==-1)):
					content=ln.split('reax/c/bonds ',1)
					raw=content[1].strip().lstrip().rstrip(',').split(' ',1)
					raw2=raw[1].strip().lstrip().rstrip(',').split(' ',1)
					bondfile=raw2[0]
				if(not(ln.find('deform ')==-1)):
					if(not(ln.find('scale ')==-1)):
						content=ln.split('scale ',1)
						raw=content[1].strip().lstrip().rstrip(',').split(' ',1)
						deformscale=eval(raw[0])
			if(not(ln.find('restart '))):
				content=ln.split(' ',1)
				raw=content[1].strip().lstrip().rstrip(',').split(' ',1)
				rsti=eval(raw[0])
				raw2=raw[1].strip().lstrip().rstrip(',').split('.',1)
				rstfile=raw2[0]
			if(not(ln.find('run '))):
				content=ln.split(' ',1)
				raw=content[1].strip().lstrip().rstrip(',').split(' ',1)
				rstt=eval(raw[0])+rsto
	src.close()
	return read_restart,rsto,rstt,rsti,rstfile,datafile,thermo,every,delay,check,timestep,Tstart,Tend,speciesfile,bondfile,deformscale


#write files
def writesubbond(i,datafile):
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
	src.write("cp End_R*.data x.data\n")
	src.write("module load lammps/15Feb16_impi-5.1.2.150\n")
	src.write("mpirun -np 16 lmp < findllmolid.in\n")
	src.write("\n")
	src.write("cp Pan.1.dump x.dump\n")
	src.write("cp %s x.data\n" %datafile)
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


#transfer files
def transfile(cnt):
	if cnt==1:
		os.system("cp log.lammps log%d.lammps" %cnt)
	else:
		os.system("mv log.lammps log%d.lammps" %cnt)
	if(speciesfile):
		os.system("mv %s temp.txt" %speciesfile)
		os.system("mv temp.txt Species.dat%d" %cnt)
	if(bondfile):
		os.system("mv %s temp.txt" %bondfile)
		os.system("mv temp.txt x.bond%d" %cnt)


#subidtomotherfile
def subidtomotherfile(jbID,jbN,pwd):
	os.system("cp /home/shen276/motherjob/motherjob.txt motherjob.txt")
	src=open('motherjob.txt',"r")
	des=open('mothertemp.txt',"w")
	des.writelines(src.read())
	src.close()
	des.write("%s %s %s\n" %(jbID,jbN,pwd))
	des.close()
	os.system("mv mothertemp.txt /home/shen276/motherjob/motherjob.txt")
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


def finaltransfer():
	os.system("cat Species.dat* > %s" %speciesfile)
	os.system("cat x.bond* > %s" %bondfile)
	writesublog('lg%s' %jbN)
	subjob('Sublog.sh')
	if(bondfile):
		writesubbond(('bd%s' %jbN),datafile)
		subjob('Subbond.sh')


#write files
def rplcfl(infl,s1,s2):
	open('temp.txt', 'w').write(re.sub(r'%s' %s1, s2, open(infl).read()))
	src = file("temp.txt", "r+")
	des = file(infl, "w+")
	des.writelines(src.read())
	src.close()
	des.close()
	os.system("rm temp.txt")


def writelogini(cnt):
	s=open('logini.m','w')
	s.writelines("global i;\n")
	if(cnt==1):
		s.writelines("smooth=1;\n")
	else:
		s.writelines("smooth=0;\n")
	s.writelines("i=%d;\n" %cnt)
	s.writelines("run logresults.m;\n")
	s.close()


def winfile(infile,read_restart,rsto,rstt,rsti,rstfile,datafile,thermo,every,delay,check,timestep,Tstart,Tend,deformscale):
	os.system("cp %s temp2.txt" %infile)
	src = file('temp2.txt', "r+")
	for line in src.readlines():
		ln=rdln(line)
		if(line.strip().lstrip().rstrip(',').find('write_data')!=-1):
			if(line.strip().lstrip().rstrip(',').find(datafile)!=-1):
				if(not(line.strip().lstrip().rstrip(',').find('write_data'))):
					if(rstt!=rsteo):
						rplcfl(infile,line,'#%s' %line)
				else:
					if(rstt==rsteo):
						rplcfl(infile,line,'write_data %s \n' %datafile)
			else:
				rplcfl(infile,line,'#%s' %line)
		if(line.strip().lstrip().rstrip(',').find('read_restart')!=-1):
			if(read_restart):
						rplcfl(infile,line,'read_restart %s \n' %read_restart)
		if(ln):			
			if(not(ln.find('read_data'))):
				if(read_restart):
					rplcfl(infile,line,'#%s' %line)
			if(not(ln.find('reset_timestep'))):
				content=ln.split(' ',1)
				raw=content[1].strip().lstrip().rstrip(',').split(' ',1)
				if(rstr!=eval(raw[0])):
					rplcfl(infile,line,'reset_timestep %d \n' %rstr)
			if(not(ln.find('thermo '))):
				content=ln.split(' ',1)
				raw=content[1].strip().lstrip().rstrip(',').split(' ',1)
				if(thermo!=eval(raw[0])):
					rplcfl(infile,line,'thermo %d \n' %thermo)
			if(not(ln.find('neigh_modify'))):
				rplcfl(infile,line,'neigh_modify every %d delay %d check %s \n' %(every,delay,check))
			if(not(ln.find('fix '))):
				if(not(ln.find('temp ')==-1)):
					content=ln.split('temp ',1)
					raw=content[1].strip().lstrip().rstrip(',').split(' ',1)
					raw2=raw[1].strip().lstrip().rstrip(',').split(' ',1)
					if(Tstart!=eval(raw[0]) or Tend!=eval(raw2[0])):
						rplcfl(infile,line,'%stemp %f %f %s \n' %(content[0],Tstart,Tend,raw2[1]))
				if(not(ln.find('reax/c/species ')==-1)):
					content=ln.split('reax/c/species ',1)
					raw=content[1].strip().lstrip().rstrip(',').split(' ',1)
					raw2=raw[1].strip().lstrip().rstrip(',').split(' ',1)
					if(every!=eval(raw2[0])):
						rplcfl(infile,line,'%sreax/c/species %s %d %s \n' %(content[0],raw[0],every,raw2[1]))
				if(not(ln.find('deform ')==-1)):
					if(not(ln.find('scale ')==-1)):
						content=ln.split('scale ',1)
						raw=content[1].strip().lstrip().rstrip(',').split(' ',1)
						if(deformscale!=eval(raw[0])):
							rplcfl(infile,line,'%sscale %d %s \n' %(content[0],deformscale,raw[1]))
			if(not(ln.find('restart '))):
				content=ln.split(' ',1)
				raw=content[1].strip().lstrip().rstrip(',').split(' ',1)
				raw2=raw[1].strip().lstrip().rstrip(',').split('.',1)
				if(rsti!=eval(raw[0]) and rstfile==raw2[0]):
					rplcfl(infile,line,'restart %d %s.*.rst \n' %(rsti,rstfile))
			if(not(ln.find('run '))):
				content=ln.split(' ',1)
				raw=content[1].strip().lstrip().rstrip(',').split(' ',1)
				if(rstt!=(eval(raw[0])+rsto)):
					rplcfl(infile,line,'run %d \n' %(rstt-rsto))
	src.close()
	os.system("rm temp2.txt")
	

#rerun set
def rerun():
	stsc=True
	t=time.strftime("%Y%m%d%H%M%S", time.localtime())
	os.system("mkdir error%s" %t)
	os.system("cp *.* error%s" %t)
	os.system("rm *.lammps")
	os.system("cp ini.txt %s" %infile)
	os.system("rm *.txt")
	os.system("rm %s.*.rst" %rstfile)
	os.system("rm *.dump")
	os.system("rm Species.dat*")
	os.system("rm x.bond*")
	os.system("rm %s" %speciesfile)
	os.system("rm %s" %bondfile)
	read_restart,rstr,rsteo,rstio,rstfile,datafile,thermoo,everyo,delayo,checko,timestep,Tstarto,Tendo,speciesfile,bondfile,deformscaleo=rdin(infile)
	if(thermoo==1 and everyo==1 and delayo==0 and checko=='yes'):
		if(ppno>16):
			ppno=16
		else:
			if(ppno!=1):
				ppno/=2
			else:
				stsc=False
	else:
		ppno=16
	thermo=every=1
	delay=0
	check='yes'
	stsc=True
	rste=rsteo
	rsti=rstio
	thermo=thermoo
	every=everyo
	delay=delayo
	check=checko
	Tstart=Tstarto
	Tend=Tendo
	deformscale=deformscaleo
	winfile(infile,read_restart,rstr,rste,rsti,rstfile,datafile,thermo,every,delay,check,timestep,Tstart,Tend,deformscale)
	return stsc


#temperature check
def fdindx(i):
	tmpc="find -maxdepth 1 -name log.lammps | xargs grep TotEng"
	tstt=Popen(tmpc,shell=True,stdout=PIPE)
	outpt,err=tstt.communicate()
	print outpt
	if(outpt):
		content=outpt.split(' ')
		return content.index(i)
	else:
		return False		


def fdln(i):
	tmpc=("sed -n '/%s/=' log.lammps" %i)
	tstt=Popen(tmpc,shell=True,stdout=PIPE)
	outpt,err=tstt.communicate()
	print outpt
	return eval(outpt)


def tmpchk(i):
	a=fdindx('Temp')
	if(a):
		cmd=("sed '1,%dd' log.lammps" %fdln('Temp'))
		tst=Popen(cmd,shell=True,stdout=PIPE)
		outp,err=tst.communicate()
		print outp
		src = open("temp.txt", "w+")
		src.writelines(outp)
		src.close()
		cmd2=("find -maxdepth 1 -name temp.txt | xargs grep %d" %i)
		tst2=Popen(cmd2,shell=True,stdout=PIPE)
		outp2,err2=tst2.communicate()
		print outp2
		if(outp2):
			src = open("temp2.txt", "w+")
			src.writelines(outp2)
			src.close()
			b = np.loadtxt('temp2.txt')
			return b[a]<4000
		else:
			return False
		os.system("rm temp.txt")
		os.system("rm temp2.txt")
	else:
		return False


def scanstandard(outp2):
	ln=rdln(outp2)
	content=ln.split('Loop time of ',1)
	raw=content[1].strip().lstrip().rstrip(',').split(' on ',1)
	raw2=raw[1].strip().lstrip().rstrip(',').split(' procs for ',1)
	raw3=raw2[1].strip().lstrip().rstrip(',').split(' steps with ',1)
	return eval(raw[0]),eval(raw2[0]),eval(raw3[0])


def autosub(subfile):
	walltimeo,jbN,infile,ppno=rdsb(subfile)
	writesublmp(subfile,walltimeo,jbN,infile,ppno)
	walltimes=walltime=walltimeo
	ppns=ppn=ppno
	read_restart,rstro,rsteo,rstio,rstfile,datafile,thermoo,everyo,delayo,checko,timestep,Tstarto,Tendo,speciesfile,bondfile,deformscaleo=rdin(infile)
	stsc=True
	k=rstr=rstro
	rste=rsteo
	rsti=rstio
	thermo=thermoo
	every=everyo
	delay=delayo
	check=checko
	Tstart=Tstarto
	Tend=Tendo
	steps=rsteo-rstr
	deformscale=deformscaleo
	while stsc: 
		cmd=("qstat -u shen276 | grep %s" %jbN)
		tst=Popen(cmd,shell=True, stdout=PIPE)
		outp,err=tst.communicate()
		print "queue check",outp
		if(not outp):
			cnt=0
			while True:
				cnt+=1
				if(not(os.path.exists('log%d.lammps' %cnt))):
					break
			if(os.path.exists(datafile)):
				transfile(cnt)
				writelogini(cnt)
				finaltransfer()
				stsc=False
				break
			else:
				if(cnt==1):
					os.system("cp %s ini.txt" %infile)
				if(os.path.exists('log.lammps')):
					errc="find . -name log.lammps | xargs grep ERROR"
					tste=Popen(errc,shell=True, stdout=PIPE)
					outpe,err=tste.communicate()
					print "error check",outpe
					if(outpe):
						if(every==1 and thermo==1):
							if(ppn==1):
								stsc=rerun()
								continue
							if(ppn==2):
								ppn=1
							if(ppn==4):
								ppn=2
							if(ppn==8):
								ppn=4
							if(ppn==16):
								ppn==8
							if(ppn>16 or ppn%2!=0):
								ppn=16
						if(every==1 and thermo==10):
							thermo=1
						if(every==10 and thermo==10):
							every=1
							delay=0
							check='yes'
						if(every==10 and thermo==100):
							thermo=10
						if(every==100):
							every=10
							delay=10
					k=rstr
					for i in range(rstr+rsti,rste+rsti,rsti):
						rstc=("find . -name *.%d.rst" %i)
						tstr=Popen(rstc,shell=True, stdout=PIPE)
						outpr,err=tstr.communicate()
						print outpr
						if(not outpr):
							break
						k=i
					for i in range(k,rstr-rsti,-rsti):
						if(tmpchk(i)):
							break
					k=i
					if(rstr<k):
						rstr=k
						if(k==rste):
							if(not(rste%rstio)):
								rsti=rstio
								rste=rsteo
							else:
								rsti*=10
								rste=(rste/(10*rsti)+1)*10*rsti
						else:
							if(not(outpe) and rsti==rstio):
								rsti=rsti
							else:
								if(rsti>=10):
									rsti/=10
								if(rsti<(rstio/10)):
									if(not(rstr%10)):
										rste=(rstr/(rsti*100)+1)*100*rsti
									else:
										rste=(rstr/10+1)*10
					else:
						if(rsti==1):
							if(every==1 and thermo==1):
								if(ppn==1):
									stsc=rerun()
									continue
								if(ppn==2):
									ppn=1
								if(ppn==4):
									ppn=2
								if(ppn==8):
									ppn=4
								if(ppn==16):
									ppn==8
								if(ppn>16 or ppn%2!=0):
									ppn=16
							if(every==1 and thermo==10):
								thermo=1
							if(every==10 and thermo==10):
								every=1
								delay=0
								check='yes'
							if(every==10 and thermo==100):
								thermo=10
							if(every==100):
								every=10
								delay=10
						if(rsti>=10):
							rsti/=10
						if(rsti<(rstio/10)):
							if(not(rstr%10)):
								rste=(rstr/(rsti*100)+1)*100*rsti
							else:
								rste=(rstr/10+1)*10
					Tstart=float(Tstarto)+(float(rstr)-float(rstro))/(float(rsteo)-float(rstro))*(float(Tendo)-float(Tstarto))
					Tend=float(Tstarto)+(float(rste)-float(rstro))/(float(rsteo)-float(rstro))*(float(Tendo)-float(Tstarto))
					if(deformscaleo==1):
						deformscale=1
					else:
						deformscale=((float(deformscaleo)-1.0)/(float(rsteo)-float(rstro))*(float(rste)-float(rstro))+1.0)/((float(deformscaleo)-1.0)/(float(rsteo)-float(rstro))*(float(rstr)-float(rstro))+1.0)
					transfile(cnt)
					cmd2=("find . -name log.lammps | xargs grep %s" %'"Loop time of "')
					tst2=Popen(cmd2,shell=True, stdout=PIPE)
					outp2,err=tst2.communicate()
					print outp2
					if(outp2):
						walltimes,ppns,steps=scanstandard(outp2)
					read_restart=('%s.%d.rst' %(rstfile,rstr))
					winfile(infile,read_restart,rstr,rste,rsti,rstfile,datafile,thermo,every,delay,check,timestep,Tstart,Tend,deformscale)
					walltime=float((rste-rstr))/float(steps)*float(walltimes)/float(ppn)*float(ppns)
					writesublmp(subfile,walltime,jbN,infile,ppn)
				subjob(subfile)
		time.sleep(600)
		
