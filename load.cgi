#!/usr/bin/env python3

import os

script_id=os.getenv("QUERY_STRING")
if not script_id: 
    print("10 Input script id:",end="\r\n")
    quit()

print("30 paint.cgi?"+script_id,end='\r\n')
