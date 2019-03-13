def meltingFQ(i,j,a,b):
	tmprange=range(500,820,20)
	for o in tmprange:
		tit='FQ'+str(o)
		if not os.path.exists(tit):
			os.mkdir(tit)
			os.system('cp coollong.in %s' %tit)
			os.system('cp step4.data %s/polymer_relax.data' %tit)
			os.system('cp log.lammps %s' %tit)
			if os.path.exists('param.qeq.pan'):
				os.system('cp param.qeq.pan %s' %tit)
			os.chdir(tit)
			coollongtoFQ('coollong.in','melt.in',o)
			walltime=getwalltime('log.lammps')
			write_sublmp(walltime,i,j,a,b,('FQ'+str(o))[:4],'melt.in')
			os.system('qsub sub.sh')
			os.chdir('..')