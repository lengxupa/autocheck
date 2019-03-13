subfile='Submit_Lammps.sh'
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

