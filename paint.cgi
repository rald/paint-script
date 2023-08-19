#!/usr/bin/env python3
import os
import re
import sys
from urllib.parse import unquote

from Lexer import Lexer
from Parser import Parser
from my_lib import is_valid_id



if len(sys.argv)>=2:
  script_path=sys.argv[1]
  image_path=sys.argv[1]+".jpg"
else:
  print("20 text/gemini",end="\r\n")

  script_id=os.getenv("QUERY_STRING")
  if not script_id:
    print("Invalid script id")
    quit()

  script_id=unquote(script_id)
  if not is_valid_id(script_id):
    print("Invalid script id:",script_id)
    quit()
   
  script_path=os.path.join(os.getcwd(),'scripts/'+script_id)

  image_path=os.path.join(os.getcwd(),'images/'+script_id+".jpg")

  print(f"=> /images/{script_id}.jpg View Painting")



code=""
try:
  f=open(script_path,"r")
  code=f.read()
  f.close()
except:
  print("Error reading script:",script_path)


tokens=Lexer.lex(code)
parser=Parser(tokens,image_path)
parser.parse()

