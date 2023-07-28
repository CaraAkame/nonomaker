import PySimpleGUI as sg
import sys
import time
from itertools import combinations
import numpy as np 
'''
Nonogram Maker with GUI
- Select dimensions, size, and max waiting time (as in: how long should the computer try to solve the thing before it declares it as unsolvable)
- Draw to your heart's content!
- You can export either the solution (so clues + canvas), or the blank version (clues + blank canvas) to solve
- Press shift to switch between delete and draw mode
Notes:
- The escape button should let you out of the entire thing if something goes wrong
- The "solvable" display is calculated from an adapted solver code found on github (https://gist.github.com/henniedeharder/d7af7462be3eed96e4a997498d6f9722#file-nonogramsolver-py)
- This is my first foray into Python, so some notes are just FYI (but for me)
TO DO:
- consider making a "hackerview" version that has the black theme with green text and tiles instead of black, etc. for fun
- maybe make a color version
- web version
'''
VERSION = 4    
BLACK = "1"
WHITE = "0"
                                                                                                            # variable in all caps = CONSTANT
sg.theme('SystemDefaultForReal')                                                                            # Colorscheme from 'https://www.pysimplegui.org/en/latest/#themes-automatic-coloring-of-your-windows'

def create_window_main():
    framelayout = [
                [sg.Input('Nono',key="name",font=("Calibri",12,"bold"),size=(20,1),enable_events=True)],
                [sg.Button('Reset Options Menu',key="buttons",font=("Calibri",10))],
                [sg.Text(f'Drawing Mode (Shift)',font=("Calibri",12), key="shift_toggle",visible=True)],
                [sg.Text(f'(Probably) Not Solvable', font=("Calibri",12),key="solvable",visible=False)],
                ]
    # Second (main) GUI layout
    layout2 = [
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
    return sg.Window(f'Nono-Maker Paint Version {VERSION} Dimensions: {width}x{height}', layout2, return_keyboard_events = True, keep_on_top=True, finalize=True)

def create_window_buttons():
    iconsize=(4*blocksize,4*blocksize)
    # original icon = ca 1024x1024 --> we want it to be 2xblocksize; shrink factor should be 1024/(2xblocksize)
    stringquotient=int(1024/(4*blocksize))
    layout3 = [
        [sg.VPush()],
        [sg.Push(),
        sg.Button('', key = "invert", size=(4,2), font=("Calibri",10),pad=((1,1),(1,1)),tooltip="Invert",image_filename="IconInvert.png",image_subsample=stringquotient,image_size=iconsize),
        sg.Button('', key = "recenter",size=(4,2), font=("Calibri",10),pad=((1,1),(1,1)),tooltip="Recenter",image_filename="IconRecenter.png",image_subsample=stringquotient,image_size=iconsize),
        sg.Push()],
        [sg.Push(),
        sg.Button('', key = "reset_canvas",size=(4,2), font=("Calibri",10),pad=((1,1),(1,1)),tooltip="Reset Canvas",image_filename="IconClear.png",image_subsample=stringquotient,image_size=iconsize),
        sg.Button('', key = "gen_clues",size=(4,2), font=("Calibri",10),pad=((1,1),(1,1)),tooltip="Generate Clues",image_filename="IconGenClues.png",image_subsample=stringquotient,image_size=iconsize),
        sg.Push()],
        [sg.Push(),
        sg.Button('', key = "export_pdf",size=(4,2), font=("Calibri",10),pad=((1,1),(1,1)),tooltip="Export(Clues with Blank Canvas)",image_filename="IconExportBlank.png",image_subsample=stringquotient,image_size=iconsize),
        sg.Button('', key = "export_solution",size=(4,2), font=("Calibri",10),pad=((1,1),(1,1)),tooltip="Export(Clues with Solution)",image_filename="IconExportSolution.png",image_subsample=stringquotient,image_size=iconsize),
        sg.Push()],
        [sg.Push(),
         sg.Button('', key = "restart",size=(4,2), font=("Calibri",10),pad=((1,1),(1,1)),tooltip="Restart",image_filename="IconRestart.png",image_subsample=stringquotient,image_size=iconsize),
         sg.Button('', key = "close",size=(4,2), font=("Calibri",10),pad=((1,1),(1,1)),tooltip="Exit",image_filename="IconExit.png",image_subsample=stringquotient,image_size=iconsize),
         sg.Push()],
        [sg.Button('Help', key="explain", font=("Calibri",10),tooltip="Button Guide")],
        [sg.VPush()],                                 
                    ]
    return sg.Window(f'Menu', layout3, return_keyboard_events = True, keep_on_top=True, finalize=True)

def draw_clue_field():
    c_x,c_y = gen_clues(array)
    c_l=window_main["canvas_left"]
    c_l.erase()
    for y in range(len(c_x)):
        c_l.draw_rectangle(
        top_left=(0,y),
        bottom_right=(8,y+1),
        fill_color = "#bbbbbb" if y%2 == 0 else "#cccccc")
    c_l.draw_line((0,0),(0,y+1),width=5)                                                                    # field is cut off on the left for some reason, this is a "fix"
    c_t=window_main["canvas_top"]
    c_t.erase()
    for x in range(len(c_y)):
        c_t.draw_rectangle(
        top_left=(x,0),
        bottom_right=(x+1,8),
        fill_color = "#bbbbbb" if x%2 == 0 else "#cccccc")

def gen_clues(cleanlines):

    array = []
    c_x = []                                                                                                # clues for rows in array
    c_y = []                                                                                                # clues for columns in array
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
            WHITE,BLACK = charlist                                                                          # same as above but better
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
        blocks = 0                                                                                          # length of vactor when filled = True --> reset values for new row
        for number in row:                                                                                  # = for each element (number) in the row
            if number == 0:
                filled = False
            else:
                filled = True
            if filled :
                blocks = blocks +1                                                                          # = blocks += 1  
            elif blocks != 0:
                result.append(blocks)                                                                       # append blocks to the end of result (insert would be opposite)
                blocks = 0                                                                                  # reset blocks variable
        # finish with row
        result.append(blocks)                                                                               # append even if it ends with "filled"
        # we don't accept trailing 0s in c_x, but we accept lone 0s
        if len(result) > 1:
            if result[-1] == 0:
                result = result[:-1]
        c_x.append(result)                                                                                  # new horizontal clues at the end
    
    #calculating columns
    for x in range(len(array[0])):                                                                          # len = length of array
        filled = False
        result = []
        blocks = 0
        for y in range(len(array)):                                                                         # len(array) = stop value here
            number = array[y][x]                                                                            # we want the row first, then the position
            if number == 0:
                filled = False
            else:
                filled = True
            if filled :
                blocks = blocks +1              
            elif blocks != 0:
                result.append(blocks)                                                                       # append blocks to the end of result
                blocks = 0
        # finish with column
        result.append(blocks)
        # we don't accept trailing 0s in c_<, but we accept lone 0s
        if len(result) > 1:
            if result[-1] == 0:
                result = result[:-1]
        c_y.append(result)
    return c_x,c_y

def gen_clues_fun():
    c_x,c_y = gen_clues(array)
    c_l=window_main["canvas_left"]
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
    c_t=window_main["canvas_top"]
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
    window_main["solvable"].update(visible=False)
    window_main["shift_toggle"].update(visible=False)
    filename = sg.PopupGetText("Filename:", default_text=f"{Game.name}.pdf", font=("Calibri",10),keep_on_top=True)
    if filename is None:
        pass
    else:
        foldername = sg.PopupGetFolder("Choose Folder:", font=("Calibri",10),keep_on_top=True)
        if foldername is None:
            pass
        try:
            window_main.save_window_screenshot_to_disk(filename)
            sg.PopupOK(f"File saved as {filename} in folder {foldername}", font=("Calibri",10),keep_on_top=True)
        except TypeError:
            pass
    window_main["shift_toggle"].update(visible=True)
    window_main.finalize()

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
    c_x,c_y = gen_clues(array)
    mysolver = NonogramSolver(c_x,c_y,max_duration=max_waittime)
    if mysolver.solved is True:
        window_main["solvable"].update('Solvable')
    if mysolver.solved is False:
        window_main["solvable"].update('(Probably) Not Solvable')
    window_main["solvable"].update(visible=True)

class Game:
    name = "Nono"

class NonogramSolver:
    def __init__(self, 
                 ROWS_VALUES=[[2], [4], [6], [4, 3], [5, 4], [2, 3, 2], [3, 5], [5], [3], [2], [2], [6]], 
                 COLS_VALUES=[[3], [5], [3, 2, 1], [5, 1, 1], [12], [3, 7], [4, 1, 1, 1], [3, 1, 1], [4], [2]], 
                 savepath='',
                 max_duration=3):
        self.start = time.time()
        self.max_duration = max_duration
        self.ROWS_VALUES = ROWS_VALUES
        self.no_of_rows = len(ROWS_VALUES)
        self.rows_changed = [0] * self.no_of_rows
        self.rows_done = [0] * self.no_of_rows

        self.COLS_VALUES = COLS_VALUES
        self.no_of_cols = len(COLS_VALUES)
        self.cols_changed = [0] * self.no_of_cols
        self.cols_done = [0] * self.no_of_cols

        self.solved = False 
        self.shape = (self.no_of_rows, self.no_of_cols)
        self.board = [[0 for c in range(self.no_of_cols)] for r in range(self.no_of_rows)]
        self.savepath = savepath
        if self.savepath != '': self.n = 0

        # step 1: Defining all possible solutions for every row and col
        self.rows_possibilities = self.create_possibilities(ROWS_VALUES, self.no_of_cols)
        self.cols_possibilities = self.create_possibilities(COLS_VALUES, self.no_of_rows)
        
        while not self.solved:
            # step 2: Order indici by lowest 
            self.lowest_rows = self.select_index_not_done(self.rows_possibilities, 1)
            self.lowest_cols = self.select_index_not_done(self.cols_possibilities, 0)
            self.lowest = sorted(self.lowest_rows + self.lowest_cols, key=lambda element: element[1])

            # step 3: Get only zeroes or only ones of lowest possibility 
            for ind1, _, row_ind in self.lowest:
                if not self.check_done(row_ind, ind1):
                    if row_ind: values = self.rows_possibilities[ind1]
                    else: values = self.cols_possibilities[ind1]
                    if time.time() - self.start > self.max_duration:
                        return
                    same_ind = self.get_only_one_option(values)
                    for ind2, val in same_ind:
                        if row_ind: ri, ci = ind1, ind2
                        else: ri, ci = ind2, ind1 
                        if self.board[ri][ci] == 0:
                            self.board[ri][ci] = val
                            if row_ind: self.cols_possibilities[ci] = self.remove_possibilities(self.cols_possibilities[ci], ri, val)
                            else: self.rows_possibilities[ri] = self.remove_possibilities(self.rows_possibilities[ri], ci, val)

                    self.update_done(row_ind, ind1)
            self.check_solved()
       
    def create_possibilities(self, values, no_of_other):
        possibilities = []
        
        for v in values:
            groups = len(v)
            no_empty = no_of_other-sum(v)-groups+1
            ones = [[1]*x for x in v]
            res = self._create_possibilities(no_empty, groups, ones)
            possibilities.append(res)  
        
        return possibilities

    def _create_possibilities(self, n_empty, groups, ones):
        res_opts = []
        for p in combinations(range(groups+n_empty), groups):
            selected = [-1]*(groups+n_empty)
            ones_idx = 0
            for val in p:
                selected[val] = ones_idx
                ones_idx += 1
            res_opt = [ones[val]+[-1] if val > -1 else [-1] for val in selected]
            res_opt = [item for sublist in res_opt for item in sublist][:-1]
            res_opts.append(res_opt)
        return res_opts

    def select_index_not_done(self, possibilities, row_ind):
        s = [len(i) for i in possibilities]
        if row_ind:
            return [(i, n, row_ind) for i, n in enumerate(s) if self.rows_done[i] == 0]
        else:
            return [(i, n, row_ind) for i, n in enumerate(s) if self.cols_done[i] == 0]

    def get_only_one_option(self, values):
        return [(n, np.unique(i)[0]) for n, i in enumerate(np.array(values).T) if len(np.unique(i)) == 1]

    def remove_possibilities(self, possibilities, i, val):
        return [p for p in possibilities if p[i] == val]

    def update_done(self, row_ind, idx):
        if row_ind: vals = self.board[idx]
        else: vals = [row[idx] for row in self.board]
        if 0 not in vals:
            if row_ind: self.rows_done[idx] = 1
            else: self.cols_done[idx] = 1 

    def check_done(self, row_ind, idx):
        if row_ind: return self.rows_done[idx]
        else: return self.cols_done[idx]

    def check_solved(self):
        if 0 not in self.rows_done and 0 not in self.cols_done:
            self.solved = True

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
    
    # Canvas Window --> I want to add the rest of the elements as well (canvas top and left)
    window_main, window_buttons = create_window_main(), create_window_buttons()
    window_main_width=window_main.current_size_accurate()[0]
    window_main.finalize()
    window_buttons.move(window_main.current_location()[0]+window_main_width+5,window_main.current_location()[1])
    
    # background grid (every second cell)
    c = window_main["canvas"]
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
        window, event, values = sg.read_all_windows()
        if event == sg.WIN_CLOSED:
            if window == window_buttons:       
                window_buttons.close()
                window_main.move_to_center()
                window_buttons = None
            elif window == window_main:     
                if window_buttons is not None:
                    window_buttons.close()
                window_main.close()
        elif event == "close":
            sys.exit()
        elif event.startswith("Esc"):
            sys.exit()
        elif event == "buttons":
            if window_buttons is None:
                window_buttons=create_window_buttons()
                window_buttons.move(window_main.current_location()[0]+window_main_width+5,window_main.current_location()[1])
            else:
                window_buttons.move(window_main.current_location()[0]+window_main_width+5,window_main.current_location()[1])
            print(values)
        elif event == "name":
            Game.name=values["name"]
        elif event == "submit":
            continue
        elif event == "recenter":
            window_main.move_to_center()
            window_main.finalize()
            # move button window to its starting position as well
            window_buttons.move(window_main.current_location()[0]+window_main_width+5,window_main.current_location()[1])
        elif event == "restart":
            break
        elif event == "canvas":                                                                             # canvas was clicked on
            x,y = values["canvas"]
            window_main["solvable"].update(visible=False)
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
        elif event == "invert":
            window_main["solvable"].update(visible=False)
            invert_fun()
            gen_clues_fun() 
            solvable_fun()
        elif event == "export_solution":
            invert_fun()
            gen_clues_fun()
            invert_fun()
            gen_clues_fun() 
            make_screenshot()
        elif event == "gen_clues":
            gen_clues_fun()
            solvable_fun()
        elif event == "reset_canvas":
            window_main["solvable"].update(visible=False)
            for fig_key in figures:
                c.delete_figure(figures[fig_key])
                for y,row in enumerate(array):
                    for x,col in enumerate(row):
                        if array[y][x] == 1:
                            array[y][x] = 0
                        elif array[y][x] == 0:
                            array[y][x] = 0
            gen_clues_fun()
        elif event == "export_pdf":
            for fig_key in figures:
                c.delete_figure(figures[fig_key])
            # and then export
            make_screenshot()
        elif event == "explain":
            sg.PopupOK(image="Icons.png",keep_on_top=True)      
        elif event.startswith("Shift"):
            if shift is True:
                shift = False
                window_main["shift_toggle"].update('Drawing Mode (Shift)')
            else:
                shift = True
                window_main["shift_toggle"].update('Delete Mode (Shift)')
    window.close()
