
import tkinter as tk
from tkinter import filedialog

import matplotlib
matplotlib.use('TkAgg')

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib import colors as mcolors
# Implement the default mpl key bindings
# from matplotlib.backend_bases import key_press_handler

from matplotlib.figure import Figure
from matplotlib.lines import Line2D
import utchem_io_module

import pandas as pd


__version__ = '1.0.0'


class JDGrafGUI(tk.Tk):

    def __init__(self):
        super(JDGrafGUI, self).__init__()
        self.data = pd.DataFrame(data=[], columns=[])
        self.title('JDGraf v{}'.format(__version__))
        self.geometry('800x800')
        self.source_label = tk.Label(self, text="", cursor= "hand2", foreground= "black", font=('Arial 14',),
                                     height=2, anchor='w')
        self.source_file = ''
        self.source_label.bind("<Button-1>", self.source_select)
        self.source_label.bind("<Enter>", lambda _: self.source_color_config('blue'))
        self.source_label.bind("<Leave>", lambda _: self.source_color_config('black'))
        self.source_label.pack(side=tk.TOP, anchor='w', padx=10)
        frame = tk.Frame(self)
        frame.pack(pady=10)
        x_frame = tk.Frame(frame)
        x_frame.pack(side=tk.LEFT)
        source_x_label = tk.Label(x_frame, text='X Variable:')
        source_x_label.pack(side=tk.TOP)
        self.source_listbox_x = tk.Listbox(x_frame, exportselection=False, selectbackground='black', height=10)
        self.source_listbox_x.pack(side=tk.TOP)
        y_frame = tk.Frame(frame)
        y_frame.pack(side=tk.LEFT)
        source_y_label = tk.Label(y_frame, text='Y Variable:')
        source_y_label.pack(side=tk.TOP)
        self.source_listbox_y = tk.Listbox(y_frame, exportselection=False, selectbackground='black', height=10)
        self.source_listbox_y.pack(side=tk.TOP)
        self.source_listbox_y.bind('<<ListboxSelect>>', self.source_y_select)
        c_frame = tk.Frame(frame)
        c_frame.pack(side=tk.LEFT)
        source_c_label = tk.Label(c_frame, text='Color:')
        source_c_label.pack(side=tk.TOP)
        self.color_listbox = tk.Listbox(c_frame, exportselection=False, height=10)
        self.color_listbox.pack(side=tk.TOP)
        self.color_listbox.bind('<<ListboxSelect>>', self.update_select_background)
        for i, color in enumerate(mcolors.TABLEAU_COLORS.keys()):
            self.color_listbox.insert(i + 1, color[4:])
            self.color_listbox.itemconfig(i, {'fg': mcolors.TABLEAU_COLORS[color]})
        self.x_sel = -1
        self.y_sel = -1
        self.x_index = -1
        self.y_indexes = []
        self.lines = []
        btn_frame = tk.Frame(frame)
        btn_frame.pack(side=tk.TOP, pady=20)
        btn = tk.Button(btn_frame, text='Plot Selected', command=self.plot, width=15)
        btn.pack(side=tk.TOP)
        self.remove_btn = tk.Button(btn_frame, text='Remove Selected', command=self.remove, width=15)
        self.remove_btn.pack(side=tk.TOP)
        btn2 = tk.Button(btn_frame, text='Reload All', command=self.reload, width=15)
        btn2.pack(side=tk.TOP)
        btn3 = tk.Button(btn_frame, text='Clear All', command=self.clear_plot, width=15)
        btn3.pack(side=tk.TOP)
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

    def source_color_config(self, color: str) -> None:
        self.source_label.config(foreground=color)

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

    @staticmethod
    def get_sel(sel: tuple) -> int:
        if not sel:
            return -1
        else:
            return int(sel[0])

    def source_y_select(self, _):
        j = JDGrafGUI.get_sel(self.source_listbox_y.curselection())
        if j not in self.y_indexes:
            return
        ind = self.y_indexes.index(j)
        l_color = self.lines[ind].get_color()
        for k, color in enumerate(mcolors.TABLEAU_COLORS.values()):
            if color == l_color:
                self.color_listbox.select_clear(self.color_listbox.curselection()[0])
                self.color_listbox.selection_set(k)
                self.color_listbox.config(selectbackground=color)
                break

    def update_select_background(self, event: tk.Event):
        if event.widget == self.color_listbox:
            item = self.color_listbox.get(self.color_listbox.curselection())
            color = mcolors.TABLEAU_COLORS['tab:{}'.format(item)]
            self.color_listbox.config(selectbackground=color)
            j = JDGrafGUI.get_sel(self.source_listbox_y.curselection())

            if j == -1 or j not in self.y_indexes:
                return

            self.lines[self.y_indexes.index(j)].set_color(color)
            self.set_legend()
            self.canvas.draw()

    def plot(self):

        i = JDGrafGUI.get_sel(self.source_listbox_x.curselection())
        j = JDGrafGUI.get_sel(self.source_listbox_y.curselection())
        k = JDGrafGUI.get_sel(self.color_listbox.curselection())

        if i == -1 or j == -1 or k == -1:
            return

        if j in self.y_indexes:
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

    def remove(self) -> None:

        if not self.y_indexes:
            return
        elif len(self.y_indexes) == 1:
            self.clear_plot()
            return

        j = JDGrafGUI.get_sel(self.source_listbox_y.curselection())
        self.subplot.lines.pop(self.y_indexes.index(j))
        self.y_indexes.remove(j)
        self.set_legend()
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
    root.mainloop()

if __name__ == "__main__":
    main()
