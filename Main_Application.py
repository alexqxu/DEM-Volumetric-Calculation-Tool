from GUI import GUI
# import os
# import sys

"""
This is the main class of the program.
@Author: Alex Xu
"""

# os.environ['PROJ_LIB'] = os.path.dirname(sys.argv[0]) # Solving PyInstaller Issue (from hook.py file)

# Start the GUI/Application
myGUI = GUI()
print("Launching GUI")
myGUI.run()
