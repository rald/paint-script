from enum import Enum

class TokenType(Enum):
  NONE = 0
  INTEGER = 1
  FLOAT = 2
  STRING = 3
  IDENT = 4

  OPEN_PAREN = 5
  CLOSE_PAREN = 6

  OPEN_BRACKET = 7
  CLOSE_BRACKET = 8

  COLON = 9
  NEW_LINE = 10
  
  LABEL = 11
  AT = 12

  COMMENT = 13

  EOF = 14

