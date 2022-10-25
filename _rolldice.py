import random, utime

def rolldice(numsides):
  val=random.randint(1,numsides)
  return(val)

roll=rolldice(6)
print("Rolled: %d" % roll)

TD.clear()
TD.typeset("Rolled: %d" % roll, 2, 2, font=tft_typeset.font2)
