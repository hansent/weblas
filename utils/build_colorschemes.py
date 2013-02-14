from PIL import Image


def create_color_scheme(colors):
    img = Image.new("RGBA", (8,8))
    for x in range(8):
        for y in range(8):
            val = tuple(map(int, colors[x]))
            img.im.putpixel((x,y), val)
    return img


schema_type = "SCHEMA TYPE"
fin = open("colorbrewer.csv", "r")
header = fin.readline()
while True:
    #read a line
    line = fin.readline()
    if not line:
        break

    #split into tokens,  ignore last or bad lines
    tokens = line.split(',')
    if len(tokens) < 10:
        continue

    #schema type changed
    if len(tokens[9]) > 1:
        schema_type = tokens[9].lower()[:3]

    #if this is the begining of a scheme, lets parse it
    name = tokens[0]
    num_colors = tokens[1]
    if name and num_colors == "8":
        colors = []
        colors.append(tokens[6:9])
        #parse colors form next 7 lines
        for i in range(7):
            color_line = fin.readline()
            colors.append(color_line.split(',')[6:9])
        img = create_color_scheme(colors)
        img.save("{0}_{1}.png".format(schema_type, name))




