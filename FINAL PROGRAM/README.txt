BINARY PUZZLE PROGRAM


DESCRIPTION: 
This program is an interactive piece of software that can load binary puzzles from text files into an interface for the user to solve them. It also includes AI that can solve any binary puzzle that it is given.


HOW TO USE/RUN THE SOFTWARE:
1. Ensure you have installed python v3.10 + (https://www.python.org/downloads/)
2. Install the module Pygame (https://www.pygame.org/download.shtml)
3. Open the main.py file and run the program

*Ensure that the folder structure remains the same.

- Binary puzzles can be created and added to the puzzles folder.
- To load a binary puzzle change the path at the top of the file on line 30.


CONTROLS:
[LMB] Click the squares on the puzzle to cycle its value (*Squares with grey background cannot be changed as they are the initial squares of the puzzle)

[RMB] Click to set a square back to empty

[S] / [LMB] Click the solve button to watch the AI solve the puzzle live

[R] / [LMB] Click the restart button to reset the puzzle


HOW TO SOLVE BINARY PUZZLES:
Binary puzzles have three simple rules

1. Each cell should contain a zero or a one. 
2. No more than two similar numbers below or next to each other are allowed. 
3. Each row and each column is unique and contains as many zeros as ones.

Enjoy :)
