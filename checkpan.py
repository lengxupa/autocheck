import os
import sys
from subprocess import call,Popen,PIPE
import glob
import string
import time 
import re
import numpy as np
import datetime 

def grabprocessors(ifile):
	src=open(ifile)
	for line in src.readlines():
		ln=line.split()
		if ln and ln[0]=='read_data':
			datafile=ln[1]
			break
	src.close()
	Dir=read_data(datafile)
	atoms=Dir['atoms']
	if 'bonds' in Dir:
		return atoms/2000+1
	else:
		return atoms/1000+1


def correctppn(ppn):
	nodes=ppn/16+1 if (ppn/16 and ppn%16) else ppn/16 if ppn/16 else 1
	if not ppn/16:
		ppn=16 if ppn>8 else 8 if ppn>4 else 4 if ppn>2 else 2 if ppn>1 else 1
	return nodes,16 if ppn/16 else ppn, nodes*16 if ppn/16 else ppn


def write_sublmp(seconds,tac,tit,i,j,ifile):
	src = file('sub.sh', "w")
	src.write("#!/bin/tcsh\n")
	walltime=secondstowalltime(seconds)
	ppn=grabprocessors(ifile)
	nodes,ppn,np=correctppn(ppn)
	a=findqueue(seconds,np)
	while True:
		if(a=='debug' or a=='ncn' or a=='prism' or a=='standby' or a=='strachan'):
			break
		a=findqueue(seconds,np)
	if a=='standby' and seconds>14400:
		walltime='4:00:00'
	src.write("#PBS -l walltime=%s\n" %walltime)
	src.write("#PBS -l nodes=%d:ppn=%d\n" %(nodes,ppn))
	src.write('#PBS -l naccesspolicy=shared\n')
	src.write("#PBS -N %s%s%s%s%s\n" %(ifile[:3],j,i,tit[:3],tac))
	src.write("#PBS -q %s\n" %a)
	src.write("\n")
	src.write("set echo\n")
	src.write("\n")
	src.write("cd $PBS_O_WORKDIR\n")
	src.write("module load intel impi/5.1.2.150 lammps/15Feb16\n")
	src.write("mpirun -np %d lmp < %s\n" %(np,ifile))
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
					if(n!=16 and dirc==debug):
						continue
					a=0
					return dirc['Name']
					break
				if(k==2 and eval(dirc['Free'])>=n and eval(dirc['Queue'])<eval(dirc['Free'])):
					if(n!=16 and dirc==debug):
						continue
					if(dirc==debug and eval(dirc['Queue'])+eval(dirc['Run'])>=64):
						continue
					a=0
					return dirc['Name']
					break
				if(k==3 and eval(dirc['Free'])>=n):
					if(n!=16 and dirc==debug):
						continue
					if(dirc==debug and eval(dirc['Queue'])+eval(dirc['Run'])>=64):
						continue
					a=0
					return dirc['Name']
					break
				if(k==4 and eval(dirc['Queue'])==0):
					if(n!=16 and dirc==debug):
						continue
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
			if not (ln[0][0].isdigit() or ln[0][0]=='-'):
				s=' '.join(ln)
				Dir[s]={}
			if s and (ln[0][0].isdigit() or ln[0][0]=='-'):
				Dir[s][eval(ln[0])]=[eval(i) for i in ln[1:]]
	src.close()
	return Dir


def getwalltime(ifile):
	src=open(ifile,'r')
	i=src.readlines()[-1].split()[-1]
	seconds=walltimetoseconds(i)
	return seconds


def getlogwalltime(ifile):
	src=open(ifile)
	for line in src.readlines():
		ln=line.split()
		if len(ln)>9 and ln[0]=='Loop' and ln[1]=='time':
			seconds=eval(ln[3])
			steps=eval(ln[8])
			break
	return float(seconds)/steps


def npt(po,fi,le,ch):
	ret=0
	new=ch
	if not os.path.exists(new):
		os.mkdir(new)
		ret=1
		if os.path.exists('param.qeq.pan'):
			os.system('cp param.qeq.pan %s' %new)
		if os.path.exists('jp1080302_si_001.reax'):
			os.system('cp jp1080302_si_001.reax %s' %new)
		os.system('cp %s.in %s' %(new,new))
		dumprange=range(0,1000000,10000) if new=='npt' else range(0,10000000,10000)
		for j in dumprange[::-1]:
			if os.path.exists('md.%d.dump' %j) and (not checkfile('md.%d.dump' %j)):
				break
		t=j
		dump2data('polymer_relax.data',('md.%d.dump' %t),('%s/polymer_relax.data' %new))
		for j in dumprange:
			if os.path.exists('md.%d.dump' %j) and (not checkfile('md.%d.dump' %j)):
				break
		sta=j
		os.chdir(new)
		ter2=1000000 if new=='npt' else 10000000
		ste2=10000
		heatcontinue('%s.in' %new,'%stmp.in' %new,t,ste2)
		walltime=float(getsubwalltime('../sub.sh'))/(t-sta)*(ter2-t)
		os.system('cp %stmp.in %s.in' %(new,new))
		write_sublmp(walltime,po,fi,le,new[:3],'%s.in' %new)
		os.system('qsub sub.sh')
	return ret


def subequi(po,fi,le,ch,m=''):
	ret=0
	new='equi'
	if os.path.exists(new):
		if not os.path.exists(new+'/jp1080302_si_001.reax'):
			os.system('rm -r equi')
	if not os.path.exists(new):
		ret=1
		os.mkdir(new)
		if m=='mai':
			os.system('cp /scratch/conte/s/shen276/20171018/PAN/input/equi2.in %s/equi.in' %new)
		else:
			os.system('cp /scratch/conte/s/shen276/20171018/PAN/input/equi.in %s' %new)
		os.system('cp /scratch/conte/s/shen276/20171018/PAN/input/Dreiding_data2ReaxFF_data.py %s' %new)
		os.system('cp step4.data %s' %new)
		os.system('cp /scratch/conte/s/shen276/20171018/PAN/input/jp1080302_si_001.reax %s' %new)
		os.chdir(new)
		os.system('python Dreiding_data2ReaxFF_data.py step4.data polymer_relax.data')
		walltime=4*60*60
		write_sublmp(walltime,po,fi,le,'equ','equi.in')
		os.system('qsub sub.sh')
	return ret


def subfurther(po,fi,le,ch):
	ret=0
	if ch=='mai':
		new='maintain'
	if ch=='rel':
		new='release'
	if not os.path.exists(new):
		ret=1
		os.mkdir(new)
		os.system('cp npt.in %s' %new)
		os.system('cp step4.data %s/polymer_relax.data' %new)
		if os.path.exists('param.qeq.pan'):
			os.system('cp param.qeq.pan %s' %new)
		walltime=getlogwalltime('log.lammps')*1000000
		os.chdir(new)
		if ch=='mai':
			furthercontinue('npt.in','npttmp.in',0,10000,300)
		if ch=='rel':
			furthercontinue('npt.in','npttmp.in',0,10000,300,1)
		os.system('cp npttmp.in npt.in')
		write_sublmp(walltime,po,fi,le,ch,'npt.in')
		os.system('qsub sub.sh')
	return ret


def substretch(po,fi,le,ch):
	ret=0
	new='stretch'
	if not os.path.exists(new):
		ret=1
		os.mkdir(new)
		os.system('cp npt.in %s' %new)
		os.system('cp step4.data %s/polymer_relax.data' %new)
		if os.path.exists('param.qeq.pan'):
			os.system('cp param.qeq.pan %s' %new)
		walltime=getlogwalltime('log.lammps')*1000000
		os.chdir(new)
		for i in [400,450]:
			for j in [2,3]:
				tit=str(i)+'K_2'+'0'*j+'atm'
				if not os.path.exists(tit):
					os.mkdir(tit)
				stretchcontinue('npt.in',tit+'/npt.in',0,10000,i,-eval('2'+'0'*j))
				os.system('cp polymer_relax.data %s' %tit)
				if os.path.exists('param.qeq.pan'):
					os.system('cp param.qeq.pan %s' %tit)
				os.chdir(tit)
				write_sublmp(walltime,po,fi,le,str(i)[:2]+str(j),'npt.in')
				os.system('qsub sub.sh')
				os.chdir('..')
	return ret


def furthercontinue(ifile,ofile,t,ste,te,pr=''):
	end=1000000
	src=open(ifile,'r')
	des=open(ofile,'w')
	dump=1
	for line in src.readlines():
		ln=line.split()
		if ln and ln[0]=='reset_timestep':
			ln[1]=str(t)
		if ('fix' in ln) and ('npt' in ln) and ('temp' in ln):
			i=ln.index('temp')
			ln[i+1]=str(te)
			ln[i+2]=str(te)
			del ln[i+4:]
			if pr or pr==0:
				ln.append('x 1 1 1000 y 1 1 1000 z %s %s 1000' %(pr,pr))
			else:
				ln.append('x 1 1 1000 y 1 1 1000')
		if dump:
			if ln and ln[0]=='run':
				ln[1]=str(end-t)
		des.write(' '.join(ln)+'\n')
	src.close()
	des.close()


def stretchcontinue(ifile,ofile,t,ste,te,pr):
	end=1000000
	src=open(ifile,'r')
	des=open(ofile,'w')
	dump=1
	for line in src.readlines():
		ln=line.split()
		if ln and ln[0]=='reset_timestep':
			ln[1]=str(t)
		if ('fix' in ln) and ('npt' in ln) and ('temp' in ln):
			i=ln.index('temp')
			ln[i+1]=str(te)
			ln[i+2]=str(te)
			del ln[i+4:]
			ln.append('x 1 1 1000 y 1 1 1000 z %s %s 1000' %(pr,pr))
		if dump:
			if ln and ln[0]=='run':
				ln[1]=str(end-t)
		des.write(' '.join(ln)+'\n')
	src.close()
	des.close()


def substress(po,fi,le,ch):
	ret=0
	if os.path.exists('finish'):
		return ret
	new='stress'
	root=os.getcwd()
	rt=root.split('/')
	for i in [400,450]:
		for j in [2,3]:
			if str(i)+'K_2'+'0'*j+'atm' in rt:
				ch=str(i)[1]+str(j)+('m' if 'maintain' in rt else 'l')
	if not os.path.exists(new):
		os.mkdir(new)
		os.system('cp /scratch/conte/s/shen276/20171018/PAN/input/stress.in %s' %new)
		os.system('cp step2.data %s/polymer_relax.data' %new)
		os.system('cp /scratch/conte/s/shen276/20171018/PAN/input/jp1080302_si_001.reax %s' %new)
		walltime=getlogwalltime('log.lammps')*10000000
		os.chdir(new)
		write_sublmp(walltime,po,fi,le,ch,'stress.in')
		os.system('qsub sub.sh')
	return ret


def equi(po,fi,le,ch):
	ret=0
	new='equi'
	if not os.path.exists(new):
		os.mkdir(new)
		ret=1
		if os.path.exists('jp1080302_si_001.reax'):
			os.system('cp jp1080302_si_001.reax %s' %new)
		os.system('cp equi.in %s' %new)
		dumprange=range(0,50000,10000)
		for j in dumprange[::-1]:
			if os.path.exists('md.%d.dump' %j) and (not checkfile('md.%d.dump' %j)):
				break
		t=j
		dump2data('polymer_relax.data',('md.%d.dump' %t),('%s/polymer_relax.data' %new))
		for j in dumprange:
			if os.path.exists('md.%d.dump' %j) and (not checkfile('md.%d.dump' %j)):
				break
		sta=j
		os.chdir(new)
		ter2=50000
		ste2=10000
		equicontinue('equi.in','equitmp.in',t,ste2)
		walltime=float(getsubwalltime('../sub.sh'))/(t-sta)*(ter2-t)
		os.system('cp equitmp.in equi.in')
		write_sublmp(walltime,po,fi,le,'equ','equi.in')
		os.system('qsub sub.sh')
	return ret


def equicontinue(ifile,ofile,t,ste):
	end=50000
	src=open(ifile,'r')
	des=open(ofile,'w')
	dump=1
	for line in src.readlines():
		ln=line.split()
		if 'qeq/reax' in ln:
			des.write(' '.join(ln)+'\n')
			des.write('\n')
			des.write('reset_timestep %d\n' %t)
			des.write('\n')
			dump=0
			continue
		if 'npt' in ln:
			dump=1
		if dump:
			if ln and ln[0]=='run':
				ln[1]=str(end-t)
			des.write(' '.join(ln)+'\n')
	src.close()
	des.close()


def getsubwalltime(ifile):
	src=open(ifile,'r')
	i=src.readlines()[1].split()[-1].split('=')[1]
	seconds=walltimetoseconds(i)
	return seconds


def heatcontinue(ifile,ofile,t,ste):
	if ifile[:3]=='npt':
		end=1000000
	else:
		end=10000000
	src=open(ifile,'r')
	des=open(ofile,'w')
	dump=1
	for line in src.readlines():
		ln=line.split()
		if ln and ln[0]=='dump':
			if dump:
				des.write('reset_timestep %d\n' %t)
				des.write('dump 1 all atom %d mdz.dump\n' %(end/10000))
				des.write('dump	       d3 all custom %d md.*.dump id type x y z vx vy vz\n' %ste)
				dump=0
			continue
		if ln and ln[0]=='reset_timestep':
			continue
		if ln and ln[0]=='run':
			ln[1]=str(end-t)
		des.write(' '.join(ln)+'\n')
	src.close()
	des.close()


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
		if len(ln)==8:
			Dir['Atoms'][eval(ln[0])][3]=eval(ln[2])
			Dir['Atoms'][eval(ln[0])][4]=eval(ln[3])
			Dir['Atoms'][eval(ln[0])][5]=eval(ln[4])
			Dir['Velocities'][eval(ln[0])][0]=eval(ln[5])
			Dir['Velocities'][eval(ln[0])][1]=eval(ln[6])
			Dir['Velocities'][eval(ln[0])][2]=eval(ln[7])
	src.close()
	write_data(Dir,ofile)


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
				des.write(str(i)+' '+' '.join([str(j) for j in Dir[key][i]])+'\n')
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


suc=open('check/checkpansuctemp.txt','w')
fai=open('check/checkpanfaitemp.txt','w')
os.chdir('PAN/structure')
cwd = os.getcwd()
tit=[]
for i in [400,450]:
	for j in [2,3]:
		tit.append(str(i)+'K_2'+'0'*j+'atm')
for root, dirs, files in os.walk(cwd, topdown=False):
	rt=root.split('/')
	if rt[-1] in ['npt','maintain','release']+tit:
		if 'step4.data' in files:
			print rt[8],rt[9],rt[10],'npt','success'
			os.chdir(root)
			if 'stretch' not in rt:
				if subequi(rt[8],rt[9],rt[10],'equ') or substretch(rt[8],rt[9],rt[10],'dra'):	
					suc.write(' '.join([rt[8],rt[9],rt[10],'npt','success'])+'\n')
					suc.write(root+'\n')
			else:
				if ('maintain' not in rt) and ('release' not in rt):
					if subfurther(rt[8],rt[9],rt[10],'mai') or subfurther(rt[8],rt[9],rt[10],'rel'):
						suc.write(' '.join([rt[8],rt[9],rt[10],'npt','success'])+'\n')
						suc.write(root+'\n')
				elif 'release' in rt:
					if subequi(rt[8],rt[9],rt[10],'equ'):	
						suc.write(' '.join([rt[8],rt[9],rt[10],'npt','success'])+'\n')
						suc.write(root+'\n')
				elif 'maintain' in rt:
					if subequi(rt[8],rt[9],rt[10],'equ','mai'):	
						suc.write(' '.join([rt[8],rt[9],rt[10],'npt','success'])+'\n')
						suc.write(root+'\n')
		else:
			a=1
			for k in files:
				if '.o' in k:
					a=0
					print rt[8],rt[9],rt[10],'npt','failed'
					os.chdir(root)
					if npt(rt[8],rt[9],rt[10],'npt'):
						os.chdir(root)
						fai.write(' '.join([rt[8],rt[9],rt[10],'npt','failed'])+'\n')
						ERR=open(k).readlines()[-1]
						fai.write((ERR if ERR[:5]=='ERROR' else 'timeout\n'))
						fai.write(root+'\n')
					break
			if a:
				print rt[8],rt[9],rt[10],'npt','continuing'
	if rt[-1] in ['equi']:
		if 'step2.data' in files:
			print rt[8],rt[9],rt[10],'equi','success'
			os.chdir(root)
			if substress(rt[8],rt[9],rt[10],'str'):	
				suc.write(' '.join([rt[8],rt[9],rt[10],'equi','success'])+'\n')
				suc.write(root+'\n')
		else:
			a=1
			for k in files:
				if '.o' in k:
					a=0
					print rt[8],rt[9],rt[10],'equi','failed'
					os.chdir(root)
					if equi(rt[8],rt[9],rt[10],'equi'):
						os.chdir(root)
						fai.write(' '.join([rt[8],rt[9],rt[10],'equi','failed'])+'\n')
						ERR=open(k).readlines()[-1]
						fai.write((ERR if ERR[:5]=='ERROR' else 'timeout\n'))
						fai.write(root+'\n')
					break
			if a:
				print rt[8],rt[9],rt[10],'equi','continuing'
	if len(rt)>11 and (rt[-1] in ['stress']):
		if 'step3.data' in files:
			print rt[8],rt[9],rt[10],'stress','success'
		else:
			a=1
			for k in files:
				if '.o' in k:
					a=0
					print rt[8],rt[9],rt[10],'stress','failed'
					os.chdir(root)
					if npt(rt[8],rt[9],rt[10],'stress'):
						os.chdir(root)
						fai.write(' '.join([rt[8],rt[9],rt[10],'stress','failed'])+'\n')
						ERR=open(k).readlines()[-1]
						fai.write((ERR if ERR[:5]=='ERROR' else 'timeout\n'))
						fai.write(root+'\n')
					break
			if a:
				print rt[8],rt[9],rt[10],'stress','continuing'
