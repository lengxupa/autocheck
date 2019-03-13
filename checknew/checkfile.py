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