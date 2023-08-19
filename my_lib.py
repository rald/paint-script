#!/usr/bin/env python3

import re

def is_valid_id(str):

  regex = "^[a-f0-9]{4}$"
  p = re.compile(regex)

  str=str.lower()

  if(str == None):
      return False

  if(re.search(p, str)):
      return True
  else:
      return False



