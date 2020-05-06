import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
import threading
import queue
import re
# from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
# import matplotlib.pyplot as plt
# from mpl_toolkits.mplot3d import Axes3D
# from matplotlib.backend_bases import key_press_handler

from CSV_Writer import CSVWriter
from DEM_Processor import DEMProcessor
from Data_Handler import DataHandler
from GraphProcessor import GraphProcessor

HEIGHT = 700
WIDTH = 700
QUEUE_CHECK_RATE = 100
TITLE = "Volumetric Calculation Tool v0.2"
RESULT = "Results"
TEXT1 = "DEM Files"
TEXT2 = "Clear"
TEXT3 = "Remove"
TEXT4 = "Shape File"
CREDITS = "Created by Alex Xu, Duke University DIGLab"
FILE_SELECT = "Browse..."
EXPORT = "Export"
GRAPH = "Visualize"


class GUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.resizable(False, False)
        self.root.title(TITLE)
        #self.root.iconphoto(False, tk.PhotoImage(file='img/icon.png')) # TODO: Remove
        self.root.iconbitmap('img/icon_3V8_icon.ico')

        # Instance variables for the Calculator Thread
        self.myDEMProcessor = None
        self.calculate_thread = None  # To create a separate thread for calculations
        self.queue = None

        # Instance variables for the Visualizer Thread
        self.queue2 = None
        self.visualize_thread = None
        self.progress_bar2 = None
        self.process_label2 = None

        # Setting up the overall Canvas
        canvas = tk.Canvas(self.root, height=HEIGHT, width=WIDTH)
        canvas.pack()

        # Adding in the title
        label = tk.Label(canvas, text=TITLE, font=('Century', 20), anchor='center')
        label.place(relx=0.15, rely=.02, relwidth=0.7, relheight=0.05)

        # Adding in the DEM Select Frame
        frame1 = tk.Frame(self.root, highlightbackground="gray70", highlightthickness=1)
        frame1.place(relwidth=0.8, relheight=0.35, relx=0.5, rely=0.1, anchor='n')

        # Select DEM Files Label
        label2 = tk.Label(frame1, text=TEXT1, font=('Century', 12), justify=tk.LEFT)
        label2.place(relheight=0.1, relx=0.02)

        # Scrollbar for ListBox
        scrollbar = tk.Scrollbar(frame1, orient=tk.VERTICAL)

        # ListBox used for Selected Files
        fileBox = tk.Listbox(frame1, activestyle="none", yscrollcommand=scrollbar.set)
        scrollbar.config(command=fileBox.yview)
        scrollbar.place(relheight=0.87, relx=0.62, rely=0.1)
        fileBox.place(relwidth=0.6, relheight=0.87, relx=0.02, rely=0.1)

        # Browse... button
        BrowseButton = tk.Button(frame1, text=FILE_SELECT, command=lambda: self.DEM_file_selector(fileBox))
        BrowseButton.place(relx=0.69, rely=.1, relwidth=0.25, relheight=0.13)

        # Clear button
        clearButton = tk.Button(frame1, text=TEXT2, command=lambda: self.clearFileBox(fileBox))
        clearButton.place(relx=0.69, rely=.28, relwidth=0.25, relheight=0.13)

        # Remove button
        removeButton = tk.Button(frame1, text=TEXT3, command=lambda: self.deleteEntry(fileBox))
        removeButton.place(relx=0.69, rely=.46, relwidth=0.25, relheight=0.13)

        # Shape File Select

        # Adding in the Frame
        frame2 = tk.Frame(self.root, highlightbackground="gray70", highlightthickness=1)
        frame2.place(relwidth=0.8, relheight=0.1, relx=0.5, rely=0.47, anchor='n')

        # Select Shape File Label
        shapeLabel = tk.Label(frame2, text=TEXT4, font=('Century', 12), justify=tk.LEFT)
        shapeLabel.place(relheight=0.3, relx=0.02, rely=0.01)

        # Entry Box
        shapeEntry = tk.Entry(frame2)
        shapeEntry.place(relwidth=0.6, relheight=0.455, relx=0.02, rely=0.4)

        # Browse button
        browseShapeButton = tk.Button(frame2, text=FILE_SELECT,
                                      command=lambda: self.SHP_file_selector(shapeEntry))
        browseShapeButton.place(relx=0.69, rely=.4, relwidth=0.25, relheight=0.455)

        # Calculate Frame
        calculate_frame = tk.Frame(self.root)
        calculate_frame.place(relwidth=0.8, relheight=0.05, relx=0.5, rely=0.6, anchor='n')

        # Calculate Button
        calculate_button = tk.Button(calculate_frame, text="Calculate",
                                     command=lambda: self.calculate_action(fileBox, shapeEntry, calculate_button))
        calculate_button.place(relwidth=0.25, relheight=0.91, relx=0.375)

        # Progress Bar
        frame3 = tk.Frame(self.root)
        frame3.place(relwidth=0.8, relheight=0.1, relx=0.5, rely=0.7, anchor='n')
        self.progress_bar = ttk.Progressbar(frame3, orient=tk.HORIZONTAL, length=100, mode='indeterminate')
        self.process_label = tk.Label(frame3, text="Working...", font=('Century', 9), anchor="w")

        # Credits Pane

        # Credits
        lower_frame = tk.Frame(self.root, bg="gray")
        lower_frame.place(relx=0.5, rely=0.93, relwidth=0.8, relheight=0.07, anchor='n')

        credits_label = tk.Label(lower_frame, text=CREDITS, font=('Century', 10), fg='white', bg='gray')
        credits_label.place(relx=0.1, rely=0.2, relwidth=0.8, relheight=0.6)

    def run(self):
        self.root.mainloop()
        return

    def DEM_file_selector(self, fileBox):
        filenames = filedialog.askopenfilenames(initialdir="/D", title="Select DEM Files",
                                                filetypes=(("DEM TIF Files", "*.tif"), ("All Files", "*.*")))
        filenames = list(filenames)
        self.addToFileSelectionBox(filenames, fileBox)
        return

    def SHP_file_selector(self, entry):
        filename = filedialog.askopenfilename(initialdir="/D", title="Select Shape file",
                                              filetypes=(("Shape File (SHP)", "*.shp"), ("All Files", "*.*")))
        self.set_entrybox_text(filename, entry)
        return

    def save_data_selector(self, results):
        destination = filedialog.asksaveasfilename(initialdir="/D", title="Export Data", filetypes=(
            ("Spreadsheet (.csv)", "*.csv"), ("Text (.txt)", "*.txt")))
        # If the user inputs a non empty string
        if destination != "":
            # Checks if the file extension has already been entered.
            if destination[-4:] != ".csv":
                destination = destination + ".csv"
            self.export_data(destination, results)
        return

    # Adds to the list displayed by the list box, if the element isn't already present.
    def addToFileSelectionBox(self, fileNames, fileBox):
        for i in range(len(fileNames)):
            size = fileBox.size()
            contents = fileBox.get(0, size)
            if fileNames[i] not in contents:
                print("Adding File to List")
                fileBox.insert(size, fileNames[i])
            else:
                print("Item already Added")
        return

    # Clears the FileBox
    def clearFileBox(self, fileBox):
        fileBox.delete(0, tk.END)
        return

    # Deletes the selected item
    def deleteEntry(self, fileBox):
        fileBox.delete(tk.ANCHOR)
        return

    def set_entrybox_text(self, filename, entry):
        entry.delete(0, tk.END)
        entry.insert(0, filename)
        return

    def calculate_action(self, fileBox, shapeEntry, calculateButton):
        self.switchButtonState(calculateButton)

        demFiles = fileBox.get(0, tk.END)
        shapeFile = shapeEntry.get()
        myDataHandler = DataHandler(demFiles, shapeFile)

        self.myDEMProcessor = DEMProcessor(myDataHandler)
        # Make a new thread to perform calculations.
        self.queue = queue.Queue()
        self.calculate_thread = threading.Thread(target=self.myDEMProcessor.perform_calculation, args=(self.queue,))

        self.process_label.place(relwidth=1, relheight=0.5, rely=0, relx=0)
        self.progress_bar.place(relwidth=1, relheight=0.5, rely=0.5)
        self.progress_bar["value"] = 0
        self.progress_bar.start()

        # Start the calculate thread and every 100ms check if it is done
        self.calculate_thread.start()
        self.root.after(QUEUE_CHECK_RATE, lambda: self.check_calculation_queue(calculateButton))
        return

    def create_results_window(self, results, data_dict):
        popup = tk.Toplevel()
        popup.title(RESULT)
        popup.resizable(False, False)
        popup.iconbitmap('img/icon_3V8_icon.ico')

        popup_canvas = tk.Canvas(popup, height=HEIGHT, width=WIDTH)
        popup_canvas.pack()

        # Adding in the title
        label = tk.Label(popup_canvas, text=RESULT, font=('Century', 20), anchor='center')
        label.place(relx=0.15, rely=0, relwidth=0.7, relheight=0.05)

        # Now make the tree
        tree = ttk.Treeview(popup_canvas)

        # Define the columns
        tree["columns"] = ("one", "two", "three", "four")
        tree.column("#0", width=50, minwidth=50, stretch=tk.NO)
        tree.column("one", width=130, minwidth=130, stretch=tk.NO)
        tree.column("two", width=130, minwidth=130, stretch=tk.NO)
        tree.column("three", width=130, minwidth=130, stretch=tk.NO)
        tree.column("four", width=130, minwidth=130, stretch=tk.NO)

        # Define the headings
        tree.heading("#0", text="Pair", anchor=tk.W)
        tree.heading("one", text="Layer 1", anchor=tk.W)
        tree.heading("two", text="Layer 2", anchor=tk.W)
        tree.heading("three", text="Volume Difference", anchor=tk.W)
        tree.heading("four", text="Unit", anchor=tk.W)

        # Insert the content.
        filename_dict = {}
        z = 0
        for pair, result in results.items():
            filename_dict[z] = pair  # Put the filename tuple into an indexed dictionary
            filenames = self.extract_filename(pair)  # Shortens the filepath to just the filename, for display purposes
            tree.insert("", z, "entry" + str(z), text=str(z), values=(filenames[0], filenames[1], result[0], result[1]))
            z += 1
        tree.place(relwidth=1, relheight=0.6, relx=0, rely=0.07)

        # Progress Bar
        progressFrame = tk.Frame(popup)
        progressFrame.place(relwidth=0.8, relheight=0.1, relx=0.5, rely=0.8, anchor='n')
        self.progress_bar2 = ttk.Progressbar(progressFrame, orient=tk.HORIZONTAL, length=100, mode='indeterminate')
        self.process_label2 = tk.Label(progressFrame, text="Working...", font=('Century', 9), anchor="w")

        # Add in Buttons
        buttonsFrame = tk.Frame(popup)
        buttonsFrame.place(relwidth=0.8, relheight=0.1, relx=0.5, rely=0.7, anchor='n')

        exportButton = tk.Button(buttonsFrame, text=EXPORT, command=lambda: self.save_data_selector(results))
        exportButton.place(relx=0.1, rely=0, relwidth=0.25, relheight=0.5)

        graphButton = tk.Button(buttonsFrame, text=GRAPH,
                                command=lambda: self.launch_graph(filename_dict, tree.focus(), data_dict, graphButton))
        graphButton.place(relx=0.65, rely=0, relwidth=0.25, relheight=0.5)

        return

    def extract_filename(self, pair):
        names = []
        for i in range(len(pair)):
            startIndex = pair[i].rindex("/") + 1
            endIndex = pair[i].rindex(".")
            name = pair[i][startIndex:endIndex]
            names.append(name)
        return names

    # Checks the calculation thread
    def check_calculation_queue(self, calculateButton):
        try:
            msg = self.queue.get(0)
            self.progress_bar.stop()
            self.progress_bar.place_forget()
            self.process_label.place_forget()
            results = self.myDEMProcessor.get_results()
            data_dict = self.myDEMProcessor.get_dataDict()
            # Now create the popup window.
            self.create_results_window(results, data_dict)
            self.switchButtonState(calculateButton)
        except queue.Empty:
            self.root.after(QUEUE_CHECK_RATE, lambda: self.check_calculation_queue(calculateButton))

    # Saves a CSV at the destination location
    def export_data(self, destination, data):
        CSVWriter(destination, data)
        return

    # Launches a graphical visualization of the Layer Pair. Selected Item is a dictionary.
    def launch_graph(self, filename_dictionary, index, data_dict, visualizeButton):
        # graphWindow = tk.Toplevel()
        # graphWindow.title(RESULT)
        # graphWindow.iconphoto(False, tk.PhotoImage(file='img/icon.png'))
        self.switchButtonState(visualizeButton)

        self.process_label2.place(relwidth=1, relheight=0.5, rely=0, relx=0)
        self.progress_bar2.place(relwidth=1, relheight=0.5, rely=0.5)
        self.progress_bar2["value"] = 0
        self.progress_bar2.start()

        index = int(
            re.findall(r'\d+', str(index))[0])  # Uses regex to find which index is of interest, from eg "entry0"

        # filename dict stores the original filenames
        fn1 = filename_dictionary[index][0]
        fn2 = filename_dictionary[index][1]

        myGraph = GraphProcessor(fn1, fn2, data_dict)

        self.queue2 = queue.Queue()
        self.visualize_thread = threading.Thread(target=myGraph.preprocess, args=(self.queue2,))

        # Start the visualize thread and every 100ms check if it is done
        self.visualize_thread.start()
        self.root.after(QUEUE_CHECK_RATE, lambda: self.check_visualization_queue(myGraph, visualizeButton))

        # figure = myGraph.getFigure()
        # canvas = FigureCanvasTkAgg(figure, graphWindow)
        # canvas.draw()
        # canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
        #
        # toolbar = NavigationToolbar2Tk(canvas, graphWindow)
        # toolbar.update()
        # toolbar.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        #
        # def on_key_press(event):
        #     print("you pressed {}".format(event.key))
        #     key_press_handler(event, canvas, toolbar)
        #
        # canvas.mpl_connect("key_press_event", on_key_press)

        return

    def check_visualization_queue(self, myGraph, visualizeButton):
        try:
            msg = self.queue2.get(0)
            self.progress_bar2.stop()
            self.progress_bar2.place_forget()
            self.process_label2.place_forget()
            self.visualize_thread.join()        # TODO: May be able to remove; waits for the graph to be completely initialized
            myGraph.graph()
            self.switchButtonState(visualizeButton)
        except queue.Empty:
            self.root.after(QUEUE_CHECK_RATE, lambda: self.check_visualization_queue(myGraph, visualizeButton))

    def switchButtonState(self, button):
        if button['state'] == tk.NORMAL:
            button['state'] = tk.DISABLED
        else:
            button['state'] = tk.NORMAL
