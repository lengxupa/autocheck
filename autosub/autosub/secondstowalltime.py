def secondstowalltime(i):
	i=correction(i)
	return ("%d:%d0:00" %(i/3600,i%3600/600))
