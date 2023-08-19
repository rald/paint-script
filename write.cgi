#!/usr/bin/env python3
import re
import sys

from my_lib import is_valid_id



print("20 text/gemini",end="\r\n")

script_code=os.getenv("QUERY_STRING")
if not script_code:
  print("Invalid script code")
  quit()

script_code=unquote(script_code)
if not script_code:
  print("Invalid script code")
  quit()

id_path=os.path.join(os.path.abspath(os.getcwd()),'/id.txt')

try:
  f=open(id_path,"r")
  id=int(f.readline())
  f.close()
except:
  print("error reading script id")
  quit()

script_id=hex(id)
if not is_valid_id(script_id):
  print("Invalid script id:",script_id)
  quit()

script_path=os.path.join(os.path.abspath(os.getcwd()),'/scripts/'+script_id)

try:
  f=open(script_path,"w")
  f.write(script_code)
  f.close()
except:
  print("error writing script")
  quit()

print("# Your script id is: ",script_id)

try:
  f=open(id_path,"w")
  f.write(id+1)
  f.close()
except:
  print("error updating script id")
  quit()
