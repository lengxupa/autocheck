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

