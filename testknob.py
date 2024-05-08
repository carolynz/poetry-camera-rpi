from gpiozero import *

switch1 = Button(17)
switch2 = Button(27)
switch3 = Button(22)
switch4 = Button(5)
switch5 = Button(6)
switch6 = Button(13)
switch7 = Button(19)
switch8 = Button(25)
switch9 = Button(24)
switch10 = Button(23)

while True:
  if switch1.is_pressed:
    print("switch 1 is selected")

  elif switch2.is_pressed:
    print("switch 2 is selected")

  elif switch3.is_pressed:
    print("switch 3 is selected")

  elif switch4.is_pressed:
    print("switch 4 is selected")

  elif switch5.is_pressed:
    print("switch 5 is selected")

  elif switch6.is_pressed:
    print("switch 6 is selected")

  elif switch7.is_pressed:
    print("switch 7 is selected")

  elif switch8.is_pressed:
    print("switch 8 is selected")

  elif switch9.is_pressed:
    print("switch 9 is selected")

  elif switch10.is_pressed:
    print("switch 10 is selected")

  else:
    print("switch 3 is selected") #mechanical issue on switch 3
