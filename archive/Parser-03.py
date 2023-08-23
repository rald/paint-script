import os
import random 
import PIL
import math
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
    self.quit=False

    self.glo["debug"]=Token(0,0,TokenType.INTEGER,0)
    self.glo["RET"]=[]
    self.glo["STK"]=[]
    self.glo["FUN"]="FUN"

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


  
  def load_labels(self):
    for i in range(len(self.tokens)):
      if self.tokens[i].type==TokenType.LABEL:
        label=self.tokens[i]
        if "LAB_"+label.value in self.glo:
          print(f"{self.tokens[i].line}:{self.tokens[i].column}:label redefined: {label.value}")
          quit()
        self.glo["LAB_"+label.value]=Token(0,0,TokenType.INTEGER,i);



  def get_line(self):
    return self.look().line



  def get_column(self):
    return self.look().column
    


  def look(self):
    return self.tokens[self.pc]



  def peek(self,offset):
    pos=self.pc+offset
    if pos<0 or pos>=len(self.tokens):
      self.print(f"offset out of bounds {pos}")
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



  def get_token(self):
    return self.look()



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
    result=self.get_token()
    self.next()
    self.end_tag("get_none") 
    return result 



  def get_integer(self):
    self.begin_tag("get_integer") 
    self.match(TokenType.INTEGER)
    result=self.get_token()
    self.next()
    self.end_tag("get_integer") 
    return result



  def get_float(self):
    self.begin_tag("get_float") 
    self.match(TokenType.FLOAT)
    result=self.get_token()
    self.next()
    self.end_tag("get_float") 
    return result



  def get_string(self):
    self.begin_tag("get_string") 
    self.match(TokenType.STRING)
    result=self.get_token()
    self.next()
    self.end_tag("get_string") 
    return result



  def get_false(self):
    self.begin_tag("get_false") 
    self.match(TokenType.FALSE)
    result=self.get_token()
    self.next()
    self.end_tag("get_false") 
    return result



  def get_true(self):
    self.begin_tag("get_true") 
    self.match(TokenType.TRUE)
    result=self.get_token()
    self.next()
    self.end_tag("get_true") 
    return result



  def get_label(self):
    self.begin_tag("get_label") 
    self.match(TokenType.IDENT)
    result=self.get_token()
    self.next()
    self.end_tag("get_label") 
    return result



  def get_label_check(self):
    self.begin_tag("get_label_check") 
    self.match(TokenType.IDENT)
    label=self.get_token()
    if "LAB_"+label.value not in self.glo:
      self.error(f"undefined label {label.value}")
    self.next()
    self.end_tag("get_label_check") 
    return label



  def get_ident(self):
    self.begin_tag("get_ident")
    self.match(TokenType.IDENT)
    result=self.get_token()
    self.next()
    self.end_tag("get_ident") 
    return result



  def get_ident_check(self):
    self.begin_tag("get_ident_check") 
    self.match(TokenType.IDENT)
    ident=self.get_token()
    if "VAR_"+ident.value not in self.glo:
      self.error(f"get_ident_check: undefined identifier {ident.value}")
    self.next()
    self.end_tag("get_ident_check") 
    return ident



  def get_number(self):
    self.begin_tag("get_number")
    result=Token(0,0,TokenType.NONE,None)
    if self.get_type() in [TokenType.INTEGER,TokenType.FLOAT]:
      result=self.get_token()
      self.next()
    elif self.get_type()==TokenType.IDENT:
      ident=self.get_ident_check()
      result=self.glo["VAR_"+ident.value]
      if result.type not in [TokenType.INTEGER,TokenType.FLOAT]:
        self.error(f"found {result.type} expected INT or FLOAT")
    else:
      self.error(f"found {self.get_type()} expected INT or FLOAT")
    self.end_tag("get_number") 
    return result



  def get_number_or_none(self):
    self.begin_tag("get_number_or_none")
    result=Token(0,0,TokenType.NONE,None)
    if self.get_type() in [TokenType.INTEGER,TokenType.FLOAT,TokenType.NONE]:
      result=self.get_token()
      self.next()
    elif self.get_type()==TokenType.IDENT:
      ident=self.get_ident_check()
      result=self.glo["VAR_"+ident.value]
      if result.type not in [TokenType.INTEGER,TokenType.FLOAT,TokenType.NONE]:
        self.error(f"found {result.type} expected INT or FLOAT")
    else:
      self.error(f"found {self.get_type()} expected INT or FLOAT")
    self.end_tag("get_number") 
    return result



  def get_atom(self):
    self.begin_tag("get_atom")
    result=Token(0,0,TokenType.NONE,None)
    if self.get_type() in [TokenType.NONE,TokenType.FALSE,TokenType.TRUE,TokenType.INTEGER,TokenType.FLOAT,TokenType.STRING]:
      result=self.get_token()
    else:
      self.error(f"found {self.get_type()} expected ATOM")
    self.next()
    self.end_tag("get_atom") 
    return result
  
      

  def get_any(self):
    self.begin_tag("get_any")
    result=Token(0,0,TokenType.NONE,None)
    if self.get_type()==TokenType.IDENT:
      ident=self.get_ident_check()
      result=self.glo["VAR_"+ident.value]
    elif self.get_type() in [TokenType.NONE,TokenType.FALSE,TokenType.TRUE,TokenType.INTEGER,TokenType.FLOAT,TokenType.STRING]:
      result=self.get_token()
      self.next()
    else:
      self.error(f"found {self.get_type()} expected VALUE")
    self.end_tag("get_any") 
    return result



  def get_ident_integer(self):
    self.begin_tag("get_ident_integer")
    result=Token(0,0,TokenType.NONE,None)
    if self.get_type()==TokenType.IDENT:
      ident=self.get_ident_check()
      result=self.glo["VAR_"+ident.value]
      if result.type!=TokenType.INTEGER:
        self.error(f"found {result.type} expected INTEGER")
    elif self.get_type()==TokenType.INTEGER: 
      result=self.get_integer()
    else:
      self.error(f"found {self.get_type()} expected INTEGER")
    self.end_tag("get_ident_integer") 
    return result


  def do_set(self):
    self.begin_tag("do_set") 
    self.check(TokenType.IDENT,"set")
    result=Token(0,0,TokenType.NONE,None)
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
    self.check(TokenType.IDENT,"say")
    result=Token(0,0,TokenType.NONE,None)
    if self.get_type()==TokenType.IDENT:
      ident=self.get_ident_check()
      result=self.glo["VAR_"+ident.value]
    else:
      result=self.get_atom()
    print(result.value)
    self.end_tag("do_say") 



  def do_add(self):
    self.begin_tag("do_add")
    self.check(TokenType.IDENT,"add")   
    result=Token(0,0,TokenType.NONE,None)
    ident=self.get_ident()
    if "VAR_"+ident.value not in self.glo:
      self.glo["VAR_"+ident.value]=Token(0,0,TokenType.INTEGER,0)
    token1=self.glo["VAR_"+ident.value]
    token2=self.get_number()
    if token1.type==TokenType.FLOAT or token2.type==TokenType.FLOAT:
      result=Token(0,0,TokenType.FLOAT,float(token1.value)+float(token2.value))
    elif token1.type==TokenType.INTEGER and token2.type==TokenType.INTEGER:
      result=Token(0,0,TokenType.INTEGER,int(token1.value)+int(token2.value))
    else:
      self.error(f"cannot add {token1.type} to {token2.type}")
    self.glo["VAR_"+ident.value]=result
    self.end_tag("do_add") 



  def do_sub(self):
    self.begin_tag("do_sub")
    self.check(TokenType.IDENT,"sub")
    result=Token(0,0,TokenType.NONE,None) 
    ident=self.get_ident()
    if "VAR_"+ident.value not in self.glo:
      self.glo["VAR_"+ident.value]=Token(0,0,TokenType.INTEGER,0)
    token1=self.glo["VAR_"+ident.value]
    token2=self.get_number()
    if token1.type==TokenType.FLOAT or token2.type==TokenType.FLOAT:
      result=Token(0,0,TokenType.FLOAT,token1.value-token2.value)
    elif token1.type==TokenType.INTEGER and token2.type==TokenType.INTEGER:
      result=Token(0,0,TokenType.INTEGER,token1.value-token2.value)
    else:
      self.error(f"cannot sub {token1.type} to {token2.type}")
    self.glo["VAR_"+ident.value]=result
    self.end_tag("do_sub") 



  def do_mul(self):
    self.begin_tag("do_mul")
    self.check(TokenType.IDENT,"mul")
    result=Token(0,0,TokenType.NONE,None) 
    ident=self.get_ident_check()
    token1=self.glo["VAR_"+ident.value]
    token2=self.get_number()
    if token1.type==TokenType.FLOAT or token2.type==TokenType.FLOAT:
      result=Token(0,0,TokenType.FLOAT,token1.value*token2.value)
    elif token1.type==TokenType.INTEGER and token2.type==TokenType.INTEGER:
      result=Token(0,0,TokenType.INTEGER,token1.value*token2.value)
    else:
      self.error(f"cannot mul {token1.type} to {token2.type}")
    self.glo["VAR_"+ident.value]=result
    self.end_tag("do_mul") 



  def do_div(self):
    self.begin_tag("do_div")
    self.check(TokenType.IDENT,"div")
    result=Token(0,0,TokenType.NONE,None) 
    ident=self.get_ident_check()
    token1=self.glo["VAR_"+ident.value]
    token2=self.get_number()
    if token2.value==0:
      self.error("division by zero")      
    elif token1.type in [TokenType.INTEGER,TokenType.FLOAT] and token2.type in [TokenType.INTEGER,TokenType.FLOAT]:
      result=Token(0,0,TokenType.FLOAT,float(token1.value)/float(token2.value))
    else:
      self.error(f"cannot mod {token1.type} to {token2.type}")
    self.glo["VAR_"+ident.value]=result
    self.end_tag("do_div") 




  def do_mod(self):
    self.begin_tag("do_mod")
    self.check(TokenType.IDENT,"mod")
    result=Token(0,0,TokenType.NONE,None) 
    ident=self.get_ident_check()
    token1=self.glo["VAR_"+ident.value]
    token2=self.get_integer()
    if token2.value==0:
      self.error("division by zero")
    elif token1.type in [TokenType.INTEGER,TokenType.FLOAT] and token2.type in [TokenType.INTEGER,TokenType.FLOAT]:
      result=Token(0,0,TokenType.INTEGER,int(token1.value)%int(token2.value))
    else:
      self.error(f"cannot mod {token1.type} to {token2.type}")
    self.glo["VAR_"+ident.value]=result
    self.end_tag("do_mod") 



  def do_call(self):
    self.begin_tag("do_call")
    self.check(TokenType.IDENT,"call")
    label=self.get_label_check()
    self.glo["RET"].append(self.pc)
    self.pc=self.glo["LAB_"+label.value].value
    self.end_tag("do_call") 



  def do_ret(self):
    self.begin_tag("do_ret")
    self.check(TokenType.IDENT,"ret")
    self.pc=self.glo["RET"].pop()
    self.end_tag("do_ret") 



  def do_jmp(self):
    self.begin_tag("do_jmp")
    self.check(TokenType.IDENT,"jmp")
    token1=self.get_label_check()
    self.pc=self.glo["LAB_"+token1.value].value
    self.end_tag("do_jmp") 



  def do_je(self):
    self.begin_tag("do_je")
    self.check(TokenType.IDENT,"je")
    token1=self.get_label_check()
    token2=self.get_number()
    token3=self.get_number()
    if token2.value==token3.value:
      self.pc=self.glo["LAB_"+token1.value].value
    self.end_tag("do_je") 



  def do_jne(self):
    self.begin_tag("do_jne")
    self.check(TokenType.IDENT,"jne")
    token1=self.get_label_check()
    token2=self.get_number()
    token3=self.get_number()
    if token2.value!=token3.value:
      self.pc=self.glo["LAB_"+token1.value].value
    self.end_tag("do_je") 



  def do_jl(self):
    self.begin_tag("do_jl")
    self.check(TokenType.IDENT,"jl")
    token1=self.get_label_check()
    token2=self.get_number()
    token3=self.get_number()
    if token2.value<token3.value:
      self.pc=self.glo["LAB_"+token1.value].value
    self.end_tag("do_je") 



  def do_jle(self):
    self.begin_tag("do_jle")
    self.check(TokenType.IDENT,"jle")
    token1=self.get_label_check()
    token2=self.get_number()
    token3=self.get_number()
    if token2.value<=token3.value:
      self.pc=self.glo["LAB_"+token1.value].value
    self.end_tag("do_jle") 



  def do_jg(self):
    self.begin_tag("do_jg")
    self.check(TokenType.IDENT,"jg")
    token1=self.get_label_check()
    token2=self.get_number()
    token3=self.get_number()
    if token2.value>token3.value:
      self.pc=self.glo["LAB_"+token1.value].value
    self.end_tag("do_jg") 



  def do_jge(self):
    self.begin_tag("do_jge")
    self.check(TokenType.IDENT,"jge")
    token1=self.get_label_check()
    token2=self.get_number()
    token3=self.get_number()
    if token2.value>=token3.value:
      self.pc=self.glo["LAB_"+token1.value].value
    self.end_tag("do_jge") 



  def do_push(self):
    self.begin_tag("do_push")
    self.check(TokenType.IDENT,"push") 
    while self.get_type() not in [TokenType.NEW_LINE,TokenType.EOF]:
      token=self.get_any()
      self.glo["STK"].append(token)
    self.end_tag("do_push") 



  def do_pop(self):
    self.begin_tag("do_pop")
    self.check(TokenType.IDENT,"pop") 
    while self.get_type() not in [TokenType.NEW_LINE,TokenType.EOF]:
      ident=self.get_ident_check()
      self.glo["VAR_"+ident.value]=self.glo["STK"].pop()
    self.end_tag("do_pop") 



  def do_int(self):
    self.begin_tag("do_int")
    self.check(TokenType.IDENT,"int")
    token1=self.get_ident_check()
    token2=self.get_number()
    self.glo["VAR_"+token1.value]=Token(0,0,TokenType.INTEGER,int(token2.value))
    self.end_tag("do_int") 



  def do_flt(self):
    self.begin_tag("do_flt")
    self.check(TokenType.IDENT,"flt")
    token1=self.get_ident_check()
    token2=self.get_number()
    self.glo["VAR_"+token1.value]=Token(0,0,TokenType.FLOAT,float(token2.value))
    self.end_tag("do_flt") 



  def do_str(self):
    self.begin_tag("do_str")
    self.check(TokenType.IDENT,"str")
    token1=self.get_ident_check()
    token2=self.get_number()
    self.glo["VAR_"+token1.value]=Token(0,0,TokenType.STRING,str(token2.value))
    self.end_tag("do_str") 



  def do_rnd(self):
    self.begin_tag("do_rnd")
    self.check(TokenType.IDENT,"rnd")
    token1=self.get_ident_check()
    token2=self.get_number()
    token3=self.get_number()
    self.glo["VAR_"+token1.value]=Token(0,0,TokenType.INTEGER,random.randint(token2.value,token3.value))
    self.end_tag("do_rnd") 



  def do_sin(self):
    self.begin_tag("do_sin")
    self.check(TokenType.IDENT,"sin")
    token1=self.get_ident_check()
    token2=self.get_number()
    self.glo["VAR_"+token1.value]=Token(0,0,TokenType.FLOAT,math.sin(token2.value))
    self.end_tag("do_sin") 



  def do_cos(self):
    self.begin_tag("do_cos")
    self.check(TokenType.IDENT,"cos")
    token1=self.get_ident_check()
    token2=self.get_number()
    self.glo["VAR_"+token1.value]=Token(0,0,TokenType.FLOAT,math.cos(token2.value))
    self.end_tag("do_cos") 



  def do_tan(self):
    self.begin_tag("do_tan")
    self.check(TokenType.IDENT,"tan")
    token1=self.get_ident_check()
    token2=self.get_number()
    self.glo["VAR_"+token1.value]=Token(0,0,TokenType.FLOAT,math.tan(token2.value))
    self.end_tag("do_tan") 



  def do_pset(self):
    self.begin_tag("do_pset")
    self.check(TokenType.IDENT,"pset")
    x=self.get_number().value
    y=self.get_number().value
    s=self.get_number().value
    f=self.get_number().value
    print(f"pset {x} {y} {s} {f}")
    self.draw.rectangle((x*s,y*s,x*s+s,y*s+s),fill=pal[f])
    self.end_tag("do_pset") 



  def do_line(self):
    self.begin_tag("do_line")
    self.check(TokenType.IDENT,"line")
    x0=self.get_number().value
    y0=self.get_number().value
    x1=self.get_number().value
    y1=self.get_number().value
    f=self.get_number_or_none().value
    w=self.get_number().value
    print(f"line {x0} {y0} {x1} {y1} {f} {w}")
    self.draw.line((x0,y0,x1,y1),fill=None if f is None else pal[f],width=w)
    self.end_tag("do_line") 



  def do_oval(self):
    self.begin_tag("do_oval")
    self.check(TokenType.IDENT,"oval")
    x0=self.get_number().value
    y0=self.get_number().value
    x1=self.get_number().value
    y1=self.get_number().value
    f=self.get_number_or_none().value
    o=self.get_number_or_none().value
    w=self.get_number().value
    print(f"oval {x0} {y0} {x1} {y1} {f} {o} {w}")
    self.draw.ellipse((x0,y0,x1,y1),fill=None if f is None else pal[f],outline=None if o is None else pal[o],width=w)
    self.end_tag("do_oval") 



  def do_rect(self):
    self.begin_tag("do_rect")
    self.check(TokenType.IDENT,"rect")
    x0=self.get_number().value
    y0=self.get_number().value
    x1=self.get_number().value
    y1=self.get_number().value
    f=self.get_number_or_none().value
    o=self.get_number_or_none().value
    w=self.get_number().value
    print(f"rect {x0} {y0} {x1} {y1} {f} {o} {w}")
    self.draw.rectangle((x0,y0,x1,y1),fill=None if f is None else pal[f],outline=None if o is None else pal[o],width=w)
    self.end_tag("do_rect") 



  def do_arc(self):
    self.begin_tag("do_arc")
    self.check(TokenType.IDENT,"arc")
    x0=self.get_number().value
    y0=self.get_number().value
    x1=self.get_number().value
    y1=self.get_number().value
    s=self.get_number().value
    e=self.get_number().value       
    f=self.get_number_or_none().value
    w=self.get_number().value
    print(f"arc {x0} {y0} {x1} {y1} {f} {o} {w}")
    self.draw.rectangle((x0,y0,x1,y1),start=s,end=e,fill=None if f is None else pal[f],width=w)    
    self.end_tag("do_arc") 



  def do_chord(self):
    self.begin_tag("do_chord")
    self.check(TokenType.IDENT,"chord")
    x0=self.get_number().value
    y0=self.get_number().value
    x1=self.get_number().value
    y1=self.get_number().value
    s=self.get_number().value
    e=self.get_number().value       
    f=self.get_number_or_none().value
    w=self.get_number().value
    print(f"chord {x0} {y0} {x1} {y1} {f} {o} {w}")
    self.draw.chord((x0,y0,x1,y1),start=s,end=e,fill=None if f is None else pal[f],width=w)    
    self.end_tag("do_chord") 



  def do_pie(self):
    self.begin_tag("do_pie")
    self.check(TokenType.IDENT,"pie")
    x0=self.get_number().value
    y0=self.get_number().value
    x1=self.get_number().value
    y1=self.get_number().value
    s=self.get_number().value
    e=self.get_number().value       
    f=self.get_number_or_none().value
    w=self.get_number().value
    print(f"pie {x0} {y0} {x1} {y1} {f} {o} {w}")
    self.draw.pieslice((x0,y0,x1,y1),start=s,end=e,fill=None if f is None else pal[f],width=w)    
    self.end_tag("do_pie") 



  def do_poly(self):
    self.begin_tag("do_poly")
    self.check(TokenType.IDENT,"poly")
    start=self.pc
    count=0
    while self.get_type() not in [TokenType.NEW_LINE,TokenType.EOF]:
      count+=1
    self.pc=start
    p=[]
    for _ in range(0,count-3,2):
      p.append(
        self.get_number().value,
        self.get_number().value
      )
    f=self.get_number_or_none().value
    o=self.get_number_or_none().value
    w=self.get_number().value
    print(f"poly {p} {f} {o} {w}")
    self.draw.polygon(p,fill=None if f is None else pal[f],outline=None if o is None else pal[o],width=w)
    self.end_tag("do_poly") 



  def do_clear(self):
    self.begin_tag("do_clear")
    self.check(TokenType.IDENT,"clear")
    f=self.get_number().value
    w,h=self.img.size
    print(f"clear {f}")
    self.draw.rectangle((0,0,w,h),fill=pal[f])
    self.end_tag("do_clear") 



  def do_debug(self):
    result=None
    self.check(TokenType.IDENT,"debug")
    self.glo["debug"]=self.get_integer()



  def do_globals(self):
    self.begin_tag("do_globals") 
    self.check(TokenType.IDENT,"globals")
    for key in self.glo:
      print(key,"=",self.glo[key])
    self.end_tag("do_globals") 



  def do_datetime(self):
    self.begin_tag("do_datetime")
    self.check(TokenType.IDENT,"datetime")
    now=datetime.now()
    self.glo["VAR_"+self.get_ident().value]=Token(0,0,TokenType.INTEGER,now.year)
    self.glo["VAR_"+self.get_ident().value]=Token(0,0,TokenType.INTEGER,now.month)
    self.glo["VAR_"+self.get_ident().value]=Token(0,0,TokenType.INTEGER,now.day)
    self.glo["VAR_"+self.get_ident().value]=Token(0,0,TokenType.INTEGER,now.hour)
    self.glo["VAR_"+self.get_ident().value]=Token(0,0,TokenType.INTEGER,now.minute)
    self.glo["VAR_"+self.get_ident().value]=Token(0,0,TokenType.INTEGER,now.second)
    self.glo["VAR_"+self.get_ident().value]=Token(0,0,TokenType.INTEGER,now.microsecond)
    self.end_tag("do_datetime") 



  def do_end(self):
    self.begin_tag("do_end") 
    self.check(TokenType.IDENT,"end")
    self.quit=True
    self.end_tag("do_end") 






  def eval(self):
    self.begin_tag("eval") 
              
    if self.get_type()==TokenType.IDENT:
    
      if self.get_value()=="set":
        self.do_set()
      elif self.get_value()=="get":
        self.do_get()
      elif self.get_value()=="say":
        self.do_say()
      elif self.get_value()=="add":
        self.do_add()
      elif self.get_value()=="sub":
        self.do_sub()
      elif self.get_value()=="mul":
        self.do_mul()
      elif self.get_value()=="div":
        self.do_div()
      elif self.get_value()=="mod":
        self.do_mod()
      elif self.get_value()=="call":
        self.do_call()
      elif self.get_value()=="ret":
        self.do_ret()
      elif self.get_value()=="jmp":
        self.do_jmp()
      elif self.get_value()=="je":
        self.do_je()
      elif self.get_value()=="jne":
        self.do_jne()
      elif self.get_value()=="jl":
        self.do_jl()
      elif self.get_value()=="jle":
        self.do_jle()
      elif self.get_value()=="jg":
        self.do_jg()
      elif self.get_value()=="jge":
        self.do_jge()
      elif self.get_value()=="push":
        self.do_push()
      elif self.get_value()=="pop":
        self.do_pop()
      elif self.get_value()=="int":
        self.do_int()
      elif self.get_value()=="flt":
        self.do_flt()
      elif self.get_value()=="str":
        self.do_str()
      elif self.get_value()=="rnd":
        self.do_rnd()
      elif self.get_value()=="sin":
        self.do_sin()
      elif self.get_value()=="cos":
        self.do_cos()
      elif self.get_value()=="tan":
        self.do_tan()
      elif self.get_value()=="pset":
        self.do_pset()
      elif self.get_value()=="line":
        self.do_line()
      elif self.get_value()=="oval":
        self.do_oval()
      elif self.get_value()=="rect":
        self.do_rect()
      elif self.get_value()=="arc":
        self.do_arc()
      elif self.get_value()=="chord":
        self.do_chord()
      elif self.get_value()=="pie":
        self.do_pie()
      elif self.get_value()=="poly":
        self.do_poly()
      elif self.get_value()=="clear":
        self.do_clear()
      elif self.get_value()=="debug":
        self.do_debug()
      elif self.get_value()=="globals":
        self.do_globals()
      elif self.get_value()=="datetime":
        self.do_datetime()
      elif self.get_value()=="end":
        self.do_end()
      else:
        self.error(f"invalid command {self.get_value()}")

    self.end_tag("eval") 






  def parse(self):

    self.load_labels()

    """
    for i in range(len(self.tokens)):
      print(i,self.tokens[i])
    """

    while not self.quit and not self.get_type()==TokenType.EOF:

      while self.get_type() in [TokenType.NEW_LINE,TokenType.LABEL,TokenType.COMMENT]:
        self.next()

      self.eval()

    self.img.save(self.image_path)





