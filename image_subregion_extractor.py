import Tkinter
import tkFileDialog
from PIL import ImageTk
import PIL.Image
import os
import re

BACKGROUND_COLOR = '#ededed'

WINDOW_WIDTH = 580
WINDOW_HEIGHT = 600

PAD_SMALL = 2
PAD_MEDIUM = 4
PAD_LARGE = 8
PAD_EXTRA_LARGE = 14


class Application(Tkinter.Frame):

    def __init__(self, master):

        Tkinter.Frame.__init__(self, master=master)

        self.image_name = None
        self.image_dir = None

        self.master.minsize(width=WINDOW_WIDTH, height=WINDOW_HEIGHT)

        file_chooser_frame = Tkinter.Frame(self.master, bg=BACKGROUND_COLOR)
        file_chooser_frame.pack(
            fill=Tkinter.X,
            expand=False,
            anchor=Tkinter.N,
            padx=PAD_MEDIUM,
            pady=PAD_MEDIUM
        )

        file_chooser_button = Tkinter.Button(
            file_chooser_frame,
            text='Choose Image File...',
            command=self.choose_files
        )
        file_chooser_button.pack(side=Tkinter.LEFT)

        self.snip_string = Tkinter.StringVar()
        snip_label = Tkinter.Label(
            file_chooser_frame,
            text="Snip Label: ",
            bg=BACKGROUND_COLOR
        )
        snip_label_entry = Tkinter.Entry(
            file_chooser_frame,
            textvariable=self.snip_string
        )
        snip_label_entry.pack(side=Tkinter.RIGHT)
        snip_label.pack(side=Tkinter.RIGHT)

        # the canvas frame's contents will use grid b/c of the double
        # scrollbar (they don't look right using pack), but the canvas itself
        # will be packed in its frame
        canvas_frame = Tkinter.Frame(self.master, bg=BACKGROUND_COLOR)
        canvas_frame.grid_rowconfigure(0, weight=1)
        canvas_frame.grid_columnconfigure(0, weight=1)
        canvas_frame.pack(
            fill=Tkinter.BOTH,
            expand=True,
            anchor=Tkinter.N,
            padx=PAD_MEDIUM,
            pady=PAD_MEDIUM
        )

        self.canvas = Tkinter.Canvas(canvas_frame, cursor="cross")

        self.scrollbar_v = Tkinter.Scrollbar(
            canvas_frame,
            orient=Tkinter.VERTICAL
        )
        self.scrollbar_h = Tkinter.Scrollbar(
            canvas_frame,
            orient=Tkinter.HORIZONTAL
        )
        self.scrollbar_v.config(command=self.canvas.yview)
        self.scrollbar_h.config(command=self.canvas.xview)

        self.canvas.config(yscrollcommand=self.scrollbar_v.set)
        self.canvas.config(xscrollcommand=self.scrollbar_h.set)

        self.canvas.grid(
            row=0,
            column=0,
            sticky=Tkinter.N + Tkinter.S + Tkinter.E + Tkinter.W
        )
        self.scrollbar_v.grid(row=0, column=1, sticky=Tkinter.N + Tkinter.S)
        self.scrollbar_h.grid(row=1, column=0, sticky=Tkinter.E + Tkinter.W)

        # setup some button and key bindings
        self.canvas.bind("<ButtonPress-1>", self.on_draw_button_press)
        self.canvas.bind("<B1-Motion>", self.on_draw_move)

        self.canvas.bind("<ButtonPress-2>", self.on_pan_button_press)
        self.canvas.bind("<B2-Motion>", self.pan_image)
        self.canvas.bind("<ButtonRelease-2>", self.on_pan_button_release)

        # save our sub-region snippet
        self.master.bind("<Return>", self.extract_region)

        self.rect = None

        self.start_x = None
        self.start_y = None

        self.pan_start_x = None
        self.pan_start_y = None

        self.image = None
        self.tk_image = None

        self.pack()

    def on_draw_button_press(self, event):
        # starting coordinates
        self.start_x = self.canvas.canvasx(event.x)
        self.start_y = self.canvas.canvasy(event.y)

        # create a new rectangle if we don't already have one
        if self.rect is None:
            self.rect = self.canvas.create_rectangle(
                self.start_x,
                self.start_y,
                self.start_x,
                self.start_y,
                outline='green',
                width=2
            )

    def on_draw_move(self, event):
        cur_x = self.canvas.canvasx(event.x)
        cur_y = self.canvas.canvasy(event.y)

        # update rectangle size with mouse position
        self.canvas.coords(self.rect, self.start_x, self.start_y, cur_x, cur_y)

    def on_pan_button_press(self, event):
        self.canvas.config(cursor='fleur')

        # starting position for panning
        self.pan_start_x = int(self.canvas.canvasx(event.x))
        self.pan_start_y = int(self.canvas.canvasy(event.y))

    def pan_image(self, event):
        self.canvas.scan_dragto(
            event.x - self.pan_start_x,
            event.y - self.pan_start_y,
            gain=1
        )

    # noinspection PyUnusedLocal
    def on_pan_button_release(self, event):
        self.canvas.config(cursor='cross')

    # noinspection PyUnusedLocal
    def extract_region(self, event):
        output_dir = "/".join(
            [
                self.image_dir,
                self.snip_string.get().strip()
            ]
        )

        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        corners = self.canvas.coords(self.rect)
        corners = tuple([int(c) for c in corners])
        region = self.image.crop(corners)

        match = re.search('(.+)\.(.+)$', self.image_name)
        output_filename = "".join(
            [
                match.groups()[0],
                '_<',
                str(corners[0]),
                ',',
                str(corners[1]),
                '>'
            ]
        )
        output_filename = ".".join([output_filename, match.groups()[1]])

        output_file_path = "/".join([output_dir, output_filename])

        region.save(output_file_path)

    def choose_files(self):
        self.canvas.delete(self.rect)
        self.rect = None

        selected_file = tkFileDialog.askopenfile('r')

        self.image = PIL.Image.open(selected_file)
        height, width = self.image.size
        self.canvas.config(scrollregion=(0, 0, height, width))
        self.tk_image = ImageTk.PhotoImage(self.image)
        self.canvas.create_image(0, 0, anchor=Tkinter.NW, image=self.tk_image)

        self.image_name = os.path.basename(selected_file.name)
        self.image_dir = os.path.dirname(selected_file.name)

root = Tkinter.Tk()
app = Application(root)
root.mainloop()
