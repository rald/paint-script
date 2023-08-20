import os
import random 
import PIL
from PIL import Image, ImageDraw
from datetime import datetime

from palette import pal
from Token import Token
from TokenType import TokenType
from my_lib import resize_canvas



class Parser:



  def __init__(self,tokens,image_path):
  
    self.id=id

    self.tokens=tokens
    self.pc=0
    self.glo={}
    self.prm=[]
    self.lab={}
    self.ret=[]
    self.stk=[]    
    self.quit=False

    self.glo["env"]=Token(0,0,TokenType.STRING,"")
    self.glo["debug"]=Token(0,0,TokenType.INTEGER,0)

    self.env=self.glo["env"]

    self.indent=0

    self.image_path=image_path

    if os.path.isfile(self.image_path):
      self.img=Image.open(self.image_path).convert('RGB')
    else:
      self.img=PIL.Image.new(mode="RGB", size=(640,480), color=pal[12])

    self.draw=ImageDraw.Draw(self.img)



  def error(self,msg):
    print(f"\n{self.get_line()}:{self.get_column()}: {msg}")
    quit()



  def next(self):
    if self.get_type()==TokenType.EOF:
      self.error("input past end of file")
    else:
      self.pc+=1
      if self.glo["debug"].value==1: print("pc",self.pc)



  def begin_tag(self,tag):
    if self.glo["debug"].value==1:
      print("  "*self.indent,end="")   
      print(f"</{tag}>")
    self.indent+=1



  def end_tag(self,tag):
    self.indent-=1
    if self.glo["debug"].value==1:
      print("  "*self.indent,end="")   
      print(f"</{tag}>")


  
  def read_labels(self):
    for i in range(len(self.tokens)):
      if self.tokens[i].type==TokenType.LABEL:
        label=self.tokens[i]
        if label.value in self.lab:
          print(f"{self.tokens[i].line}:{self.tokens[i].column}:label redefined: {label.value}")
          quit()
        self.glo["LABEL_"+label.value]=i;



  def get_line(self):
    return self.look().line



  def get_column(self):
    return self.look().column
    


  def look(self):
    return self.tokens[self.pc]



  def peek(self,offset):
    pos=self.pc+offset
    if pos<0 or pos>=len(self.tokens):
      self.print(f"peek: offset out of bounds {pos}")
      quit()
    return self.tokens[self.pc+offset]



  def match(self,type):
    if self.look().type!=type:
      self.error(f"found {self.look().type} expected {type}")      


 
  def check(self,type,value):
    self.begin_tag("check") 
    self.match(TokenType.IDENT)
    if self.get_value()!=value:
      self.error(f"found '{self.get_value()}' expected {value}")  
    self.next()
    self.end_tag("check") 



  def get_type(self):
    return self.look().type



  def get_value(self):
    return self.look().value



  def eat(self,type,count=1):
    for _ in range(count):
      self.match(type)
      self.next()


      
  def get_none(self):
    self.begin_tag("get_none") 
    self.match(TokenType.NONE)
    self.next()
    self.end_tag("get_none") 
    return self.look() 



  def get_integer(self):
    self.begin_tag("get_integer") 
    self.match(TokenType.INTEGER)
    result=self.look()
    self.next()
    self.end_tag("get_integer") 
    return result



  def get_float(self):
    self.begin_tag("get_float") 
    self.match(TokenType.FLOAT)
    result=self.look()
    self.next()
    self.end_tag("get_float") 
    return result



  def get_string(self):
    self.begin_tag("get_string") 
    self.match(TokenType.STRING)
    result=self.look()
    self.next()
    self.end_tag("get_string") 
    return result



  def get_false(self):
    self.begin_tag("get_false") 
    self.match(TokenType.FALSE)
    result=self.look()
    self.next()
    self.end_tag("get_false") 
    return result



  def get_true(self):
    self.begin_tag("get_true") 
    self.match(TokenType.TRUE)
    result=self.look()
    self.next()
    self.end_tag("get_true") 
    return result



  def get_label(self):
    self.begin_tag("get_label") 
    self.match(TokenType.IDENT)
    result=self.look()
    self.end_tag("get_label") 
    return result


  def get_label_check(self):
    self.begin_tag("get_label_check") 
    self.match(TokenType.IDENT)
    label=self.look()
    if "LAB_"+label.value not in self.glo:
      self.error(f"undefined label {label_name}")
    self.next()
    self.end_tag("get_label_check") 
    return label



  def get_ident(self):
    self.begin_tag("get_ident")
    self.match(TokenType.IDENT)
    result=self.look()
    self.next()
    self.end_tag("get_ident") 
    return result



  def get_ident_check(self):
    self.begin_tag("get_ident_check") 
    self.match(TokenType.IDENT)
    ident=self.look()
    if "VAR_"+ident.value not in self.glo:
      self.error(f"get_ident_check: undefined identifier {ident.value}")
    self.next()
    self.end_tag("get_ident_check") 
    return ident



  def get_number(self):
    self.begin_tag("get_number")
    result=None
    if self.get_type()==TokenType.INTEGER or self.get_type()==TokenType.FLOAT:
      result=self.look()
    else:
      self.error(f"found {self.get_type()} expected INT or FLOAT")
    self.end_tag("get_number") 
    return result



  def get_atom(self):
    self.begin_tag("get_atom")
    result=None 
    if self.get_type()==TokenType.NONE or self.get_type()==TokenType.FALSE or self.get_type()==TokenType.TRUE or self.get_type()==TokenType.INTEGER or self.get_type()==TokenType.FLOAT or self.get_type()==TokenType.STRING:
      result=self.look()
    else:
      self.error(f"found {self.get_type()} expected ATOM")
    self.next()
    self.end_tag("get_atom") 
    return result



  @staticmethod
  def concat(token1,token2):
    return Token(0,0,TokenType.STRING,str(token1.value)+str(token2.value))
  
      




  def do_set(self):
    self.begin_tag("do_set") 
    result=""
    self.check(TokenType.IDENT,"set")
    token1=self.get_ident()
    if self.get_type()==TokenType.IDENT:
      token2=self.get_ident_check()
      token2=self.glo["VAR_"+token2.value]
    else:
      token2=self.get_atom()
    result=token2
    while self.get_type() not in [TokenType.NEW_LINE,TokenType.EOF]:
      if self.get_type()==TokenType.IDENT:
        token2=self.get_ident_check()
        token2=self.glo["VAR_"+token2.value]
      else:
        token2=self.get_atom()
      result=Token(0,0,TokenType.STRING,str(result.value)+str(token2.value))
    self.glo["VAR_"+token1.value]=result      
    self.end_tag("do_set") 



  def do_get(self):
    self.begin_tag("do_get") 
    token=None
    self.check(TokenType.IDENT,"get")
    token1=self.get_ident()
    if self.get_type()==TokenType.IDENT:
      token2=self.get_ident_check()
    else:
      token2=self.get_string()
    count=self.get_integer().value
    for _ in range(count):
      if "VAR_"+token2.value in self.glo:
        token2=self.glo["VAR_"+token2.value]
      else:
        self.error(f"invalid identifier {token2.value}")
    self.glo["VAR_"+token1.value]=token2
    self.end_tag("do_get") 



  def do_say(self):
    self.begin_tag("do_say") 
    result=None
    self.check(TokenType.IDENT,"say")
    if self.get_type()==TokenType.IDENT:
      ident=self.get_ident_check()
      result=self.glo["VAR_"+ident.value]
    else:
      result=self.get_atom()
    print(result.value)
    self.end_tag("do_say") 



  def do_end(self):
    self.begin_tag("do_end") 
    result=None
    self.check(TokenType.IDENT,"end")
    self.quit=True
    self.end_tag("do_end") 



  def do_debug(self):
    result=None
    self.check(TokenType.IDENT,"debug")
    self.glo["debug"]=self.get_integer()



  def do_globals(self):
    self.begin_tag("do_globals") 
    self.check(TokenType.IDENT,"globals")
    for key in self.glo:
      token=self.glo[key]
      print(key,"=",f"\"{token.value}\"" if token.type==TokenType.STRING else token.value)
    self.end_tag("do_globals") 







  def eval(self):
    self.begin_tag("eval") 
              
    if self.get_type()==TokenType.IDENT:
    
      if self.get_value()=="set":
        self.do_set()
      elif self.get_value()=="get":
        self.do_get()
      elif self.get_value()=="say":
        self.do_say()
      elif self.get_value()=="end":
        self.do_end()
      elif self.get_value()=="debug":
        self.do_debug()
      elif self.get_value()=="globals":
        self.do_globals()
      else:
        self.error(f"invalid command {self.get_value()}")
    self.end_tag("eval") 



  def parse(self):

    self.read_labels()

    

    while not self.quit and not self.get_type()==TokenType.EOF:

      while self.get_type() in [TokenType.NEW_LINE,TokenType.LABEL,TokenType.COMMENT]:
        self.next()

      self.eval()
