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

