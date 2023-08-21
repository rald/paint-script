class Token:
  def __init__(self,line,column,type,value):
    self.type=type
    self.value=value
    self.line=line
    self.column=column

  def __str__(self):
    return f'{{ line: {self.line}, column: {self.column}, type: {self.type}, value: {self.value} }}'

  def __repr__():
    return this.__str__()
