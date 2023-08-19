class Token:
  def __init__(self,line,column,type,text):
    self.type=type
    self.text=text
    self.line=line
    self.column=column

  def __str__(self):
    return f'{{ line: {self.line}, column: {self.column}, type: {self.type}, text: "{self.text}" }}'

  def __repr__():
    return this.__str__()
