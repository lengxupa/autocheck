src=open('checkpan.txt')
des=open('checkpansuc.txt','w')
a=0
for line in src.readlines():
	ln=line.split()
	if ln[-1]=='success':
		a=1
	if ln[-1]=='failed':
		a=0
	if a:
		des.write(line)
