#!/usr/bin/env python3

import re



def is_valid_id(str):

  regex = "^[a-f0-9]{4}$"
  p = re.compile(regex)

  str=str.lower()

  if(str == None):
      return False

  if(re.search(p, str)):
      return True
  else:
      return False



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
