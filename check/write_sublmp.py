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
