from enum import Enum

class LexerState(Enum):
  DEFAULT = 0
  STRING = 1
  NUMBER = 2
  IDENT = 3
  LABEL = 4
  COMMENT = 5
  SLASH_COMMENT = 6
  MULTILINE_COMMENT = 7 
  QUIT = 8
