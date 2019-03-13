def finaltransfer():
	os.system("cat Species.dat* > %s" %speciesfile)
	os.system("cat x.bond* > %s" %bondfile)
	writesublog('lg%s' %jbN)
	subjob('Sublog.sh')
	if(bondfile):
		writesubbond(('bd%s' %jbN),datafile)
		subjob('Subbond.sh')

