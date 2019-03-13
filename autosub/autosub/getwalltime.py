def getwalltime(ifile):
	src=open(ifile,'r')
	i=src.readlines()[-1].split()[-1]
	seconds=walltimetoseconds(i)
	return seconds