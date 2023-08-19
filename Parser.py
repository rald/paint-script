import os
import random 
import PIL
from PIL import Image, ImageDraw
from datetime import datetime

from palette import pal
from TokenType import TokenType



def resize_canvas(
    old_image_path, 
    new_image_path,
    canvas_width=256, 
    canvas_height=256):
  """
  Resize the canvas of old_image_path.

  Store the new image in new_image_path. Center the image on the new canvas.

  Parameters
  ----------
  old_image_path : str
  new_image_path : str
  canvas_width : int
  canvas_height : int
  """
  im = Image.open(old_image_path)
  old_width, old_height = im.size

  # Center the image
  x1 = int(math.floor((canvas_width - old_width) / 2))
  y1 = int(math.floor((canvas_height - old_height) / 2))

  mode = im.mode
  if len(mode) == 1:  # L, 1
      new_background = (255)
  if len(mode) == 3:  # RGB
      new_background = (255, 255, 255)
  if len(mode) == 4:  # RGBA, CMYK
      new_background = (255, 255, 255, 255)

  newImage = Image.new(mode, (canvas_width, canvas_height), new_background)
  newImage.paste(im, (x1, y1, x1 + old_width, y1 + old_height))
  newImage.save(new_image_path)





class Parser:

  def __init__(self,tokens,image_path):
    self.debug=0

    self.id=id

    self.tokens=tokens
    self.pc=0
    self.glo={}
    self.lab={}
    self.ret=[]
    self.stk=[]    
    self.quit=False

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
      if self.debug==1: print(f"pc: {self.pc}")

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
    result=None
    self.match(TokenType.INTEGER)
    result=int(self.get_text())
    self.next()
    return result

  def get_float(self):
    result=None
    self.match(TokenType.FLOAT)
    result=float(self.get_text())
    self.next()
    return result

  def get_string(self):
    result=None
    self.match(TokenType.STRING)
    result=self.get_text()
    self.next()
    return result 

  def get_label(self):
    self.match(TokenType.IDENT)
    label_name=self.get_text()
    if label_name not in self.lab:
      self.error(f"undefined label {label_name}")
    return label_name 

  def get_none(self):
    self.match(TokenType.NONE)
    self.next()
    return None 

  def get_value(self):
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
      ident_name=self.get_ident_check()
      result=self.glo[ident_name]
    else:
      self.error(f"found {self.get_type()} expected NUMBER")
    return result

  def check(self,type,text):
    self.match(TokenType.IDENT)
    if self.get_text()!=text:
      self.error(f"found '{self.get_text()}' expected {text}")  
    self.next()

  def get_ident(self):
    self.match(TokenType.IDENT)
    return self.get_text()

  def get_ident_check(self):
    ident_name=self.get_ident()
    if ident_name not in self.glo:
      self.error(f"undefined ident {ident_name}")
    self.next()
    return ident_name

  def get_label_check(self):
    label_name=self.get_label()
    if label_name not in self.lab:
      self.error(f"undefined label {label_name}")
    self.next()
    return label_name
   
  def do_say(self):
    result=""
    self.check(TokenType.IDENT,"say")
    while self.get_type() not in [TokenType.NEW_LINE,TokenType.EOF]:
      result+=str(self.get_value())
    print(result)

  def do_ask(self):
    result=""
    self.check(TokenType.IDENT,"ask")
    ident_name=self.get_ident_check()
    msg=self.get_value()
    self.set_glo[ident_name]=input(msg)
  
  def do_push(self):
    self.check(TokenType.IDENT,"push")
    while self.get_type() not in [TokenType.NEW_LINE,TokenType.EOF]:
      self.stk.append(self.get_value())
  
  def do_pop(self):
    self.check(TokenType.IDENT,"pop")
    while self.get_type() not in [TokenType.NEW_LINE,TokenType.EOF]:
      ident_name=self.get_ident_check()
      self.glo[ident_name]=self.stk.pop()

  def do_set(self):
    result=None
    self.check(TokenType.IDENT,"set")
    if self.get_type()==TokenType.IDENT:
      ident_name=self.get_ident()
      self.next()
    result=self.get_value()
    while self.get_type() not in [TokenType.NEW_LINE,TokenType.EOF]:
      result=str(result)+str(self.get_value())
    self.glo[ident_name]=result

  def do_add(self):
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

  def do_sub(self):
    result=None
    self.check(TokenType.IDENT,"sub")
    ident_name=self.get_ident_check()
    result=self.glo[ident_name]
    while self.get_type() not in [TokenType.NEW_LINE,TokenType.EOF]:
      value=self.get_value()
      result-=value
    self.glo[ident_name]=result

  def do_mul(self):
    result=None
    self.check(TokenType.IDENT,"mul")
    ident_name=self.get_ident_check()
    result=self.glo[ident_name]
    while self.get_type() not in [TokenType.NEW_LINE,TokenType.EOF]:
      value=self.get_value()
      result*=value
    self.glo[ident_name]=result

  def do_div(self):
    result=None
    self.check(TokenType.IDENT,"div")
    ident_name=self.get_ident_check()
    result=self.glo[ident_name]
    while self.get_type() not in [TokenType.NEW_LINE,TokenType.EOF]:
      value=self.get_value()
      if value!=0:
        result/=value
      else:
        self.error("divide by zero")
    self.glo[ident_name]=result

  def do_mod(self):
    result=None
    self.check(TokenType.IDENT,"mod")
    ident_name=self.get_ident_check()
    value=self.get_value()
    self.glo[ident_name]%=value


  def do_jmp(self):

    self.check(TokenType.IDENT,"jmp")

    label_name=self.get_ident()
    if label_name not in self.lab:
      self.error(f"undefined label {label_name}")
    self.pc=self.lab[label_name]
    self.next()

  def do_call(self):
    self.check(TokenType.IDENT,"call")
    label_name=self.get_label_check();
    self.ret.append(self.pc)
    self.pc=self.lab[label_name]
    
  def do_ret(self):
    self.check(TokenType.IDENT,"ret")
    self.pc=self.ret.pop()

  def do_and(self):
    self.check(TokenType.IDENT,"and")
    ident_name=self.get_ident_check()
    a=int(self.get_value())
    b=int(self.get_value())
    self.glo[ident_name]=a & b

  def do_or(self):
    self.check(TokenType.IDENT,"or")
    ident_name=self.get_ident_check()
    a=int(self.get_value())
    b=int(self.get_value())
    self.glo[ident_name]=a | b

  def do_not(self):
    self.check(TokenType.IDENT,"not")
    ident_name=self.get_ident_check()
    self.glo[ident_name]=~self.glo[ident_name]

 
  def do_jeq(self):
    self.check(TokenType.IDENT,"jeq")
    label_name=self.get_label_check()
    a=self.get_value()
    b=self.get_value()
    if a==b:
      self.pc=self.lab[label_name]

  def do_jne(self):
    self.check(TokenType.IDENT,"jne")
    label_name=self.get_label_check()
    a=self.get_value()
    b=self.get_value()
    if a!=b:
      self.pc=self.lab[label_name]

  def do_jl(self):
    self.check(TokenType.IDENT,"jl")
    label_name=self.get_label_check()
    a=self.get_value()
    b=self.get_value()
    if a<b:
      self.pc=self.lab[label_name]

  def do_jle(self):
    self.check(TokenType.IDENT,"jle")
    label_name=self.get_label_check()
    a=self.get_value()
    b=self.get_value()
    if a<=b:
      self.pc=self.lab[label_name]

  def do_jg(self):
    self.check(TokenType.IDENT,"jg")
    label_name=self.get_label_check()
    a=self.get_value()
    b=self.get_value()
    if a>b:
      self.pc=self.lab[label_name]
    
  def do_jge(self):
    self.check(TokenType.IDENT,"jge")
    label_name=self.get_label_check()
    a=self.get_value()
    b=self.get_value()
    if a>=b:
      self.pc=self.lab[label_name]

  def do_int(self):
    self.check(TokenType.IDENT,"int")
    ident_name=self.get_ident_check()
    value=int(self.get_value())
    self.glo[ident_name]=value

  def do_flt(self):
    self.check(TokenType.IDENT,"flt")
    ident_name=self.get_ident_check()
    value=float(self.get_value())
    self.glo[ident_name]=value

  def do_str(self):
    self.check(TokenType.IDENT,"str")
    ident_name=self.get_ident_check()
    value=str(self.get_value())
    self.glo[ident_name]=value

  def do_rnd(self):
    self.check(TokenType.IDENT,"rnd")
    ident_name=self.get_ident_check()
    s=self.get_value()
    e=self.get_value()   
    self.glo[ident_name]=random.randint(s,e)

  def do_end(self):
    self.check(TokenType.IDENT,"end")
    self.quit=True







  def do_line(self):
    self.check(TokenType.IDENT,"line")
    
    x0=self.get_value()
    y0=self.get_value()
    x1=self.get_value()
    y1=self.get_value()
    f=self.get_value()
    w=self.get_value()

    print(f"line {x0} {y0} {x1} {y1} {f} {w}")

    try:
      self.draw.line((x0,y0,x1,y1),fill=None if f==None else pal[f],width=w)      
      self.img.save(self.image_path)
    except:
      self.error("Drawing Error")



  def do_oval(self):
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



  def do_rect(self):
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



  def do_arc(self):
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



  def do_chord(self):
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



  def do_pie(self):
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



  def do_poly(self):
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


  def do_clear(self):
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


  def do_datetime(self):
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
        


  def do_setsize(self):
    self.check(TokenType.IDENT,"setsize")

    w=self.get_value()
    h=self.get_value()

    resize_canvas(self.image_path,self.image_path,w,h)

    self.img=Image.open(self.image_path).convert('RGB')



  def do_getsize(self):
    self.check(TokenType.IDENT,"getsize")

    ident_name1=self.get_ident_check()
    ident_name2=self.get_ident_check()

    w,h=self.img.size

    self.glo[ident_name1]=w
    self.glo[ident_name2]=h





  def eval(self):

    while self.get_type() in [TokenType.NEW_LINE,TokenType.LABEL,TokenType.COMMENT]:
      self.next()
              
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
      else:
        self.error(f"invalid command {self.get_text()}")



  def parse(self):

    self.read_labels()

    if self.debug==1:
      for key in self.lab:
        print(key,self.lab[key])
    
      print("\n\n")

      for i in range(len(self.tokens)):
        print(i,self.tokens[i])

      print("\n\n")

    while not self.quit and not self.get_type()==TokenType.EOF:
      self.eval()

