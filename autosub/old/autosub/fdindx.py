def fdindx(i):
	tmpc="find -maxdepth 1 -name log.lammps | xargs grep TotEng"
	tstt=Popen(tmpc,shell=True,stdout=PIPE)
	outpt,err=tstt.communicate()
	print outpt
	if(outpt):
		content=outpt.split(' ')
		return content.index(i)
	else:
		return False

