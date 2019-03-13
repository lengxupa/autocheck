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
	src.write("#PBS -l walltime=%s\n" %walltime)
	src.write("#PBS -l nodes=1:ppn=16\n")
	src.write("#PBS -N %s%s%s%s%sAA\n" %(med[:3],b[:3],aa[:3],(j[:2]+j[-1]),i[-3:]))
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
		tmprange=range(300,540,20)
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
		tmprange=range(300,540,20)
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
		tmprange=range(300,540,20)
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


def subcontinue(po,fi,ta,te,rt,jud):
	ns=['5ns','10ns','20ns','50ns','100ns','200ns','500ns']
	if rt in ns:
		if rt==ns[-1]:
			return 0
		new=ns[ns.index(rt)+1]
		sta=eval(ns[ns.index(rt)-1][:-2])*1000000
		ter=eval(rt[:-2])*1000000
		ste=(ter-sta)/100
	else:
		new=ns[1]
		sta=0
		ter=5000000
		ste=50000
	dumprange=range(((sta/ste+(1 if sta%ste else 0))*ste),ter,ste)
	if not os.path.exists(new):
		os.mkdir(new)
		os.system('cp melt.in %s' %new)
		os.system('cp param.qeq.pan %s' %new)
		if jud:
			for j in dumprange:
				if os.path.exists('md.%d.dump' %j) and (not checkfile('md.%d.dump' %j)):
					continue
				break
			t=j-ste
			dump2data('polymer_relax.data',('md.%d.dump' %t),('%s/polymer_relax.data' %new))
		else:
			t=ter
			Dir=read_data('step4.data')
			write_data(Dir,('%s/polymer_relax.data' %new))
		os.system('cp log.lammps %s' %new)
		os.chdir(new)
		ter2=eval(new[:-2])*1000000
		ste2=(ter2-ter)/100
		meltcontinue('melt.in',('melt%s.in' %new),t,ste2)
		if jud:
			walltime=float(getsubwalltime('../sub.sh'))/(t-sta)*(ter2-t)
		else:
			walltime=float(getwalltime('log.lammps'))/(t-sta)*(ter2-t)
		os.system('cp melt%s.in melt.in' %new)
		write_sublmp(walltime,po,fi,ta,te,new,'melt.in')
		os.system('qsub sub.sh')


def getsubwalltime(ifile):
	src=open(ifile,'r')
	i=src.readlines()[1].split()[-1].split('=')[1]
	seconds=walltimetoseconds(i)
	return seconds


def dump2data(datafile,dumpfile,ofile):
	Dir=read_data(datafile)
	src=open(dumpfile)
	box='x'
	for line in src.readlines():
		ln=line.split()
		if len(ln)==2 and ln[0]!='ITEM:':
			Dir[box+'lo']=eval(ln[0])
			Dir[box+'hi']=eval(ln[1])
			if box=='x':
				box='y'
				continue
			if box=='y':
				box='z'
				continue
			continue
		if len(ln)==5:
			Dir['Atoms'][eval(ln[0])][3]=Dir['xlo']+(Dir['xhi']-Dir['xlo'])*eval(ln[2])
			Dir['Atoms'][eval(ln[0])][4]=Dir['ylo']+(Dir['yhi']-Dir['ylo'])*eval(ln[3])
			Dir['Atoms'][eval(ln[0])][5]=Dir['zlo']+(Dir['zhi']-Dir['zlo'])*eval(ln[4])
	src.close()
	write_data(Dir,ofile)


def meltcontinue(ifile,ofile,t,ste):
	end=eval(ofile.split('.')[0][4:-2])*1000000
	src=open(ifile,'r')
	des=open(ofile,'w')
	for line in src.readlines():
		ln=line.split()
		if ln and ln[0]=='dump' and ln[1]=='2':
			ln[0]='#'
		if ln and ln[0]=='dump' and ln[1]=='3':
			ln[4]=str(ste)
		if ln and ln[0]=='dump' and ln[1]=='4':
			ln[4]=str(ste)
		if ln and ln[0]=='reset_timestep':
			ln[1]=str(t)
		if ln and ln[0]=='run':
			ln[1]=str(end-t)
		des.write(' '.join(ln)+'\n')
	src.close()
	des.close()


def read_data(ifile):
	Dir={}
	Box={}
	Masses={}
	src=open(ifile,'r')
	a=1
	s=''
	for line in src.readlines():
		if a:
			a=0
			continue
		ln=line.split('#')[0].split()
		if ln:
			if len(ln)>1 and ln[0].isdigit() and (not ln[1].isdigit()) and (not s):
				Dir[' '.join(ln[1:])]=eval(ln[0])
			if len(ln)==4 and ln[2][1:]=='lo' and ln[3][1:]=='hi':
				Dir[ln[2]]=eval(ln[0])
				Dir[ln[3]]=eval(ln[1])
			if not ln[0][0].isdigit():
				s=' '.join(ln)
				Dir[s]={}
			if s and ln[0][0].isdigit():
				Dir[s][eval(ln[0])]=[eval(i) for i in ln[1:]]
	src.close()
	return Dir


def write_data(Dir,ofile):
	des=open(ofile,'w')
	des.write('LAMMPS data file via Tongtong\n')
	des.write('\n')
	for i in ['atom','bond','angle','dihedral','improper']:
		if (i+'s') in Dir:
			des.write('%d %s\n' %(Dir[i+'s'],(i+'s')))
			des.write('%d %s\n' %(Dir[i+' types'],(i+' types')))
	des.write('\n')
	for i in ['x','y','z']:
		des.write('%f %f %s %s\n' %(Dir[i+'lo'],Dir[i+'hi'],(i+'lo'),(i+'hi')))
	des.write('\n')
	for key in ['Masses','Pair Coeffs','Bond Coeffs','Angle Coeffs','Dihedral Coeffs','Improper Coeffs','Atoms','Velocities','Bonds','Angles','Dihedrals','Impropers']:
		if key in Dir and len(Dir[key])>0:
			des.write(key+'\n')
			des.write('\n')
			for i in Dir[key]:
				des.write(str(i)+' '+' '.join(str(j) for j in Dir[key][i])+'\n')
			des.write('\n')
	des.close()


def checkfile(ifile):
	src=open(ifile,'r')
	li=0
	for line in src.readlines():
		li+=1
		break
	if li:
		return 0
	else:
		return 1


fixlist=['fix','xfix8','yfix1']
for i in ['PE45']:
	for j in fixlist:
		os.chdir('%s/%s' %(i,j))
		cwd = os.getcwd()
		for root, dirs, files in os.walk(cwd, topdown=False):
			rt=root.split('/')
			if len(rt)>13 and rt[13][0]=='Q' and (rt[-1][0]=='Q' or rt[-1][-2:]=='ns'):
				if rt[9]=='m2m10':
					continue
				if ('step4.data' in files):
					print i,j,rt[9],rt[13],(rt[-1] if len(rt)>14 else '5ns'),'success'
					os.chdir(root)
					subcontinue(i,j,rt[9],rt[13],rt[-1],checkfile('step4.data'))
				else:
					a=1
					for k in files:
						if ('.o' in k) or ('.e' in k):
							a=0
							print i,j,rt[9],rt[13],(rt[-1] if len(rt)>14 else '5ns'),'failed'
							os.chdir(root)
							subcontinue(i,j,rt[9],rt[13],rt[-1],1)
							break
					if a:
						print i,j,rt[9],rt[13],(rt[-1] if len(rt)>14 else '5ns'),'continuing'
		os.chdir(cwd)
		os.chdir('../..')
	