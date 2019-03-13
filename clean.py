import os

cwd = os.getcwd()
for root, dirs, files in os.walk(cwd, topdown=False):
	if 'mdz.dump' in files:
		rt=root.split('/')
		if 'PAN' in rt:
			continue
		if 'step4.data' in files:
			os.chdir(root)
			print root,'mdz.dump deleting'
			os.system('rm mdz.dump')
			continue
		for i in files:
			if '.o' in i:
				os.chdir(root)
				print root,'mdz.dump deleting'
				os.system('rm mdz.dump')
				break
	if 'md.dump' in files:
		if 'step4.data' in files:
			os.chdir(root)
			print root,'md.dump deleting'
			os.system('rm md.dump')
			continue
		for i in files:
			if '.o' in i:
				os.chdir(root)
				print root,'md.dump deleting'
				os.system('rm md.dump')
				break
