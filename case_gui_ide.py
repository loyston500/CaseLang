# hello mister Inspect
import gi
import sys
import os

if len(sys.argv) == 2:
    FILE = sys.argv[1]
else:
    print("Error: No file passed")
    exit()

try:
    from ide_data import COMPILER, TERMINAL
except:
    print("Warning: IDE data got Currupted. Recreating it.")
    with open("ide_data.py", "w") as opened_file:
        opened_file.write("COMPILER='python3.8'\nTERMINAL='x-terminal-emulator -e'")
    COMPILER, TERMINAL = "python3.8", "x-terminal-emulator -e"


gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Pango
from gi.repository import GObject


class main(Gtk.Window):
    def __init__(self):
        global FILE
        Gtk.Window.__init__(self, title="CaseLang IDE " + FILE)

        self.set_default_size(400, 800)

        self.grid = Gtk.Grid()
        self.add(self.grid)

        self.create_textview()
        self.create_labels()
        self.create_buttons()

        self.grid_arrange()

    def create_buttons(self):
        self.compile_button = Gtk.Button(label="Compile")
        self.compile_button.connect("clicked", self.on_compile_button_click)

        self.compile_and_run_button = Gtk.Button(label="Compile & Run")
        self.compile_and_run_button.connect(
            "clicked", self.on_compile_and_run_button_click
        )

    def create_labels(self):
        self.compiled_code_label = Gtk.Label(label="")

    def create_textview(self):
        global FILE
        self.scrolledwindow = Gtk.ScrolledWindow()
        self.scrolledwindow.set_hexpand(True)
        self.scrolledwindow.set_vexpand(True)

        self.textview = Gtk.TextView()
        self.textbuffer = self.textview.get_buffer()
        self.textbuffer.set_text(self.get_file_data(FILE))
        self.scrolledwindow.add(self.textview)

    def grid_arrange(self):
        self.grid.attach(self.scrolledwindow, 1, 0, 4, 1)
        self.grid.attach(self.compile_button, 1, 2, 2, 1)
        self.grid.attach(self.compile_and_run_button, 3, 2, 2, 1)

    def get_textview_text(self):
        start_iter = self.textbuffer.get_start_iter()
        end_iter = self.textbuffer.get_end_iter()
        return self.textbuffer.get_text(start_iter, end_iter, True)

    def get_file_data(self, file):
        try:
            with open(file) as opened_file:
                return opened_file.read()
        except FileNotFoundError:
            return ""

    def save_file(self, file, code):
        with open(file, "w") as opened_file:
            opened_file.write(code)

    def on_compile_button_click(self, widget):
        code = self.get_textview_text()

        global COMPILER, TERMINAL, FILE
        self.save_file(FILE, code)
        os.system(COMPILER + " case_compiler.py " + FILE)

    def on_compile_and_run_button_click(self, widget):
        code = self.get_textview_text()

        global COMPILER, TERMINAL, FILE
        self.save_file(FILE, code)
        os.system(TERMINAL + " " + COMPILER + " -i case_compiler.py -run " + FILE)


window = main()
window.connect("destroy", Gtk.main_quit)
window.show_all()
Gtk.main()
# ah you read ma code?
