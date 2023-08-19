#!/usr/bin/env python3

import os

script_code=os.getenv("QUERY_STRING")
if not script_code: 
    print("10 Input script code:",end="\r\n")
    quit()

print("30 write.cgi?"+script_code,end='\r\n')
