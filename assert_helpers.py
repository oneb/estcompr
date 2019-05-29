def is_good_handle(f):
  return (
      f.readable() 
      and not f.closed 
      and f.seekable())

def is_pos_int(x):
    return isinstance(x, int) and x >= 1
