import PySimpleGUI as sg
import sys
import os
import os.path
import NonogramClueGenerator as nono
'''
split into two GUIs (instead of update window)
TO DO:
- Mouse Drag events
- Refactoring functions
- export pdf with solution
- display if solvable
- right click for flag as 0
- adjust frame of canvas (it's uneven)
'''
VERSION = 1.4    
BLACK = "1"
WHITE = "0"
                                                                                                            # variable in all caps = CONSTANT
sg.theme('SystemDefaultForReal')                                                                                           # Colorscheme from 'https://www.pysimplegui.org/en/latest/#themes-automatic-coloring-of-your-windows'

def draw_clue_field():
    c_x,c_y = nono.gen_clues(array)
    c_l=window["canvas_left"]
    c_l.erase()
    for y in range(len(c_x)):
        c_l.draw_rectangle(
        top_left=(0,y),
        bottom_right=(8,y+1),
        fill_color = "#bbbbbb" if y%2 == 0 else "#cccccc")
    c_l.draw_line((0,0),(0,y+1),width=5)                    # field is cut off on the left for some reason, this is a "fix"
    c_t=window["canvas_top"]
    c_t.erase()
    for x in range(len(c_y)):
        c_t.draw_rectangle(
        top_left=(x,0),
        bottom_right=(x+1,8),
        fill_color = "#bbbbbb" if x%2 == 0 else "#cccccc")

def gen_clues_fun():
    c_x,c_y = nono.gen_clues(array)
    c_l=window["canvas_left"]
    c_l.erase()
    for y in range(len(c_x)):
        c_l.draw_rectangle(
            top_left=(0,y),
            bottom_right=(8,y+1),
            fill_color = "#bbbbbb" if y%2 == 0 else "#cccccc"
        )
    c_l.draw_line((0,0),(0,y+1),width=5)
    for y,clue in enumerate(c_x):
        text = f"{clue}"
        text = text.replace(",","  ")
        text = text.replace("[","")
        text = text.replace("]","")
        c_l.draw_text(
            text,
            (7.8,y+0.5),
            "#000000",
            ("Calibri",int(blocksize-5)),
            text_location = sg.TEXT_LOCATION_RIGHT
        )
    c_t=window["canvas_top"]
    c_t.erase()
    for x in range(len(c_y)):
        c_t.draw_rectangle(
            top_left=(x,0),
            bottom_right=(x+1,8),
            fill_color = "#bbbbbb" if x%2 == 0 else "#cccccc"
        )
    for x,clue in enumerate(c_y):
        for y,number in enumerate(clue[::-1]):
            c_t.draw_text(
                str(number),
                (x+0.5,8-y),
                "#000000",
                ("Calibri",int(blocksize-5)),
                text_location = sg.TEXT_LOCATION_BOTTOM
            )
    # solver TO DO
    print(c_x)
    print(c_y)
# First GUI (Input Window) layout
while True:
    layout1 = [ 
                [sg.Text('Welcome to NonoPaint!', font = ("Calibri",22,"bold"))],
                [sg.Text('Please enter the parameters:', key = "subhead", font=("Calibri",16,"italic")),
                 sg.Text('Dimensions:', key = "dims", font = ("Calibri", 16), visible = False),
                 sg.Text('Width', key = "wlabel", font = ("Calibri",16)), 
                 sg.InputText(default_text = "20", key = "width", size = (5,1), font = ("Calibri",16)),
                 sg.Text('Height', key = "hlabel", font = ("Calibri",16)), 
                 sg.InputText(default_text = "20", key = "height", size = (5,1), font = ("Calibri",16))],
                [sg.Text('Blocksize (in pixel):', font=("Calibri",12)),
                 sg.Slider(range=(15,30), default_value=20, orientation='h', key="slider")],
                [sg.Button('Ok', key = "ok", font = ("Calibri",10)), 
                 sg.Button('Recenter', key = "recenter", font = ("Calibri",10)),
                 sg.Button('Cancel', key = "cancel", font = ("Calibri",10))]
              ]
    # First Window (Input window)
    window = sg.Window(f'Nono-Maker Input Version {VERSION}', layout1, finalize=True, font=("Calibri",12))  # would like to use use_custom_titlebar=True,titlebar_font=(), but can't figure out houw to leave the icons alone
    # Event Loop to process "events" and get the "values" of the inputs
    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED or event == "cancel":                                                     # if user closes window or clicks cancel
            sys.exit()                                                                                      # exit the entire process (break would just exit the loop itself)
        if event == "recenter":                                                                             # if window is dragged off center, it can be recentered on the screen
            window.move_to_center()
        if event == "ok":                                                                                   # pressing the OK button tests if there is a value in the fields
            width = values["width"]
            height = values["height"]
            if len(width) == 0:
                sg.PopupError("Please enter a width value!", font=("Calibri",10))
                continue
            if len(height) == 0:
                sg.PopupError("Please enter a height value!", font=("Calibri",10))
                continue
            # "try" if the value is a usable integer and spits out an error popup if it isn't
            try:
                width = int(width)
            except:
                sg.PopupError("Please enter a (whole) numerical value for width!", font=("Calibri",10))
                continue
            try:
                height = int(height)
            except:
                sg.PopupError("Please enter a (whole) numerical value for height!", font=("Calibri",10))
                continue
            # <0?
            if (width <= 0) or (height <= 0):
                sg.PopupError("Please only enter positive values!", font=("Calibri",10))
                continue
            # OK - If all values are usable, break to the next loop (close this window and open the next one)
            blocksize = values["slider"]                                                                    # "save" values from slider into variable
            break
    window.close()
    framelayout = [
        [sg.VPush()],
        [sg.Push(),
         sg.Button('Invert', key = "invert", size=(6,1), font=("Calibri",10)), 
         sg.Button('Recenter', key = "recenter",size=(8,1), font=("Calibri",10))],
        [sg.Push(),
         sg.Button('Print', key = "export_pdf",size=(6,1), font=("Calibri",10)),
         sg.Button('Export', key = "export_txt",size=(8,1), font=("Calibri",10))                           # make a "print with solution" button instead
         ],
        [sg.Push(),
         sg.Button('Clear', key = "reset_canvas",size=(6,1), font=("Calibri",10)),
         sg.Button('Restart', key = "restart",size=(8,1), font=("Calibri",10))],
        [sg.Push(),
         sg.Button('Done', key = "gen_clues",size=(6,1), font=("Calibri",10)),
         sg.Button('Exit', key = "close",size=(8,1), font=("Calibri",10))],                                 # or make screenshot
]
    # Second (main) GUI layout
    layout2 = [
                [sg.Text(f'Selected Dimensions: {width} x {height}', font=("Calibri",14,"bold"))],
                [sg.Push(),
                 sg.Frame("",framelayout,size =(8*blocksize,8*blocksize),border_width=0),
                 sg.Graph(canvas_size=((width+2)*blocksize, 8*blocksize), 
                        graph_bottom_left=(-0.5,8), graph_top_right=(width+0.5,-0.5), 
                        key = "canvas_top"),
                 sg.Push()],
                [sg.Push(),
                 sg.Graph(canvas_size=(8*blocksize,(height+2)*blocksize),
                          graph_bottom_left=(0,height+0.5), graph_top_right=(8,-0.5),
                          key = "canvas_left", pad =((0,0),(0,0))),
                 sg.Graph(canvas_size=((width+2)*blocksize, (height+2)*blocksize), 
                        graph_bottom_left=(-0.5,height+0.5), graph_top_right=(width+0.5,-0.5), 
                        key = "canvas", enable_events=True), 
                 sg.Push()],                                                                                # drag_submits=True --> too hard rn
              ]
    # Canvas Window --> I want to add the rest of the elements as well (canvas top and left)
    window = sg.Window(f'Nono-Maker Paint Version {VERSION}', layout2, finalize=True)
    # background grid (every second cell)
    c = window["canvas"]
    n = 0
    c.draw_rectangle(top_left=(-1,-1),bottom_right=(width+1,height+1),fill_color="#666666",line_width=0)
    for y in range(0,height):
        for x in range(0,width):
            if n%2 == 0:                                                                                    # if rest einer division durch 2 = 0 (also gerade)
                color = "#cccccc"
            else:
                color = "#bbbbbb"
            c.draw_rectangle(top_left=(x,y),bottom_right=(x+1,y+1), fill_color=color)
            n += 1
        if width%2 == 0:
            n += 1
    array = [[0 for i in range(width)] for j in range(height)]                                              # i, j are elements
    figures = {}
    draw_clue_field()                                                                                           # key: "y_x", value: figure number
    while True:
        event, values = window.read()
        if event in (sg.WIN_CLOSED,"close"):
            sys.exit()
        if event == "recenter":
            window.move_to_center()
        if event == "restart":
            break
        if event == "canvas":                                                                               # canvas was clicked on
            x,y = values["canvas"]
            if (x<0) or (y<0):
                continue
            # check array for filled squares
            try:
                click=array[y][x]
            except IndexError:
                continue
            if array[y][x] == 1:
                # check if figure = True for "y_x"
                if f"{y}_{x}" in figures:
                    fig_num = figures[f"{y}_{x}"]
                    c.delete_figure(fig_num)                                                                # delete black square
                # flip array elements
                array[y][x] = 0
            elif array[y][x] == 0:
                figures[f"{y}_{x}"] = c.draw_rectangle(top_left=(x,y),bottom_right=(x+1,y+1), fill_color="#000000")
                array[y][x] = 1
        if event == "invert":
            # flip array
            for y,row in enumerate(array):
                for x,col in enumerate(row):
                    if array[y][x] == 1:
                        array[y][x] = 0
                    elif array[y][x] == 0:
                        array[y][x] = 1
            # delete all old figures
            for fig_key in figures:
                c.delete_figure(figures[fig_key]) 
            for y,row in enumerate(array):
                for x,col in enumerate(row):
                    if array[y][x] == 1:
                        figures[f"{y}_{x}"] = c.draw_rectangle(top_left=(x,y),bottom_right=(x+1,y+1), fill_color="#000000")
            gen_clues_fun() 
        if event == "export_txt":
            black = sg.PopupGetText("Char for Black:", default_text=BLACK, font=("Calibri",10))
            white = sg.PopupGetText("Char for White:", default_text=WHITE, font=("Calibri",10))
            if black is None or white is None:
                continue
            filename = sg.PopupGetText("Filename:", default_text="Nono.txt", font=("Calibri",10))
            if filename is None:
                continue
            foldername = sg.PopupGetFolder("Choose Folder:", font=("Calibri",10))
            if foldername is None:
                continue
            with open (os.path.join(foldername,filename),"w") as myfile:
                for row in array:
                    textline=""
                    for number in row:
                        if number == 1:
                            textline += black
                        elif number == 0:
                            textline += white
                    myfile.write(textline+"\n")
            sg.PopupOK("File Saved", font=("Calibri",10))                   # wie bei pdf anzeigen
        if event == "gen_clues":
            gen_clues_fun()
        if event == "reset_canvas":
            for fig_key in figures:
                c.delete_figure(figures[fig_key])
                for y,row in enumerate(array):
                    for x,col in enumerate(row):
                        if array[y][x] == 1:
                            array[y][x] = 0
                        elif array[y][x] == 0:
                            array[y][x] = 0
            gen_clues_fun()
        if event == "export_pdf":
            for fig_key in figures:
                c.delete_figure(figures[fig_key])
            # and then export
            filename = sg.PopupGetText("Filename:", default_text="Nono.pdf", font=("Calibri",10))
            if filename is None:
                continue
            foldername = sg.PopupGetFolder("Choose Folder:", font=("Calibri",10))
            if foldername is None:
                continue
            window.save_window_screenshot_to_disk(filename)
            sg.PopupOK(f"File saved as {filename} in folder {foldername}", font=("Calibri",10))
            window.finalize()
    window.close()