import requests
import re
import sys
import os.path

def input_determiner(cmdarg):
	if cmdarg[0] == '-':
		#Create and print list of URLs from file
		if cmdarg[1] == 'u':
			return 1
		#Create report when given list of URLs
		elif cmdarg[1] == 'l':
			return 2
		#Print raw HTML
		elif cmdarg[1] == 'n':
			return 3
		#Print sanitized version of HTML
		elif cmdarg[1] == 's':
			return 4
		#Fix HTML
		elif cmdarg[1] == 'f':
			return 5
		else:
			return 0
	else:
		return -1

def generate_urllist(filename):
	list = {"empty":1}

	if os.path.exists(filename):
		with open(filename) as file:
			list["entries"] = file.read().split("\n")[:-1]
	else:
		print "File does not exist."
		sys.exit()

	return list

def extract_bio(url, name, expression, x, y):
	html = requests.get(url + name)

	if x == 0 and y ==0:
		y = len(html.text)

        if expression != "1":
            regex = re.compile(expression, re.DOTALL)
            try:
                return regex.findall(html.text)[0][int(x):int(y)]
            except:
                return regex.findall(html.text)[int(x):int(y)]
        else:
            return html.text


def check_unbalanced_tags(text):
	openingtags = re.findall("&lt;(?!/)(?!br)[^&gt;]*&gt;", text) + re.findall("<(?!/)(?!br)[^>]*>", text)

	closingtags = re.findall("&lt;(?=/)[^&gt;]*&gt;", text) + re.findall("<(?=/)[^>]*>", text)

	tags = {'found': 0}

	if len(openingtags) != len(closingtags):
		tags['found'] = 1
		tags['opening'] = len(openingtags)
		tags['closing'] = len(closingtags)
	return tags

def check_office_tags(text):
	apos = ["&lt;o:p&gt;","&lt;/o:p&gt;"]


	tags = {'found': 0, 'storage': []}

	for x in apos:
		tags['storage'].extend(re.findall(x, text))

	if len(tags['storage']) > 0:
		tags['found'] = 1
	return tags

def write_data_urllist(url, filename, expression, x, y):
	urllist = generate_urllist(filename)['entries']

	statusfile = open("status_log.txt","a")

	for name in urllist:
		status = ""
		try:
			bio = str(extract_bio(url, name, expression, x, y))
		except:
			bio = str(extract_bio(url, name, expression, x, y).encode("utf-8"))
		if check_unbalanced_tags(bio)['found'] and check_office_tags(bio)['found']:
			print "1 worked " + name
			status = name + ":a1: open tags = " + str(check_unbalanced_tags(bio)['opening']) + " | closing tags = " + str(check_unbalanced_tags(bio)['closing']) + "\n"
		elif check_unbalanced_tags(bio)['found']:
			print "2 worked " + name
			status = name + ":a2: open tags = " + str(check_unbalanced_tags(bio)['opening']) + " | closing tags = " + str(check_unbalanced_tags(bio)['closing']) + "\n"
		elif check_office_tags(bio)['found']:
			print "3 worked " + name
			status = name + ":a3: needs office tag sanitation" + "\n"
		else:
			print "4 didn't work or nothing wrong " + name

		if len(status) > 0:
			statusfile.write(status)

def tag_sanitizer(url, input, expr, x, y):

	bio = extract_bio(url, input, expr, x, y)

	text = bio.replace("&lt;","<").replace("&gt;", ">").strip("<o:p>")

	return text

def tag_matcher(name):
	bio = tag_sanitizer(extract_bio(name))

	opening = "<(?!/)(?!br)[^>]*>"
	openingtags = {}

	openamt = len(re.findall(opening, bio))

	print openamt

url = sys.argv[1]

cmdarg = sys.argv[2]

input = sys.argv[3]

if len(sys.argv) > 6:
    express = sys.argv[4]
    x = sys.argv[5]
    y = sys.argv[6]
elif len(sys.argv) > 4:
    express = sys.argv[4]
    x = 0
    y = 0
else:
    express = "1"
    x = 0
    y = 0

if input_determiner(cmdarg) == 1:
	print generate_urllist(input)
elif input_determiner(cmdarg) == 2:
	write_data_urllist(url, input, express, x, y)
elif input_determiner(cmdarg) == 3:
	print extract_bio(url, input, express, x, y)
elif input_determiner(cmdarg) == 4:
	print tag_sanitizer(url, input, express, x, y)
elif input_determiner(cmdarg) == 0:
	print "Incorrect option"
else:
        print "Not enough arguments"
