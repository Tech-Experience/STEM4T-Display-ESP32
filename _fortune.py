import random

fortunes = [
'first fortune',
'second fortune is longer',
'third fortune is a charm'
]

# method 2:  no funny counting!
fortune = random.choice(fortunes)
print( fortune )


try: TD.clear()
except:
    print ('T-Display not available')
else:
    TD.typeset("Your fortune:\n%s" % fortune, font=tft_typeset.font2)
    