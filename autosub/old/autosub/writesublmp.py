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

