from enum import Enum

class TokenType(Enum):
  NONE = 0
  INTEGER = 1
  FLOAT = 2
  STRING = 3
  FALSE = 4
  TRUE = 5

  IDENT = 6

  COLON = 11
  SEMI_COLON = 12
  NEW_LINE = 13
  
  LABEL = 14

  AT = 15
  DOLLAR = 16
  PERCENT = 17

  COMMENT = 18

  EOF = 19





