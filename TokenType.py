from enum import Enum

class TokenType(Enum):
  NONE = 0
  INTEGER = 1
  FLOAT = 2
  STRING = 3
  FALSE = 4
  TRUE = 5

  IDENT = 6

  OPEN_PAREN = 7
  CLOSE_PAREN = 8

  OPEN_BRACKET = 9
  CLOSE_BRACKET = 10

  COLON = 11
  NEW_LINE = 12
  
  LABEL = 13

  AT = 14
  DOLLAR = 15
  PERCENT = 16

  COMMENT = 17

  EOF = 18

