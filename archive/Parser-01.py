import os
import random 
import PIL
from PIL import Image, ImageDraw
from datetime import datetime

from palette import pal
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

    self.glo["env"]=""
    self.glo["debug"]=0

    self.env=self.glo["env"]

    self.indent=0

    self.image_path=image_path

    if os.path.isfile(self.image_path):
      self.img=Image.open(self.image_path).convert('RGB')
    else:
      self.img=PIL.Image.new(mode="RGB", size=(640,480), color=pal[12])

    self.draw=ImageDraw.Draw(self.img)




  def next(self):
    if self.get_type()==TokenType.EOF:
      self.error("end of file")
    else:
      self.pc+=1
      if self.glo["debug"]==1: print(f"pc: {self.pc}")


  def begin_tag(self,text):
    if self.glo["debug"]==1:
      print("  "*self.indent,end="")   
      print(f"<{text}>")
    self.indent+=1

  def end_tag(self,text):
    self.indent-=1
    if self.glo["debug"]==1:
      print("  "*self.indent,end="")   
      print(f"</{text}>")
  
  def read_labels(self):
    for i in range(len(self.tokens)):
      if self.tokens[i].type==TokenType.LABEL:
        label_name=self.tokens[i].text
        if label_name in self.lab:
          print(f"{self.tokens[i].line}:{self.tokens[i].column}:label redefined: {label_name}")
          quit()
        self.lab[label_name]=i;

  def get_line(self):
    return self.look().line

  def get_column(self):
    return self.look().column

  def error(self,msg):
    print(f"\n{self.get_line()}:{self.get_column()}: {msg}")
    quit()

  def look(self):
    return self.tokens[self.pc]

  def peek(self,offset):
    return self.tokens[self.pc+offset]

  def match(self,type):
    if self.look().type!=type:
      self.error(f"found {self.look().type} expected {type}")      
 
  def get_type(self):
    return self.look().type

  def get_text(self):
    return self.look().text

  def eat(self,type,count=1):
    for _ in range(count):
      self.match(type)
      self.next()
      
  def get_integer(self):
    self.begin_tag("get_integer") 
    result=None
    self.match(TokenType.INTEGER)
    result=int(self.get_text())
    self.next()
    self.end_tag("get_integer") 
    return result

  def get_float(self):
    self.begin_tag("get_float") 
    result=None
    self.match(TokenType.FLOAT)
    result=float(self.get_text())
    self.next()
    self.end_tag("get_float") 
    return result

  def get_string(self):
    self.begin_tag("get_string") 
    result=None
    self.match(TokenType.STRING)
    result=self.get_text()
    self.next()
    self.end_tag("get_string") 
    return result 

  def get_label(self):
    self.begin_tag("get_label") 
    self.match(TokenType.IDENT)
    label_name=self.get_text()
    if label_name not in self.lab:
      self.error(f"undefined label {label_name}")
    self.end_tag("get_label") 
    return label_name 

  def get_none(self):
    self.begin_tag("get_none") 
    self.match(TokenType.NONE)
    self.next()
    self.end_tag("get_none") 
    return None 



  def get_at(self):
    self.begin_tag("get_at") 

    result=None
    count=0
    env=None

    while self.get_type()==TokenType.AT:
      count+=1
      self.next()

    if self.get_type()==TokenType.DOLLAR:
      env=self.glo["env"]    
      self.next()
    
    if self.get_type()==TokenType.PERCENT:        
      self.next()
      index=self.get_integer()
      if index<0 and index>=len(self.prm):
        self.error(f"index out of bounds {index}")
      result=self.prm[index] if env is None else env+"_"+str(self.prm[index])
    elif self.get_type()==TokenType.IDENT:
      result=self.get_text() if env==None else env+"_"+self.get_text()
      self.next()
    else:
      self.error("invalid IDENT")

    for _ in range(count):
      if result not in self.glo:
        self.error(f"undefined identifier {result}")
      result=self.glo[result]
    self.end_tag("get_at") 
    return result



  def get_ident(self):
    self.begin_tag("get_ident")
    ident_name=self.get_text()
    self.next()
    self.end_tag("get_ident") 
    return ident_name



  def get_ident_check(self):
    self.begin_tag("get_ident_check") 
    ident_name=self.get_ident()
    if ident_name not in self.glo:
      self.error(f"get_ident_check: undefined identifier {ident_name}")
    self.end_tag("get_ident_check") 
    return ident_name



  def get_value(self):
    self.begin_tag("get_value") 
    result=None
    if self.get_type()==TokenType.NONE:
      result=self.get_none()
    elif self.get_type()==TokenType.INTEGER:
      result=self.get_integer()
    elif self.get_type()==TokenType.FLOAT:
      result=self.get_float()
    elif self.get_type()==TokenType.STRING:
      result=self.get_string()
    elif self.get_type()==TokenType.IDENT:
      result=self.get_ident_check()
    elif self.get_type() in [TokenType.AT,TokenType.DOLLAR,TokenType.PERCENT]:
      result=self.get_at_check()
    else:
      self.error(f"found {self.get_type()} expected VALUE")
    self.end_tag("get_value") 
    return result



  def check(self,type,text):
    self.begin_tag("check") 
    self.match(TokenType.IDENT)
    if self.get_text()!=text:
      self.error(f"found '{self.get_text()}' expected {text}")  
    self.next()
    self.end_tag("check") 



  def get_label_check(self):
    self.begin_tag("get_label_check") 
    label_name=self.get_label()
    if label_name not in self.lab:
      self.error(f"undefined label {label_name}")
    self.next()
    self.end_tag("get_label_check") 
    return label_name


   
  def do_say(self):
    self.begin_tag("do_say") 
    result=""
    self.check(TokenType.IDENT,"say")
    while self.get_type() not in [TokenType.NEW_LINE,TokenType.EOF]:
      if self.get_type()==TokenType.IDENT:
        ident_name=self.get_ident_check()
        value=self.glo[ident_name]
      else:
        value=self.get_value()
      result+=str(value)
    print(result)
    self.end_tag("do_say") 



  def do_ask(self):
    self.begin_tag("do_ask") 
    result=""
    self.check(TokenType.IDENT,"ask")
    ident_name=self.get_ident_check()
    msg=self.get_value()
    self.set_glo[ident_name]=input(msg)
    self.end_tag("do_ask") 
  
  def do_push(self):
    self.begin_tag("do_push") 
    self.check(TokenType.IDENT,"push")
    while self.get_type() not in [TokenType.NEW_LINE,TokenType.EOF]:
      self.stk.append(self.get_value())
    self.end_tag("do_push") 

  def do_pop(self):
    self.begin_tag("do_pop") 
    self.check(TokenType.IDENT,"pop")
    while self.get_type() not in [TokenType.NEW_LINE,TokenType.EOF]:
      ident_name=self.get_ident_check()
      self.glo[ident_name]=self.stk.pop()
    self.end_tag("do_pop") 

  def do_set(self):
    self.begin_tag("do_set") 
    result=None
    self.check(TokenType.IDENT,"set")
    ident_name=self.get_ident()
    result=self.get_value()
    while self.get_type() not in [TokenType.NEW_LINE,TokenType.EOF]:
      result=str(result)+str(self.get_value())
    self.glo[ident_name]=result
    self.end_tag("do_set") 

  def do_add(self):
    self.begin_tag("do_add") 
    result=0
    self.check(TokenType.IDENT,"add")
    ident_name=self.get_ident_check()
    result=self.glo[ident_name]
    while self.get_type() not in [TokenType.NEW_LINE,TokenType.EOF]:
      value=self.get_value()
      if isinstance(result,str) or isinstance(value,str):
        result=str(result)+str(value)
      else:
        result+=value
    self.glo[ident_name]=result
    self.end_tag("do_add") 

  def do_sub(self):
    self.begin_tag("do_sub") 
    result=None
    self.check(TokenType.IDENT,"sub")
    ident_name=self.get_ident_check()
    result=self.glo[ident_name]
    while self.get_type() not in [TokenType.NEW_LINE,TokenType.EOF]:
      value=self.get_value()
      result-=value
    self.glo[ident_name]=result
    self.end_tag("do_sub") 



  def do_mul(self):
    self.begin_tag("do_mul") 
    result=None
    self.check(TokenType.IDENT,"mul")
    value=self.get_at()
    while self.get_type() not in [TokenType.NEW_LINE,TokenType.EOF]:
      value=self.get_value()
      result*=value
    self.glo[ident_name]=result
    self.end_tag("do_mul") 



  def do_div(self):
    self.begin_tag("do_div") 
    result=None
    self.check(TokenType.IDENT,"div")
    ident_name=self.get_ident()
    self.next()
    result=self.glo[ident_name]
    while self.get_type() not in [TokenType.NEW_LINE,TokenType.EOF]:
      value=self.get_value()
      if value!=0:
        result/=value
      else:
        self.error("divide by zero")
    self.glo[ident_name]=result
    self.end_tag("do_div") 

  def do_mod(self):
    self.begin_tag("do_mod") 
    result=None
    self.check(TokenType.IDENT,"mod")
    ident_name=self.get_ident_check()
    value=self.get_value()
    self.glo[ident_name]%=value
    self.end_tag("do_mod") 


  def do_jmp(self):
    self.begin_tag("do_jmp") 
    self.check(TokenType.IDENT,"jmp")
    label_name=self.get_ident()
    if label_name not in self.lab:
      self.error(f"undefined label {label_name}")
    self.pc=self.lab[label_name]
    self.next()
    self.end_tag("do_jmp") 



  def do_call(self):
    self.begin_tag("do_call") 
    self.check(TokenType.IDENT,"call")
    label_name=self.get_label_check();

    prm=[]
    while self.get_type() not in [TokenType.NEW_LINE,TokenType.EOF]:
      value=self.get_value()
      prm.append(value)

    self.ret.append(
      {
        "env":self.glo["env"],
        "prm":self.prm,
        "pc":self.pc
      }
    )

    self.prm=prm
    self.glo["env"]=label_name
    self.pc=self.lab[label_name]

    self.end_tag("do_call") 

    
  def do_ret(self):
    self.begin_tag("do_ret") 
    self.check(TokenType.IDENT,"ret")
    ret=self.ret.pop()
    self.glo["env"]=ret["env"]
    self.prm=ret["prm"]
    self.pc=ret["pc"]
    if self.glo["debug"]==1: print("</ret>") 
    self.end_tag("do_ret") 



  def do_and(self):
    self.begin_tag("do_and") 
    self.check(TokenType.IDENT,"and")
    ident_name=self.get_ident_check()
    a=int(self.get_value())
    b=int(self.get_value())
    self.glo[ident_name]=a & b
    self.end_tag("do_and") 

  def do_or(self):
    self.begin_tag("do_or") 
    self.check(TokenType.IDENT,"or")
    ident_name=self.get_ident_check()
    a=int(self.get_value())
    b=int(self.get_value())
    self.glo[ident_name]=a | b
    self.end_tag("do_or") 

  def do_not(self):
    self.begin_tag("do_not") 
    self.check(TokenType.IDENT,"not")
    ident_name=self.get_ident_check()
    self.glo[ident_name]=~self.glo[ident_name]
    self.end_tag("do_not") 

 
  def do_jeq(self):
    self.begin_tag("do_jeq") 
    self.check(TokenType.IDENT,"jeq")
    label_name=self.get_label_check()
    a=self.get_value()
    b=self.get_value()
    if a==b:
      self.pc=self.lab[label_name]
    self.end_tag("do_jeq") 

  def do_jne(self):
    self.begin_tag("do_jne") 
    self.check(TokenType.IDENT,"jne")
    label_name=self.get_label_check()
    a=self.get_value()
    b=self.get_value()
    if a!=b:
      self.pc=self.lab[label_name]
    self.end_tag("do_jne") 

  def do_jl(self):
    self.begin_tag("do_jl") 
    self.check(TokenType.IDENT,"jl")
    label_name=self.get_label_check()
    a=self.get_value()
    b=self.get_value()
    if a<b:
      self.pc=self.lab[label_name]
    self.end_tag("do_jl") 

  def do_jle(self):
    self.begin_tag("do_jle") 
    self.check(TokenType.IDENT,"jle")
    label_name=self.get_label_check()
    a=self.get_value()
    b=self.get_value()
    if a<=b:
      self.pc=self.lab[label_name]
    self.end_tag("do_jle") 

  def do_jg(self):
    self.begin_tag("do_jg") 
    self.check(TokenType.IDENT,"jg")
    label_name=self.get_label_check()
    a=self.get_value()
    b=self.get_value()
    if a>b:
      self.pc=self.lab[label_name]
    self.end_tag("do_jg") 
    
  def do_jge(self):
    self.begin_tag("do_jge") 
    self.check(TokenType.IDENT,"jge")
    label_name=self.get_label_check()
    a=self.get_value()
    b=self.get_value()
    if a>=b:
      self.pc=self.lab[label_name]
    self.end_tag("do_jge") 

  def do_int(self):
    self.begin_tag("do_int") 
    self.check(TokenType.IDENT,"int")
    ident_name=self.get_ident_check()
    value=int(self.get_value())
    self.glo[ident_name]=value
    self.end_tag("do_int") 

  def do_flt(self):
    self.begin_tag("do_flt") 
    self.check(TokenType.IDENT,"flt")
    ident_name=self.get_ident_check()
    value=float(self.get_value())
    self.glo[ident_name]=value
    self.end_tag("do_flt") 

  def do_str(self):
    self.begin_tag("do_str") 
    self.check(TokenType.IDENT,"str")
    ident_name=self.get_ident_check()
    value=str(self.get_value())
    self.glo[ident_name]=value
    self.end_tag("do_str") 

  def do_rnd(self):
    self.begin_tag("do_rnd") 
    self.check(TokenType.IDENT,"rnd")
    ident_name=self.get_ident_check()
    s=self.get_value()
    e=self.get_value()   
    self.glo[ident_name]=random.randint(s,e)
    self.end_tag("do_rnd") 

  def do_end(self):
    self.begin_tag("do_end") 
    self.check(TokenType.IDENT,"end")
    self.quit=True
    self.end_tag("do_end") 







  def do_line(self):
    self.begin_tag("do_line") 
    self.check(TokenType.IDENT,"line")
    
    x0=self.get_value()
    y0=self.get_value()
    x1=self.get_value()
    y1=self.get_value()
    f=self.get_value()
    w=self.get_value()

    if self.glo["debug"]==1:
      print(f"line {x0} {y0} {x1} {y1} {f} {w}")

    try:
      self.draw.line((x0,y0,x1,y1),fill=None if f==None else pal[f],width=w)      
      self.img.save(self.image_path)
    except:
      self.error("Drawing Error")
    self.end_tag("do_line") 



  def do_oval(self):
    self.begin_tag("do_oval") 
    self.check(TokenType.IDENT,"oval")
    
    x0=self.get_value()
    y0=self.get_value()
    x1=self.get_value()
    y1=self.get_value()
    f=self.get_value()
    o=self.get_value()    
    w=self.get_value()

    print(f"oval {x0} {y0} {x1} {y1} {f} {o} {w}")

    try:
      self.draw.ellipse((x0,y0,x1,y1),fill=None if f==None else pal[f],outline=None if o==None else pal[o],width=w)      
      self.img.save(self.image_path)
    except:
      self.error("Drawing Error")
    self.end_tag("do_oval") 



  def do_rect(self):
    self.begin_tag("do_rect") 
    self.check(TokenType.IDENT,"rect")
    
    x0=self.get_value()
    y0=self.get_value()
    x1=self.get_value()
    y1=self.get_value()
    f=self.get_value()
    o=self.get_value()    
    w=self.get_value()

    print(f"rect {x0} {y0} {x1} {y1} {f} {o} {w}")

    try:
      self.draw.rectangle((x0,y0,x1,y1),fill=None if f==None else pal[f],outline=None if o==None else pal[o],width=w)      
      self.img.save(self.image_path)
    except:
      self.error("Drawing Error")
    self.end_tag("do_rect") 



  def do_arc(self):
    self.begin_tag("do_arc") 
    self.check(TokenType.IDENT,"arc")
    
    x0=self.get_value()
    y0=self.get_value()
    x1=self.get_value()
    y1=self.get_value()
    s=self.get_value()
    e=self.get_value()
    f=self.get_value()
    w=self.get_value()

    print(f"arc {x0} {y0} {x1} {y1} {f} {w}")

    try:
      self.draw.arc((x0,y0,x1,y1),start=s,end=e,fill=None if f==None else pal[f],width=w)      
      self.img.save(self.image_path)
    except:
      self.error("Drawing Error")
    self.end_tag("do_arc") 



  def do_chord(self):
    self.begin_tag("do_chord") 
    self.check(TokenType.IDENT,"chord")
    
    x0=self.get_value()
    y0=self.get_value()
    x1=self.get_value()
    y1=self.get_value()
    s=self.get_value()
    e=self.get_value()
    f=self.get_value()
    o=self.get_value()    
    w=self.get_value()

    print(f"chord {x0} {y0} {x1} {y1} {f} {o} {w}")

    try:
      self.draw.chord((x0,y0,x1,y1),start=s,end=e,fill=None if f==None else pal[f],outline=None if o==None else pal[f],width=w)      
      self.img.save(self.image_path)
    except:
      self.error("Drawing Error")
    self.end_tag("do_chord") 



  def do_pie(self):
    self.begin_tag("do_pie") 
    self.check(TokenType.IDENT,"pie")
    
    x0=self.get_value()
    y0=self.get_value()
    x1=self.get_value()
    y1=self.get_value()
    s=self.get_value()
    e=self.get_value()
    f=self.get_value()
    o=self.get_value()    
    w=self.get_value()

    print(f"pie {x0} {y0} {x1} {y1} {f} {o} {w}")

    try:
      self.draw.pieslice((x0,y0,x1,y1),start=s,end=e,fill=None if f==None else pal[f],outline=None if o==None else pal[f],width=w)      
      self.img.save(self.image_path)
    except:
      self.error("Drawing Error")
    self.end_tag("do_pie") 



  def do_poly(self):
    self.begin_tag("do_poly") 
    self.check(TokenType.IDENT,"poly")

    count=0
    start=self.pc
    while self.get_type() not in [TokenType.NEW_LINE,TokenType.EOF]:
      count+=1

    p=[]
    for i in range(0,count-3,2):
      p.append=((self.get_value(),self.get_value()))

    f=self.get_value()
    o=self.get_value()    
    w=self.get_value()

    print(f"poly {p} {f} {o} {w}")

    try:
      self.draw.polygon(p,start=s,end=e,fill=None if f==None else pal[f],outline=None if o==None else pal[f],width=w)      
      self.img.save(self.image_path)
    except:
      self.error("Drawing Error")
    self.end_tag("do_poly") 


  def do_clear(self):
    self.begin_tag("do_clear") 
    self.check(TokenType.IDENT,"clear")
    
    x0=0
    y0=0
    x1,y1=self.img.size
    f=self.get_value()

    print(f"clear {f}")

    try:
      self.draw.rectangle((x0,y0,x1,y1),fill=None if f==None else pal[f])      
      self.img.save(self.image_path)
    except:
      self.error("Drawing Error")
    self.end_tag("do_clear") 


  def do_datetime(self):
    self.begin_tag("do_datetime") 
    self.check(TokenType.IDENT,"datetime")
    
    Y=self.get_ident_check()
    M=self.get_ident_check()
    D=self.get_ident_check()
    h=self.get_ident_check()
    m=self.get_ident_check()
    s=self.get_ident_check()
    ms=self.get_ident_check()

    now=datetime.now()

    self.glo[Y]=now.year
    self.glo[M]=now.month
    self.glo[D]=now.day
    self.glo[h]=now.hour
    self.glo[m]=now.minute
    self.glo[s]=now.second
    self.glo[ms]=now.microsecond
    self.end_tag("do_datetime") 
        


  def do_setsize(self):
    self.begin_tag("do_setsize") 
    self.check(TokenType.IDENT,"setsize")

    w=self.get_value()
    h=self.get_value()

    resize_canvas(self.image_path,self.image_path,w,h)

    self.img=Image.open(self.image_path).convert('RGB')
    self.end_tag("do_setsize") 



  def do_getsize(self):
    self.begin_tag("do_getsize") 
    self.check(TokenType.IDENT,"getsize")

    ident_name1=self.get_ident_check()
    ident_name2=self.get_ident_check()

    w,h=self.img.size

    self.glo[ident_name1]=w
    self.glo[ident_name2]=h
    self.end_tag("do_getsize") 



  def do_debug(self):
    self.check(TokenType.IDENT,"debug")
    self.glo["debug"]=self.get_integer()

  def do_globals(self):
    self.begin_tag("do_globals") 
    self.check(TokenType.IDENT,"globals")
    for key in self.glo:
      print(f"{key} =",f"\"{self.glo[key]}\"" if isinstance(self.glo[key],str) else self.glo[key])
    self.end_tag("do_globals") 

  def do_labels(self):
    self.begin_tag("do_labels") 
    self.check(TokenType.IDENT,"labels")
    for key in self.lab:
      print(key,self.lab[key])
    self.end_tag("do_labels") 

  def do_params(self):
    self.begin_tag("do_params") 
    self.check(TokenType.IDENT,"params")
    for i in range(len(self.prm)):
      print(f"%{i} = {self.prm[i]}")
    self.end_tag("do_params") 

  def do_tokens(self):
    self.begin_tag("do_tokens") 
    self.check(TokenType.IDENT,"tokens")
    for i in range(len(self.tokens)):
      print(f"{i} {self.tokens[i]}")
    self.end_tag("do_tokens") 



  def eval(self):
    self.begin_tag("eval") 
              
    if self.get_type()==TokenType.IDENT:
    
      if self.get_text()=="say":
        self.do_say()
      elif self.get_text()=="ask":
        self.do_ask()
      elif self.get_text()=="push":
        self.do_push()
      elif self.get_text()=="pop":
        self.do_pop()
      elif self.get_text()=="set":
        self.do_set()
      elif self.get_text()=="add":
        self.do_add()
      elif self.get_text()=="sub":
        self.do_sub()
      elif self.get_text()=="mul":
        self.do_mul()
      elif self.get_text()=="div":
        self.do_div()
      elif self.get_text()=="mod":
        self.do_mod()
      elif self.get_text()=="and":
        self.do_and()
      elif self.get_text()=="or":
        self.do_or()
      elif self.get_text()=="not":
        self.do_not()
      elif self.get_text()=="jmp":
        self.do_jmp()
      elif self.get_text()=="jeq":
        self.do_jeq()
      elif self.get_text()=="jne":
        self.do_jne()
      elif self.get_text()=="jl":
        self.do_jl()
      elif self.get_text()=="jle":
        self.do_jle()
      elif self.get_text()=="jg":
        self.do_jg()
      elif self.get_text()=="jge":
        self.do_jge()
      elif self.get_text()=="call":
        self.do_call()
      elif self.get_text()=="ret":
        self.do_ret()
      elif self.get_text()=="int":
        self.do_int()
      elif self.get_text()=="flt":
        self.do_flt()
      elif self.get_text()=="str":
        self.do_str()
      elif self.get_text()=="end":
        self.do_end()
      elif self.get_text()=="line":
        self.do_line()
      elif self.get_text()=="oval":
        self.do_oval()
      elif self.get_text()=="rect":
        self.do_rect()
      elif self.get_text()=="arc":
        self.do_aec()
      elif self.get_text()=="chord":
        self.do_chord()
      elif self.get_text()=="pie":
        self.do_pie()
      elif self.get_text()=="poly":
        self.do_poly()
      elif self.get_text()=="clear":
        self.do_clear()
      elif self.get_text()=="rnd":
        self.do_rnd()
      elif self.get_text()=="datetime":
        self.do_datetime()
      elif self.get_text()=="setsize":
        self.do_setsize()
      elif self.get_text()=="getsize":
        self.do_getsize()
      elif self.get_text()=="debug":
        self.do_debug()
      elif self.get_text()=="labels":
        self.do_labels()
      elif self.get_text()=="globals":
        self.do_globals()
      elif self.get_text()=="params":
        self.do_params()
      elif self.get_text()=="tokens":
        self.do_tokens()
      else:
        self.error(f"invalid command {self.get_text()}")
    self.end_tag("eval") 



  def parse(self):
    self.read_labels()
    while not self.quit and not self.get_type()==TokenType.EOF:

      while self.get_type() in [TokenType.NEW_LINE,TokenType.LABEL,TokenType.COMMENT]:
        self.next()

      self.eval()

