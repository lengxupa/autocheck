import os

cwd = os.getcwd()
des=open('results.txt','w')
for root, dirs, files in os.walk(cwd, topdown=False):
	for i in files:
		if i[:5]=='check' and i[-3:]!='.py':
			src=open(i)
			lala=src.readlines()
			des.write('%s:\n%s%s\n' %(i,lala[-2],lala[-1]))
			src.close()
des.close()

