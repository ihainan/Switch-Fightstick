#!/bin/python

import sys, os, getopt
from PIL import Image

def main(argv):
  opts, args = getopt.getopt(argv, "pshi")
  previewBilevel = False
  saveBilevel = False
  invertColormap = False

  for opt, arg in opts:
    if opt == '-h':
      usage()
      sys.exit()
    elif opt == '-p':
      previewBilevel = True
    elif opt == '-s':
      saveBilevel = True
    elif opt == '-i':
      invertColormap = True

  im = Image.open(args[0])                # import 320x120 png
  if not (im.size[0] == 320 and im.size[1] == 120):
    print("ERROR: Image must be 320px by 120px!")
    sys.exit()

  im = im.convert("1")                    # convert to bilevel image
                                          # dithering if necessary
  if previewBilevel:
    im.show()
  if saveBilevel:
    im.save("bilevel_" + args[0])
    print("Bilevel version of " + args[0] + " saved as bilevel_" + args[0])
  if not (previewBilevel or saveBilevel):
    im_px = im.load()
    data = []
    for i in range(0,120):                # iterate over the columns
      for j in range(0,320):              # and convert 255 vals to 0 to match logic in Joystick.c and invertColormap option
         data.append(0 if im_px[j,i] == 255 else 1)

    edges = []
    for i in range(0, 120):
        sublist = data[i * 320:(i + 1) * 320 ]
        indices = [j for j,x in enumerate(sublist) if x == 1]
        if (len(indices) == 0):
          edges.append(0)
          edges.append(319)
        elif (len(indices) == 1):
          edges.append(indices[0])
          edges.append(indices[0])
        else:
          edges.append(indices[0])
          edges.append(indices[-1])

    str_out = "#include <stdint.h>\n#include <avr/pgmspace.h>\n\nconst uint8_t image_data[0x12c1] PROGMEM = {"
    for i in range(0, (320*120) / 8):
       val = 0;

       for j in range(0, 8):
          val |= data[(i * 8) + j] << j

       if (invertColormap):
          val = ~val & 0xFF;
       else:
          val = val & 0xFF;

       str_out += hex(val) + ", "         # append hexidecimal bytes
                                          # to the output .c array
    str_out += "0x0};\n\n"                # of bytes

    str_out += "const uint32_t edges_data[0xf1] PROGMEM = {"
    for i in range(0, 240):
        str_out += str(edges[i]) + ", "

    str_out += "0x0};\n"

    with open('image.c', 'w') as f:       # save output into image.c
      f.write(str_out)

    if (invertColormap):
       print("{} converted with inverted colormap and saved to image.c".format(args[0]))
    else:
       print("{} converted with original colormap and saved to image.c".format(args[0]))

def usage():
  print("To convert to image.c: png2c.py <yourImage.png>")
  print("To convert to an inverted image.c: png2c.py -i <yourImage.png>")
  print("To preview bilevel image: png2c.py -p <yourImage.png>")
  print("To save bilevel image: png2c.py -s <yourImage.png>")

if __name__ == "__main__":
  if len(sys.argv[1:]) == 0:
    usage()
    sys.exit
  else:
    main(sys.argv[1:])
