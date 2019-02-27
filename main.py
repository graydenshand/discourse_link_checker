import psycopg2
import psycopg2.extras
import re
import requests
from decimal import Decimal
import json
from datetime import datetime
import csv
import sys

try:
	sessionid = sys.argv[1]
except IndexError:
	sessionid = input("Please enter the ID of this workshop session (e.g. TMS6)\n")

output_path = 'finished_searches/' + sessionid + '_' + str(datetime.now().date()) + '.csv'

f = open("known_links.json",'r')
known_links = json.loads(f.read())

link_structure = re.compile('''(href=['"])(http(s)://[ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789\-.\_~:/?#\[\]@!$&'()*+,;=]+)(")'''.encode('utf-8'))
#Function to get all found links
def linkSearch(string):
	links_found = link_structure.findall(string)
	if len(links_found) == 0:
		return(False)
	else:
		links = []
		for link in links_found:
			links.append(link[1])
		return(links)


#Open the database connection
conn = psycopg2.connect("dbname=postgres user=postgres")
cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

#Write SQL query to string
sql = '''SELECT p.id, p.user_id, p.post_number, t.title topic, c.name category, p.cooked html
FROM public.posts p, public.topics t, public.categories c, public.users u
WHERE t.id = p.topic_id 
AND c.id = t.category_id
AND p.user_id = u.id
AND u.admin = TRUE
AND p.deleted_at IS null;
'''


#Execute SQL query
cur.execute(sql)


#Iterate through posts to find links
link_list_master = []
i=1

for row in cur:
	utf_post = row['html'].encode('utf-8')
	if linkSearch(utf_post) != False:
		for link in linkSearch(utf_post):
			data = {'post':utf_post, 'post_id': row['id'], 'user_id': row['user_id'], 'post_number': row['post_number'], 'topic': row['topic'].encode("utf-8"), 'category': row['category'].encode("utf-8"), 'link': link}
			link_list_master.append(data)
	i+=1
conn.close()

num_links = len(link_list_master)

print(str(num_links) + " links found")

print("Clicking links")

broken_links = []
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:20.0) Gecko/20100101 Firefox/20.0'}
for i, row in enumerate(link_list_master):
	for k,v in row.items():
		if type(v) is bytes:
			row[k] = v.decode("utf-8")	
	link = row['link']		
	try: 
		r = requests.get(link, headers=headers)
		r.raise_for_status()
	except requests.exceptions.RequestException as e:
		if link not in known_links:
			row['error'] = str(e)
			row['fixed'] = 'n'
			row['comment'] = None
			broken_links.append(row)
			print(link, e)

	if i % 20 == 0:
		print(str(i) + " links clicked")

print(str(len(broken_links)) + " suspicious links found")

print("Writing output to " + output_path)
f = open(output_path, 'w')
f.write('')
f.close()
if len(broken_links) > 0:
	print("Building CSV")
	if len(broken_links) > 0:
		csv_headers = broken_links[0].keys()
	else:
		csv_headers = ['There were no suspicious links found.']
	f = open(output_path,'w', encoding="utf-8")
	writer = csv.DictWriter(f, fieldnames=csv_headers)
	writer.writeheader()
	writer.writerows(broken_links)
	f.close()

print("DONE")



#Unit Testing linkSearch function
#links = linkSearch('some other text over here <a href="https://somelink.com" plus some more over here <a href="http://anotherlink.link"'.encode('utf-8'))
#print(linkSearch('some other text over here <a href="http/somelink.com" plus some more over here <a href="ht//anotherlink.link"'.encode('utf-8')))
#print(linkSearch('this is testing a realy long link <a href="http://somereallylonglink.com/other_characters?like=this&this=that_or-this"'.encode('utf-8')))
#for link in links:
	#print(link.decode('utf-8'))
#print(linkSearch('''href="https://www.udemy.com/modern-marketing-with-seth-godin/?couponCode=LEAPFIRST" lkj'''.encode("utf-8")))

