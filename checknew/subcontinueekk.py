def subcontinue(po,fi,ta,co,te,rt,jud):
	ns=['5ns','10ns','20ns','50ns','100ns','200ns','500ns']
	if rt in ns:
		if rt==ns[-1]:
			return 0
		new=ns[ns.index(rt)+1]
		sta=eval(ns[ns.index(rt)-1][:-2])*1000000
		ter=eval(rt[:-2])*1000000
		ste=(ter-sta)/100
	else:
		new=ns[1]
		sta=0
		ter=5000000
		ste=50000
	dumprange=range(((sta/ste+(1 if sta%ste else 0))*ste),ter,ste)
	if jud:
		for j in dumprange:
			if os.path.exists('md.%d.dump' %j) and (not checkfile('md.%d.dump' %j)):
				continue
			break
		t=j-ste
		if t<dumprange[0]:
			new=rt
			sta=eval(ns[ns.index(rt)-2][:-2])*1000000 if rt!='10ns' else 0
			ter=eval(ns[ns.index(rt)-1][:-2])*1000000 if rt!='10ns' else 5000000
			ste=(ter-sta)/100 if rt!='10ns' else 50000
			dumprange=range(((sta/ste+(1 if sta%ste else 0))*ste),ter,ste)
	if not os.path.exists(new):
		os.mkdir(new)
		os.system('cp melt.in %s' %new)
		if jud:
			for j in dumprange[::-1]:
				if os.path.exists('md.%d.dump' %j) and (not checkfile('md.%d.dump' %j)):
					break
			t=j
			dump2data('polymer_relax.data',('md.%d.dump' %t),('%s/polymer_relax.data' %new))
		else:
			t=ter
			Dir=read_data('step4.data')
			write_data(Dir,('%s/polymer_relax.data' %new))
		os.system('cp log.lammps %s' %new)
		os.chdir(new)
		ter2=eval(new[:-2])*1000000
		ste2=(ter2-ter)/100
		meltcontinue('melt.in',('melt%s.in' %new),t,ste2)
		if jud:
			walltime=float(getsubwalltime('../sub.sh'))/(t-sta)*(ter2-t)
		else:
			walltime=float(getwalltime('log.lammps'))/(t-sta)*(ter2-t)
		os.system('cp melt%s.in melt.in' %new)
		write_sublmp(walltime,po,fi,ta,co,te,new,'melt.in')
		os.system('qsub sub.sh')

