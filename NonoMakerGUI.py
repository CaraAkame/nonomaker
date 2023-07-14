import PySimpleGUI as sg
import sys
import os
import os.path
import NonogramClueGeneratorV1 as nono
import solver_from_github as solver # adjusted from: https://gist.github.com/henniedeharder/d7af7462be3eed96e4a997498d6f9722#file-nonogramsolver-py
'''
Nonogram Maker with GUI
- Select dimensions, size, and max waiting time (as in: how long should the computer try to solve the thing before it declares it as unsolvable)
- Draw to your heart's content!
- You can export either the solution (so clues + canvas), or the blank version (clues + blank canvas) to solve
- Press shift to switch between delete and draw mode
Notes:
- The escape button should let you out of the entire thing if something goes wrong
- The "solvable" display is calculated from a solver code found on github (link above)
- This is my first foray into Python, so some notes are just FYI (but for me)
TO DO:
- the function from the NonogramClueGenerator could be directly incorporated into this file to spare the user from having to download an extra file
- consider making a "hackerview" version that has the black theme with green text and tiles instead of black, etc. for fun
'''
VERSION = 2.0    
BLACK = "1"
WHITE = "0"
                                                                                                            # variable in all caps = CONSTANT
sg.theme('SystemDefaultForReal')                                                                            # Colorscheme from 'https://www.pysimplegui.org/en/latest/#themes-automatic-coloring-of-your-windows'

def draw_clue_field():
    c_x,c_y = nono.gen_clues(array)
    c_l=window["canvas_left"]
    c_l.erase()
    for y in range(len(c_x)):
        c_l.draw_rectangle(
        top_left=(0,y),
        bottom_right=(8,y+1),
        fill_color = "#bbbbbb" if y%2 == 0 else "#cccccc")
    c_l.draw_line((0,0),(0,y+1),width=5)                                                                    # field is cut off on the left for some reason, this is a "fix"
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

def make_screenshot():
    window["solvable"].update(visible=False)
    window["shift_toggle"].update(visible=False)
    filename = sg.PopupGetText("Filename:", default_text=f"{values['name']}.pdf", font=("Calibri",10))
    if filename is None:
        pass
    else:
        foldername = sg.PopupGetFolder("Choose Folder:", font=("Calibri",10))
        if foldername is None:
            pass
        try:
            window.save_window_screenshot_to_disk(filename)
            sg.PopupOK(f"File saved as {filename} in folder {foldername}", font=("Calibri",10))
        except TypeError:
            pass
    window["shift_toggle"].update(visible=True)
    window.finalize()

def invert_fun():
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

def solvable_fun():
    c_x,c_y = nono.gen_clues(array)
    mysolver = solver.NonogramSolver(c_x,c_y,max_duration=max_waittime)
    if mysolver.solved is True:
        window["solvable"].update('Solvable')
    if mysolver.solved is False:
        window["solvable"].update('(Probably) Not Solvable')
    window["solvable"].update(visible=True)

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
                [sg.Text('Blocksize (in pixel):', font=("Calibri",12),pad=((4,0),(17,0)),size=(18,1)),
                 sg.Slider(range=(15,30), default_value=20, orientation='h', key="slider")],
                [sg.Text('Max Thinking Time:', font=("Calibri",12),pad=((4,0),(17,0)),size=(18,1)),
                 sg.Slider(range=(1,10), default_value=2, orientation='h', key="slidertime")],
                [sg.Button('Ok', key = "ok", font = ("Calibri",10)), 
                 sg.Button('Recenter', key = "recenter", font = ("Calibri",10)),
                 sg.Button('Cancel', key = "cancel", font = ("Calibri",10))]
              ]
    # First Window (Input window)
    window = sg.Window(f'Nono-Maker Input Version {VERSION}', layout1, finalize=True, font=("Calibri",12))  # would like to use use_custom_titlebar=True,titlebar_font=(), but can't figure out how to leave the icons alone
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
            max_waittime = values["slidertime"]
            break
    window.close()
    framelayout = [
        [sg.VPush()],
        [sg.Push(),
         sg.Button('Invert', key = "invert", size=(8,1), font=("Calibri",10),pad=((0,1),(5,1))), 
         sg.Button('Recenter', key = "recenter",size=(8,1), font=("Calibri",10),pad=((5,0),(5,1)))],
        [sg.Push(),
        sg.Button('Print Clues Only', key = "export_pdf",size=(18,1), font=("Calibri",10),pad=((1,0),(5,1)))],
        [sg.Push(),
         sg.Button('Print Solution', key = "export_solution",size=(18,1), font=("Calibri",10),pad=((1,0),(5,1)))],
        [sg.Push(),
         sg.Button('Clear', key = "reset_canvas",size=(8,1), font=("Calibri",10),pad=((0,1),(5,1))),
         sg.Button('Restart', key = "restart",size=(8,1), font=("Calibri",10),pad=((5,0),(5,1)))],
        [sg.Push(),
         sg.Button('Done', key = "gen_clues",size=(8,1), font=("Calibri",10),pad=((0,1),(5,1))),
         sg.Button('Exit', key = "close",size=(8,1), font=("Calibri",10),pad=((5,0),(5,1)))],                                 
]
    # Second (main) GUI layout
    layout2 = [
                [sg.Frame("",[[sg.Text(f'(Probably) Not Solvable', font=("Calibri",12),key="solvable",visible=False)]],size=(170,30),border_width=0),
                 sg.Push(),
                 sg.Input('Nono',font=("Calibri",12,"bold"),key=("name"),size=(20,1)),
                 sg.Push(),
                 sg.Frame("",[[sg.Text(f'Drawing Mode (Shift)',font=("Calibri",12), key="shift_toggle",visible=True)]],size=(170,30),border_width=0)],
                [sg.Push(),
                 sg.Frame("",framelayout,size =(8*blocksize,8*blocksize),border_width=0,pad=((1,3),(0,0))),
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
                        key = "canvas", drag_submits=True, enable_events=True), 
                 sg.Push()],                                                                                
              ]
    # Canvas Window --> I want to add the rest of the elements as well (canvas top and left)
    window = sg.Window(f'Nono-Maker Paint Version {VERSION} Dimensions: {width}x{height}', layout2, return_keyboard_events = True, finalize=True)
    # background grid (every second cell)
    c = window["canvas"]
    n = 0
    c.draw_rectangle(top_left=(-1,-1),bottom_right=(width+1,height+1),fill_color="#666666",line_width=0)
    c.draw_rectangle(top_left=(-0.7,-0.7),bottom_right=(width+0.7,height+0.7),fill_color=None,line_color="#F2F2F2",line_width=13) # field is asymmetrical for some reason, this is a workaround
    for y in range(0,height):
        for x in range(0,width):
            if n%2 == 0:                                                                                    # if rest of division by 2 = 0 (even number)
                color = "#cccccc"
            else:
                color = "#bbbbbb"
            c.draw_rectangle(top_left=(x,y),bottom_right=(x+1,y+1), fill_color=color)
            n += 1
        if width%2 == 0:
            n += 1
    array = [[0 for i in range(width)] for j in range(height)]                                              # i, j are elements
    figures = {}
    draw_clue_field()                                                                                       # key: "y_x", value: figure number
    shift = False   # "Shift_L:16"
    
    while True:
        event, values = window.read()
        if event in (sg.WIN_CLOSED,"close"):
            sys.exit()
        if event.startswith("Esc"):
            sys.exit()
        if event == "submit":
            continue
        if event == "recenter":
            window.move_to_center()
        if event == "restart":
            break
        if event == "canvas":                                                                               # canvas was clicked on
            x,y = values["canvas"]
            window["solvable"].update(visible=False)
            if shift:
                # delete squares
                if array[y][x] == 0:
                    continue
                if f"{y}_{x}" in figures:
                    fig_num = figures[f"{y}_{x}"]
                    c.delete_figure(fig_num)  
                array[y][x] = 0
            else:
                # paint squares
                try:
                    if array[y][x] == 1:
                        continue
                except IndexError:
                    continue
                if (y<0) or (x<0):
                    continue
                figures[f"{y}_{x}"] = c.draw_rectangle(top_left=(x,y),bottom_right=(x+1,y+1), fill_color="#000000")
                array[y][x] = 1
        if event == "invert":
            window["solvable"].update(visible=False)
            invert_fun()
            gen_clues_fun() 
            solvable_fun()
        if event == "export_solution":
            invert_fun()
            gen_clues_fun()
            invert_fun()
            gen_clues_fun() 
            make_screenshot()
        if event == "gen_clues":
            gen_clues_fun()
            solvable_fun()
        if event == "reset_canvas":
            window["solvable"].update(visible=False)
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
            make_screenshot()
        if event.startswith("Shift"):
            if shift is True:
                shift = False
                window["shift_toggle"].update('Drawing Mode (Shift)')
            else:
                shift = True
                window["shift_toggle"].update('Delete Mode (Shift)')
    window.close()
