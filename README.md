# nonomaker
uses Python and pysimplegui (and some other things specifically for the imported solver) 

GUI to make a nonogram

https://en.wikipedia.org/wiki/Nonogram

can: pick canvas size, blocksize, max waiting time for solving; draw a nonogram, check if it's solvable, and export as either the solution (screenshot below) or the blank version (so the clues with a blank canvas)

edits: all necessary functions are in the main file, no need to download the rest. The "NonoClueGenerator" DOES still work as a standalone (using .txt files for instance), but requires some cleanup - it prints the clues with the nonogram itself in the terminal.

to do: some QoL stuff like other themes and icons for the buttons (uses single letters right now, with a tooltip and help function, still need to draw the icons)

Sample (the new version has a new button layout):

![Screenshot](HelloWorld2.png)
