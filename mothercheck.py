import os

print 'AA'
os.system('python checknew.py')
os.system('python checknew.py > checknew.txt')
os.chdir('../20170610')
print 'UA'
os.system('python button.py')
os.system('python button.py > button.txt')
os.chdir('../20170717')
print 'LJ'
os.system('python button_LJ.py')
os.system('python button_LJ.py > button_LJ.txt')
os.chdir('../20170719')
print 'lj'
os.system('python button_LJrevised.py')
os.system('python button_LJrevised.py > button_LJrevised.txt')
