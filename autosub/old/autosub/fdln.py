def fdln(i):
	tmpc=("sed -n '/%s/=' log.lammps" %i)
	tstt=Popen(tmpc,shell=True,stdout=PIPE)
	outpt,err=tstt.communicate()
	print outpt
	return eval(outpt)

