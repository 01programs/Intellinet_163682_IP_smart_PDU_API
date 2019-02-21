#!/usr/bin/env python
# -*- coding: utf-8 -*- 
from api import IPU



api = IPU("YOUR_IP_HERE")

print(api.endpoints)

for name, page in api.endpoints.items():
	e = api._get_request(page)
	print("GETTING: " + name)
	print("SAVING TO: /test/test_data/"+page)
	with open("test/test_data/"+page, "w") as f: 
	 	f.write(e.content) 
