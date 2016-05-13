"""
    meetup.py
    ~~~~~~~~~
    Collects streaming meetup.com RSVP data.  Writes frequency count of topics 
    that meetup members are RSVPing to by city/state/country.
    Usage::
    	writes to freq_counts.json in directory where script is run
"""
import requests
import json
from collections import Counter
print '''streaming data...'''
r = requests.get('http://stream.meetup.com/2/rsvps', stream=True)

counter_dict = {}
write_frequency = 100
line_counter = 0
for line in r.iter_lines():
	if line:
		item = json.loads(line) 
		city = item['group']['group_city'] +'||' + str(item['group'].get('group_state','NA')) +'||' + str(item['group']['group_country']).upper()
		lat = item['group']['group_lat']
		lon = item['group']['group_lon']
		topics = [topic['topic_name'] for topic in item['group']['group_topics']] 
		if city in counter_dict.keys():
			counter_dict[city]['count'] += 1
			counter_dict[city]['topics'] += Counter(topics)
		else:
			counter_dict[city] = {"count":1,"lat":lat, "lon":lon, "topics":Counter(topics)}
		line_counter += 1
		if line_counter % write_frequency == 0:
			#print counter_dict
			with open("freq_counts.json", "wb") as f:
				write_dict = {}
				for k in counter_dict:
					write_dict[k] = {}
					write_dict[k]['count'] = counter_dict[k]['count']
					write_dict[k]['lat'] = counter_dict[k]['lat']
					write_dict[k]['lon'] = counter_dict[k]['lon']
					write_dict[k]['topics'] = counter_dict[k]['topics'].most_common()
				f.write(json.dumps(write_dict, sort_keys=True, indent=4, ensure_ascii=False).encode('utf8'))
				print str(line_counter) + 'rows written'
