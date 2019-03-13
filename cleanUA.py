import os

fixlist=['xfix'+str(i) for i in range(1,16)]
fixlist+=['fix','xfix','yfix','yfix1','xyfix']
realist=['fix','xfix8','yfix1']
for i in ['PE43','PP']:
	for j in fixlist:
		if not os.path.exists('%s/%s' %(i,j)):
			continue
		os.chdir('%s/%s' %(i,j))
		cwd = os.getcwd()
		for root, dirs, files in os.walk(cwd, topdown=False):
			rt=root.split('/')
			if 'Detailed.dump' in files:
				os.chdir(root)
				print root,'Detailed deleting'
				os.system('rm Detailed.dump')
				os.chdir(cwd)
			if 'md.dump' in files:
				os.chdir(root)
				print root,'md.dump deleting'
				os.system('rm md.dump')
				os.chdir(cwd)
		os.chdir('../..')
