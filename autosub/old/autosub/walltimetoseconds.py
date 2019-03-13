def walltimetoseconds(i):
	content=i.split(':')
	if eval(content[0])<=24:
		pt =datetime.datetime.strptime(i,'%H:%M:%S')
		total_seconds = pt.second+pt.minute*60+pt.hour*3600
	else:
		total_seconds=eval(content[2])+eval(content[1])*60+eval(content[0])*3600
	return total_seconds

