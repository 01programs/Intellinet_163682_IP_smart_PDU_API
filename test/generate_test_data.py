#!/usr/bin/env python
# -*- coding: utf-8 -*- 
from api import IPU

from config import HOST

api = IPU(HOST)

print(api.endpoints)

for name, page in api.endpoints.items():
	e = api._get_request(page)
	print("GETTING: " + name)
	print("SAVING TO: /test/test_data/"+page)
	with open("test/test_data/"+page, "w") as f: 
	 	f.write(e.content) 
