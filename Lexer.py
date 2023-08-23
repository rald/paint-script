from LexerState import LexerState
from Token import Token
from TokenType import TokenType

class Lexer(object):



  @staticmethod
  def lex(s):
    quit=False
    state=LexerState.DEFAULT
    tokens=[]
    text=""
    i=0
    ln=1
    cl=1
    scl=0
    has_dot=False
    while not quit:

      if i<len(s): 
        c=s[i] 
      else: 
        state=LexerState.QUIT

      if state==LexerState.DEFAULT:
        if c=='\"':
          scl=cl
          state=LexerState.STRING
        elif c==';':
          tokens.append(Token(ln,cl,TokenType.SEMICOLON,c))
        elif c==':':
          state=LexerState.LABEL
        elif c=='#':
          scl=cl
          i-=1
          cl-=1
          state=LexerState.COMMENT
        elif i<len(s)-1 and s[i]=="/" and s[i+1]=="/":
          scl=cl
          i-=1
          cl-=1
          state=LexerState.COMMENT
        elif (i<len(s)-1 and s[i]=="/" and s[i+1]=="*"):
          scl=cl
          i-=1
          cl-=1
          state=LexerState.MULTILINE_COMMENT 
        elif c=='\n':
          tokens.append(Token(ln,cl,TokenType.NEW_LINE,c))  
          ln+=1
          cl=0  
        elif c=='+' or c=='-' or c.isdigit():
          scl=cl
          text=c
          state=LexerState.NUMBER
        elif c.isalpha():
          scl=cl
          i-=1
          cl-=1
          state=LexerState.IDENT
        elif c=='(':
          tokens.append(Token(ln,cl,TokenType.OPEN_PAREN,text))
        elif c==')':
          tokens.append(Token(ln,cl,TokenType.CLOSE_PAREN,text))
        elif c=='[':
          tokens.append(Token(ln,cl,TokenType.OPEN_BRACKET,text))
        elif c==']':
          tokens.append(Token(ln,cl,TokenType.CLOSE_BRAKET,text))
        elif c.isspace():
          pass
        else:
          state=LexerState.QUIT
      elif state==LexerState.STRING:
        if c!='\"':
          text+=c
        else:
          tokens.append(Token(ln,scl,TokenType.STRING,text))
          text=""
          state=LexerState.DEFAULT
      elif state==LexerState.NUMBER:
        if c.isdigit() or (not has_dot and c=='.'):
          if c=='.': has_dot=True
          text+=c
        else:
          if has_dot:
            tokens.append(Token(ln,scl,TokenType.FLOAT,float(text)))
          else:
            tokens.append(Token(ln,scl,TokenType.INTEGER,int(text)))          
          has_dot=False
          text=""
          i-=1
          cl-=1
          state=LexerState.DEFAULT
          
      elif state==LexerState.IDENT:
        if c.isalnum() or c=='_':
          text+=c
        else:
          if text=='none':
            tokens.append(Token(ln,scl,TokenType.NONE,None))
          elif text=='false':
            tokens.append(Token(ln,scl,TokenType.FALSE,False))
          elif text=='true':
            tokens.append(Token(ln,scl,TokenType.TRUE,True))
          else:
            tokens.append(Token(ln,scl,TokenType.IDENT,text))
            
          text=""
          i-=1
          cl-=1
          state=LexerState.DEFAULT       

      elif state==LexerState.LABEL:
        if c.isalnum() or c=='_':
          text+=c
        else:
          tokens.append(Token(ln,scl,TokenType.LABEL,text))
          text=""
          i-=1
          cl-=1
          state=LexerState.DEFAULT       

      elif state==LexerState.COMMENT:

        if c!="\n":
          text+=c
        else:
          tokens.append(Token(ln,scl,TokenType.COMMENT,text))
          text=""
          i-=1
          cl-=1
          state=LexerState.DEFAULT       

      elif state==LexerState.MULTILINE_COMMENT:
        
        if i<len(s)-1 and not (s[i]=="*" and s[i+1]=="/"):
          text+=c+"*/"
        else:
          tokens.append(Token(ln,scl,TokenType.COMMENT,text))
          text=""
          state=LexerState.DEFAULT       

      elif state==LexerState.QUIT:
        quit=True

      if i<len(s): 
        i+=1 
        cl+=1
      else: 
        state=LexerState.QUIT

    tokens.append(Token(ln,cl,TokenType.EOF,None))

    return tokens  






