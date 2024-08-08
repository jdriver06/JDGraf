
import tkinter as tk
from tkinter import filedialog

import matplotlib
matplotlib.use('TkAgg')

from numpy import arange, sin, pi
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib import colors as mcolors
# Implement the default mpl key bindings
# from matplotlib.backend_bases import key_press_handler

from matplotlib.figure import Figure
from matplotlib.lines import Line2D
import utchem_io_module

import pandas as pd


class JDGrafGUI(tk.Tk):

    def __init__(self):
        super(JDGrafGUI, self).__init__()
        self.data = pd.DataFrame(data=[], columns=[])
        self.title('JDGraf')
        self.geometry('800x800')
        label = tk.Label(self, text="", cursor= "hand2", foreground= "black", font=('Arial 14',))
        self.source_file = ''
        label.bind("<Button-1>", self.source_select)
        label.pack()
        self.source_label = label
        frame = tk.Frame(self)
        frame.pack()
        listbox = tk.Listbox(frame, exportselection=False)
        listbox.pack(side=tk.LEFT)
        listbox.bind('<<ListboxSelect>>', self.update_x_sel)
        listbox2 = tk.Listbox(frame, exportselection=False)
        listbox2.pack(side=tk.LEFT)
        listbox2.bind('<<ListboxSelect>>', self.update_y_sel)
        listbox3 = tk.Listbox(frame, exportselection=False)
        listbox3.pack(side=tk.LEFT)
        for i, color in enumerate(mcolors.TABLEAU_COLORS.keys()):
            listbox3.insert(i + 1, color[4:])
            listbox3.itemconfig(i, {'fg': mcolors.TABLEAU_COLORS[color]})
        self.x_sel = -1
        self.y_sel = -1
        self.x_index = -1
        self.y_indexes = []
        self.lines = []
        btn = tk.Button(frame, text='Plot', command=self.plot)
        btn.pack(side=tk.LEFT)
        btn2 = tk.Button(frame, text='Reload', command=self.reload)
        btn2.pack(side=tk.LEFT)
        btn3 = tk.Button(frame, text='Clear', command=self.clear_plot)
        btn3.pack(side=tk.LEFT)
        self.source_listbox_x = listbox
        self.source_listbox_y = listbox2
        self.color_listbox = listbox3
        self.plot_button = btn
        self.fig = Figure()
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        self.subplot = self.fig.add_subplot(111)
        self.canvas.draw()
        self.update_source_label()
        self.canvas.get_tk_widget()

    def update_source_label(self):
        self.source_label.config(text='Source: {}'.format(self.source_file))

    def source_select(self, _):
        self.source_file = filedialog.askopenfilename()
        self.update_source_label()
        if self.source_file:
            self.load_from_source()

    def load_from_source(self):
        self.data = utchem_io_module.import_hist(self.source_file, 23)
        JDGrafGUI.source_listbox_populate(self.source_listbox_x, self.data.columns.tolist())
        JDGrafGUI.source_listbox_populate(self.source_listbox_y, self.data.columns.tolist())

    @staticmethod
    def source_listbox_populate(listbox: tk.Listbox, items: list):
        listbox.delete(0, listbox.size() - 1)
        for i, c in enumerate(items):
            listbox.insert(i + 1, c)

    def update_x_sel(self, _):
        sel = self.source_listbox_x.curselection()
        if sel:
            self.x_sel = sel[0]

    def update_y_sel(self, _):
        sel = self.source_listbox_y.curselection()
        if sel:
            self.y_sel = sel[0]

    def test(self):
        t = arange(0.0, 3.0, 0.01)
        s = sin(2 * pi * t)

        self.subplot.plot(t, s)

    def plot(self):

        i = self.x_sel
        j = self.y_sel
        k = self.color_listbox.curselection()
        if not k:
            k = -1
        else:
            k = k[0]

        if i == -1 or j == -1 or k == -1:
            return

        self.x_index = i
        self.y_indexes.append(j)

        color = 'tab:{}'.format(self.color_listbox.get(k))

        line = self.subplot.plot(self.data.values[:, i], self.data.values[:, j], color=mcolors.TABLEAU_COLORS[color])
        self.lines.append(line[0])
        self.subplot.set_xlabel(self.data.columns[i])
        self.set_legend()
        self.canvas.draw()
        self.source_listbox_x.config(state=tk.DISABLED)

    def set_legend(self):
        legend_items = []
        for i in self.y_indexes:
            legend_items.append(self.data.columns[i])
        self.subplot.legend(legend_items)

    def reload(self):
        self.load_from_source()
        for i, line in enumerate(self.lines):
            print(self.x_index, self.y_indexes[i])
            if isinstance(line, Line2D):
                line.set_data(self.data.values[:, self.x_index], self.data.values[:, self.y_indexes[i]])
        self.subplot.relim()
        self.subplot.autoscale()
        self.canvas.draw()

    def clear_plot(self):
        self.subplot.clear()
        self.x_index = -1
        self.y_indexes = []
        self.lines = []
        self.source_listbox_x.config(state=tk.NORMAL)

        self.canvas.draw()

def main():
    root = JDGrafGUI()
    # root.title('root')
    # label = tk.Label(root, text="Hello, Tkinter!")
    # label.pack()
    root.mainloop()

if __name__ == "__main__":
    main()
