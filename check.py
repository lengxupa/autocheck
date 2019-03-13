import os
import sys
from subprocess import call,Popen,PIPE
import glob
import string
import time 
import re
import numpy as np
import datetime 

def write_sublmp(seconds,i,j,aa,b,med,ifile):
	src = file('sub.sh', "w")
	src.write("#!/bin/tcsh\n")
	walltime=secondstowalltime(seconds)
	a=findqueue(seconds,16)
	while True:
		if(a=='debug' or a=='ncn' or a=='prism' or a=='standby' or a=='strachan'):
			break
		a=findqueue(seconds,16)
	if a=='standby' and seconds>14400:
		walltime='4:00:00'
	src.write("#PBS -l walltime=%s\n" %walltime)
	src.write("#PBS -l nodes=1:ppn=16\n")
	src.write("#PBS -N %s%s%s%s%s\n" %(med,b,aa[:3],(j[:2]+j[-1]),i[-3:]))
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
		if len(ln)==4 and ln[0]=='#velocity' and ln[1]=='1' and ln[2]=='zero':
			des.write(line[1:])
			continue
		if ('fix' in ln) and ('npt' in ln) and ('temp' in ln):
			i=ln.index('temp')
			ln[i+1]='800'
			ln[i+2]='300'
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
		write_sublmp(walltime,i,j,a,b,'coo','cool.in')
		os.system('qsub sub.sh')
		os.chdir('..')


def fixtocoollong(ifile,ofile):
	src=open(ifile,'r')
	des=open(ofile,'w')
	for line in src.readlines():
		ln=line.split()
		if len(ln)>3 and ln[0]=='#velocity' and ln[1]=='1' and ln[2]=='zero':
			des.write(line[1:])
			continue
		if ('fix' in ln) and ('npt' in ln) and ('temp' in ln):
			i=ln.index('temp')
			ln[i+1]='800'
			ln[i+2]='300'
		if ('md.*.dump' in ln):
			i=ln.index('md.*.dump')
			ln[i-1]='50000'
		if ('x.xyz' in ln):
			i=ln.index('x.xyz')
			ln[i-1]='50000'	
		if len(ln)>1 and ln[0]=='run':
			ln[1]='5000000'	
		des.write(' '.join(ln)+'\n')
	src.close()
	des.close()


def fixtocoollongG(ifile,ofile):
	src=open(ifile,'r')
	des=open(ofile,'w')
	for line in src.readlines():
		ln=line.split()
		if len(ln)>3 and ln[0]=='#velocity' and ln[1]=='1' and ln[2]=='zero':
			des.write(line[1:])
			continue
		if ('fix' in ln) and ('npt' in ln) and ('temp' in ln):
			i=ln.index('temp')
			ln[i+1]='800'
			ln[i+2]='20'
		if ('md.*.dump' in ln):
			i=ln.index('md.*.dump')
			ln[i-1]='50000'
		if ('Detailed.dump' in ln):
			ln[0]='#'
		if ('x.xyz' in ln):
			i=ln.index('x.xyz')
			ln[i-1]='50000'	
		if len(ln)>1 and ln[0]=='run':
			ln[1]='5000000'	
		des.write(' '.join(ln)+'\n')
	src.close()
	des.close()


def coollong(i,j,a,b):
	if not os.path.exists('coollong'):
		os.mkdir('coollong')
		os.system('cp fix.in coollong')
		os.system('cp step4.data coollong/polymer_relax.data')
		os.system('cp log.lammps coollong')
		if os.path.exists('param.qeq.pan'):
			os.system('cp param.qeq.pan coollong')
		os.chdir('coollong')
		fixtocoollong('fix.in','coollong.in')
		walltime=getwalltime('log.lammps')*10
		write_sublmp(walltime,i,j,a,b,'col','coollong.in')
		os.system('qsub sub.sh')
		os.chdir('..')
	if not os.path.exists('coollongG'):
		os.mkdir('coollongG')
		os.system('cp fix.in coollongG')
		os.system('cp step4.data coollongG/polymer_relax.data')
		os.system('cp log.lammps coollongG')
		if os.path.exists('param.qeq.pan'):
			os.system('cp param.qeq.pan coollongG')
		os.chdir('coollongG')
		fixtocoollongG('fix.in','coollong.in')
		walltime=getwalltime('log.lammps')*10
		write_sublmp(walltime,i,j,a,b,'coG','coollong.in')
		os.system('qsub sub.sh')
		os.chdir('..')


def coollongtoM(ifile,ofile,o):
	src=open(ifile,'r')
	des=open(ofile,'w')
	for line in src.readlines():
		ln=line.split()
		if ln and ln[0]=='group':
			continue
		if ln and ln[0]=='velocity':
			continue
		if ('fix' in ln) and ('rigid' in ln):
			continue
		if ('fix' in ln) and ('npt' in ln) and ('temp' in ln):
			ln[2]='all'
			i=ln.index('temp')
			ln[i+1]=str(o)
			ln[i+2]=str(o)
		des.write(' '.join(ln)+'\n')
	src.close()
	des.close()


def melting(i,j,a,b):
	if i=='PP':
		tmprange=range(320,560,20)
	else:
		tmprange=range(240,540,20)
	for o in tmprange:
		tit='M'+str(o)
		if not os.path.exists(tit):
			os.mkdir(tit)
			os.system('cp coollong.in %s' %tit)
			os.system('cp step4.data %s/polymer_relax.data' %tit)
			os.system('cp log.lammps %s' %tit)
			if os.path.exists('param.qeq.pan'):
				os.system('cp param.qeq.pan %s' %tit)
			os.chdir(tit)
			coollongtoM('coollong.in','melt.in',o)
			walltime=getwalltime('log.lammps')
			write_sublmp(walltime,i,j,a,b,('M'+str(o))[:3],'melt.in')
			os.system('qsub sub.sh')
			os.chdir('..')


def coollongtoV(ifile,ofile,o):
	src=open(ifile,'r')
	des=open(ofile,'w')
	for line in src.readlines():
		ln=line.split()
		if ln and ln[0]=='group':
			continue
		if ln and ln[0]=='velocity':
			ln[1]='all'
		if ('fix' in ln) and ('rigid' in ln):
			continue
		if ('fix' in ln) and ('npt' in ln) and ('temp' in ln):
			ln[2]='all'
			i=ln.index('temp')
			ln[i+1]=str(o)
			ln[i+2]=str(o)
		des.write(' '.join(ln)+'\n')
	src.close()
	des.close()


def meltingV(i,j,a,b):
	if i=='PP':
		tmprange=range(320,560,20)
	else:
		tmprange=range(240,540,20)
	for o in tmprange:
		tit='V'+str(o)
		if not os.path.exists(tit):
			os.mkdir(tit)
			os.system('cp coollong.in %s' %tit)
			os.system('cp step4.data %s/polymer_relax.data' %tit)
			os.system('cp log.lammps %s' %tit)
			if os.path.exists('param.qeq.pan'):
				os.system('cp param.qeq.pan %s' %tit)
			os.chdir(tit)
			coollongtoV('coollong.in','melt.in',o)
			walltime=getwalltime('log.lammps')
			write_sublmp(walltime,i,j,a,b,('V'+str(o))[:3],'melt.in')
			os.system('qsub sub.sh')
			os.chdir('..')


def coollongtoF(ifile,ofile,o):
	src=open(ifile,'r')
	des=open(ofile,'w')
	for line in src.readlines():
		ln=line.split()
		if ('fix' in ln) and ('npt' in ln) and ('temp' in ln):
			i=ln.index('temp')
			ln[i+1]=str(o)
			ln[i+2]=str(o)
		des.write(' '.join(ln)+'\n')
	src.close()
	des.close()


def meltingF(i,j,a,b):
	if i=='PP':
		tmprange=range(320,560,20)
	else:
		tmprange=range(240,540,20)
	for o in tmprange:
		tit='F'+str(o)
		if not os.path.exists(tit):
			os.mkdir(tit)
			os.system('cp coollong.in %s' %tit)
			os.system('cp step4.data %s/polymer_relax.data' %tit)
			os.system('cp log.lammps %s' %tit)
			if os.path.exists('param.qeq.pan'):
				os.system('cp param.qeq.pan %s' %tit)
			os.chdir(tit)
			coollongtoF('coollong.in','melt.in',o)
			walltime=getwalltime('log.lammps')
			write_sublmp(walltime,i,j,a,b,('F'+str(o))[:3],'melt.in')
			os.system('qsub sub.sh')
			os.chdir('..')


def coollongtoQ(ifile,ofile,o):
	src=open(ifile,'r')
	des=open(ofile,'w')
	for line in src.readlines():
		ln=line.split()
		if ln and ln[0]=='group':
			continue
		if ln and ln[0]=='velocity':
			ln[1]='all'
		if 'Detailed.dump' in ln:
			ln[0]='#'
		if ln and ln[0]=='run':
			des.write('fix               2 all qeq/shielded 100 10 1.0e-6 10000 param.qeq.pan\n')
			des.write('\n')
		if ('fix' in ln) and ('rigid' in ln):
			continue
		if ('fix' in ln) and ('npt' in ln) and ('temp' in ln):
			ln[2]='all'
			i=ln.index('temp')
			ln[i+1]=str(o)
			ln[i+2]=str(o)
		des.write(' '.join(ln)+'\n')
	src.close()
	des.close()


def meltingQ(i,j,a,b):
	if i=='PP':
		tmprange=range(320,560,20)
	else:
		tmprange=range(240,540,20)
	for o in tmprange:
		tit='Q'+str(o)
		if not os.path.exists(tit):
			os.mkdir(tit)
			os.system('cp coollong.in %s' %tit)
			os.system('cp step4.data %s/polymer_relax.data' %tit)
			os.system('cp log.lammps %s' %tit)
			os.chdir(tit)
			os.system('cp ../../../Qeq/param.qeq.pan .')
			coollongtoQ('coollong.in','melt.in',o)
			walltime=getwalltime('log.lammps')
			write_sublmp(walltime,i,j,a,b,('Q'+str(o))[:3],'melt.in')
			os.system('qsub sub.sh')
			os.chdir('..')


def fixtostable(ifile,ofile):
	src=open(ifile,'r')
	des=open(ofile,'w')
	for line in src.readlines():
		ln=line.split()
		if len(ln)==4 and ln[0]=='#velocity' and ln[1]=='1' and ln[2]=='zero':
			des.write(line[1:])
			continue
		if ('fix' in ln) and ('npt' in ln) and ('temp' in ln):
			i=ln.index('temp')
			ln[i+1]='800'
			ln[i+2]='800'
		des.write(' '.join(ln)+'\n')
	src.close()
	des.close()


def stable(i,j,a,b):
	if not os.path.exists('stable'):
		os.mkdir('stable')
		os.system('cp fix.in stable')
		os.system('cp step4.data stable/polymer_relax.data')
		os.system('cp log.lammps stable')
		if os.path.exists('param.qeq.pan'):
			os.system('cp param.qeq.pan stable')
		os.chdir('stable')
		if j[0]=='z':
			os.system('cp ../title.in .')
			os.system('cp ../ffield.txt .')
			os.system('cp ../group.txt .')
			os.system('cp ../%sstable.in .' %b)
			os.system('cp ../run.in .')
			os.system('cat title.in ffield.txt group.txt %sstable.in run.in > fix.in' %b)
		fixtostable('fix.in','stable.in')
		walltime=getwalltime('log.lammps')
		write_sublmp(walltime,i,j,a,b,'sta','stable.in')
		os.system('qsub sub.sh')
		os.chdir('..')


fixlist=['fix','xfix8','yfix1']
for i in ['PE45']:
	for j in fixlist:
		if not os.path.exists('%s/%s' %(i,j)):
			print i,j,'not exists'
			continue
		os.chdir('%s/%s' %(i,j))
		os.system('chmod 700 button.py')
		os.system('./button.py 5 5 180')
		os.chdir('structure')
		cwd = os.getcwd()
		for root, dirs, files in os.walk(cwd, topdown=False):
			rt=root.split('/')
			if len(rt)>11 and rt[11]=='Qeq':
				continue
			if (rt[-1]=='Gas') or (rt[-1]=='Qeq') or (rt[-1]=='new') or (rt[-1]=='cool') or (rt[-1]=='stable') or rt[-1][:8]=='coollong' or rt[-1][0]=='M' or rt[-1][0]=='V' or rt[-1][0]=='F':
				if ('step4.data' in files) and ('md.500000.dump' in files):
					if rt[-1]=='new' or rt[-1]=='cool' or rt[-1]=='stable' or rt[-1][:8]=='coollong' or rt[-1][0]=='M' or rt[-1][0]=='V' or rt[-1][0]=='F':
						print i,j,rt[9],rt[11],rt[-1],'success'
						if rt[-1]=='new' or rt[-1]=='stable':
							if rt[-1]=='new' and j in ['yfix']:
								os.chdir(root)
								stable(i,j,rt[9],rt[11])
								coollong(i,j,rt[9],rt[11])
								os.chdir(cwd)
							else:
								os.chdir(root)
								cool(i,j,rt[9],rt[11])
								coollong(i,j,rt[9],rt[11])
								os.chdir(cwd)
						if rt[-1][:8]=='coollong':
							os.chdir(root)
							meltingV(i,j,rt[9],rt[11])
							meltingQ(i,j,rt[9],rt[11])
							os.chdir(cwd)
					else:
						print i,j,rt[9],rt[11],'success'
						if j not in (['xfix'+str(xfix) for xfix in range(4,8)]+['xfix'+str(xfix) for xfix in range(12,16)]+['zfix']+['zfix'+str(xfix) for xfix in range(1,4)]):
							os.chdir(root)
							cool(i,j,rt[9],rt[11])
							coollong(i,j,rt[9],rt[11])
							os.chdir(cwd)
						else:
							os.chdir(root)
							stable(i,j,rt[9],rt[11])
							os.chdir(cwd)
				else:
					a=1
					if not ((rt[-1]=='new') and ('step4.data' in files)):
						for k in files:
							if ('.o' in k) or ('.e' in k):
								a=0
								if (rt[-1]=='cool') or (rt[-1]=='new') or rt[-1]=='stable' or rt[-1][:8]=='coollong' or rt[-1][0]=='M' or rt[-1][0]=='V' or rt[-1][0]=='F':
									print i,j,rt[9],rt[11],rt[-1],'failed'
								else:
									print i,j,rt[9],rt[11],'failed'
								break
						if a:
							if (rt[-1]=='cool') or (rt[-1]=='new') or rt[-1]=='stable' or rt[-1][:8]=='coollong' or rt[-1][0]=='M' or rt[-1][0]=='V' or rt[-1][0]=='F':
								print i,j,rt[9],rt[11],rt[-1],'continuing'
							else:
								print i,j,rt[9],rt[11],'continuing'
		os.chdir('../../..')

		