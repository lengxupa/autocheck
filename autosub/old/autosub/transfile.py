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
