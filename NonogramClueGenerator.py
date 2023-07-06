"""
Nonogramm Clue Creator
(https://www.conceptispuzzles.com/index.aspx?uri=puzzle/pic-a-pix)
Nonogramm aus .txt file oder von Programm lesen
warn if more than 2 char types
Calculate horizontal clues
Calculate vertical clues
For use in GUI
"""

import os
import os.path

allowedfileextensions = [".txt",".csv",".log",".ini",".nono"]

logfilename = "output.csv"
loglist = ["Filename,Width,Height,\n"]

startdir = os.getcwd()                                  # find current working directory

c_y_sep = "*"                                           # separation char for y clues
c_x_sep = "*"

# function paint
def paintnono(array,c_x,c_y,black="#",white=" "):
    print("+"+len(array[0])*"-"+"+")
    for y,row in enumerate(array):                      # enumerate = gibt jedem Element(row) in einer Liste einen Index (y)
        print("|", end="")
        for number in row:
            if number == 0:
                print(white, end="")
            else:
                print(black, end="")    
        # finish with row
        print("| ", end="")
        print(str(c_x[y]).replace(", ",c_x_sep))           # show calc values
    print("+"+len(array[0])*"-"+"+")
    # find longest result array (mehrstellige Zahlen!) in c_y
    max_y = 0
    for row in c_y:
        y = 0
        for number in row:
            y += len(str(number))
            y += 1
        if y > max_y:
            max_y = y
    t_c_y = []                                            # gestürzte c_y (transformed c_y)
    for y in range (max_y):
        row = []
        for x in range (len(array[0])):
            row.append(" ")
        t_c_y.append(row)
    
    # paint y clues
    for x,row in enumerate(c_y):
        y = 0
        for number in row:
            if y != 0:
                # seperation char
                t_c_y[y][x] = c_y_sep
                y += 1
            for digit in str(number).strip():                    # digit = Stelle
                t_c_y[y][x] = digit
                y += 1            

    # print t_c_y with leading space
    for line in t_c_y:
        print(" "+"".join(line))

# function file to array
def file_to_array(filename):
    # read file
    with open(filename) as f:                           # if indented block ends, file is automatically closed
        lines = f.readlines()

    # cleanup excess (linebreaks)
    cleanlines = [list(line.strip()) for line in lines] # .strip nur für string!
    return cleanlines

# function generate clues
def gen_clues(cleanlines):

    array = []
    c_x = []                                            # clues for rows in array
    c_y = []                                            # clues for columns in array
    charlist = []

    # replace with 0 & 1
    for line in cleanlines:
        rowa = []
        for char in line:
            # append only new chars in list (like set)
            if char not in charlist:
                charlist.append(char)
                # alert for more than 2 chars
                if len(charlist) > 2:
                    return None    
    
    # only 2 chars in charlist = True
    if charlist[0] in (" ",".","0","-","_","'","~",0):
        # WHITE = charlist[0]
        # BLACK = charlist[1]
        if len(charlist) == 1:
            WHITE = charlist[0]
            BLACK = None
        else:
            WHITE,BLACK = charlist                  # same as above but better
    else:
        if len(charlist) == 1:
            BLACK = charlist[0]
            WHITE = None
        else:
            BLACK,WHITE = charlist
    for line in cleanlines:
        rowa = []
        for char in line:
            if char == WHITE:
                rowa.append(0)
            elif char == BLACK:
                rowa.append(1)
        array.append(rowa)
    
    # nono dimensions
    y = len(cleanlines)
    x = len(cleanlines[0])   
    
    # calculating rows                              
    for row in array:
        filled = False                          
        result = []
        blocks = 0                                      # Länge des vektors wenn filled = True --> reset values for new row
        for number in row:                              # for each element (number) in the row
            if number == 0:
                filled = False
            else:
                filled = True
            if filled :
                blocks = blocks +1                      # =blocks += 1  
            elif blocks != 0:
                result.append(blocks)                   # append blocks to the end of result (insert would be opposite)
                blocks = 0                              # reset blocks variable
        # finish with row
        result.append(blocks)                           # append even if it ends with "filled"
        # we don't accept trailing 0s in c_x, but we accept lone 0s
        if len(result) > 1:
            if result[-1] == 0:
                result = result[:-1]
        c_x.append(result)                              # new horizontal clues at the end
    
    #calculating columns
    for x in range(len(array[0])):                      # len = length of array
        filled = False
        result = []
        blocks = 0
        for y in range(len(array)):                     # len(array) = stopp wert hier
            number = array[y][x]                        # Wollen die Zeile zuerst wissen, dann position
            if number == 0:
                filled = False
            else:
                filled = True
            if filled :
                blocks = blocks +1              
            elif blocks != 0:
                result.append(blocks)                   # append blocks to the end of result
                blocks = 0
        # finish with column
        result.append(blocks)
        # we don't accept trailing 0s in c_<, but we accept lone 0s
        if len(result) > 1:
            if result[-1] == 0:
                result = result[:-1]
        c_y.append(result)
    return c_x,c_y

def main():
    # https://docs.python.org/3/library/os.html?highlight=os%20walk#os.walk
    for root, dirs, files in os.walk(startdir):             # "." = current dir ("C:\" wäre dann die ganze C Festplatte)
        for filename in files:
            validfilename = False
            for extension in allowedfileextensions:
                if filename.endswith(extension):
                    validfilename = True
                    break
            if validfilename:                               # = if validfilename == True
                cleanlines = file_to_array(os.path.join(root,filename)) # glues dir name to filename
                if gen_clues(cleanlines) is None:
                    continue                        

# iterations, body
if __name__ == "__main__":                                  # nur machen wenn aufgerufen wird
    main()