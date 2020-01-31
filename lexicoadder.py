#!/usr/bin/env -O python3
"""First prototype for an dictionary extension workflow app."""

from sys import argv
import os.path
import subprocess
from subprocess import PIPE
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import GLib, Gio, Gtk


def apepipe(args, inputs, **kwargs):
    # FIXME: when 3.7 is common, use subprocess.run
    with subprocess.Popen(args, stdout=PIPE, stdin=PIPE) as ape:
        ape.stdin.write(inputs.encode())
        ape.stdin.close()
        outputs = ape.stdout.read().decode("UTF-8")
    return outputs


class LexicoAdderWindow(Gtk.ApplicationWindow):
    """Main window of the app."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.header = Gtk.HeaderBar()
        self.header.set_show_close_button(True)
        self.header.props.title = "Lexico🐍: (Untitled)"
        self.open = Gtk.Button()
        icon = Gio.ThemedIcon(name="document-open")
        image = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.BUTTON)
        self.open.add(image)
        self.open.connect("clicked", self.on_open)
        self.header.pack_end(self.open)
        self.analyse = Gtk.Button.new_with_label("Analyse")
        self.analyse.connect("clicked", self.on_analyse)
        self.header.pack_end(self.analyse)
        languagestext = apepipe(["apertium", "-l"], "")
        languages = Gtk.ListStore(str)
        for lang in languagestext.split():
            languages.append([lang.strip()])
        self.language_list = Gtk.ComboBox.new_with_model_and_entry(languages)
        self.language_list.set_entry_text_column(0)
        self.header.pack_end(self.language_list)
        self.set_titlebar(self.header)
        self.box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.add(self.box)
        self.input_scroll = Gtk.ScrolledWindow()
        self.input_scroll.set_border_width(5)
        self.input_scroll.set_policy(Gtk.PolicyType.AUTOMATIC,
                                     Gtk.PolicyType.AUTOMATIC)
        self.texti = Gtk.TextView()
        self.input_scroll.add(self.texti)
        self.box.pack_start(self.input_scroll, True, True, 0)
        self.inbuffer = self.texti.get_buffer()
        self.output_scroll = Gtk.ScrolledWindow()
        self.output_scroll.set_border_width(5)
        self.output_scroll.set_policy(Gtk.PolicyType.AUTOMATIC,
                                     Gtk.PolicyType.AUTOMATIC)
        self.texto = Gtk.TextView(editable=False)
        self.output_scroll.add(self.texto)
        self.box.pack_start(self.output_scroll, True, True, 0)
        self.outbuffer = self.texto.get_buffer()

    def on_open(self, button):
        dialog = Gtk.FileChooserDialog("Please choose a file", self,
                                       Gtk.FileChooserAction.OPEN,
                                       (Gtk.STOCK_CANCEL,
                                        Gtk.ResponseType.CANCEL,
                                        Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
        dialog.set_current_folder(os.path.abspath('.'))
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            with open(dialog.get_filename(), 'r') as f:
                data = f.read()
                self.inbuffer.set_text(data)
                self.header.props.title = "Lexico🐍: " + dialog.get_filename()
        elif response == Gtk.ResponseType.CANCEL:
            print("Cancel clicked")
        dialog.destroy()

    def on_analyse(self, button):
        print("We analyse...")
        textinput = self.inbuffer.get_text(self.inbuffer.get_start_iter(),
                                           self.inbuffer.get_end_iter(), False)
        outputs = apepipe(["apertium", self.get_langs()], textinput)
        self.outbuffer.set_text(outputs)

    def get_langs(self):
        tree_iter = self.language_list.get_active_iter()
        if tree_iter is not None:
            model = self.language_list.get_model()
            return model[tree_iter][0]


class LexicoAdderApplication(Gtk.Application):
    """Application container stuff."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args,
                         application_id="com.flammie.github.lexicoadder",
                         flags=Gio.ApplicationFlags.HANDLES_COMMAND_LINE,
                         **kwargs)
        self.window = None
        self.add_main_option("test", ord("t"), GLib.OptionFlags.NONE,
                             GLib.OptionArg.NONE, "Command line test", None)

    def do_startup(self):
        Gtk.Application.do_startup(self)
        action = Gio.SimpleAction.new("about", None)
        action.connect("activate", self.on_about)
        self.add_action(action)
        action = Gio.SimpleAction.new("quit", None)
        action.connect("activate", self.on_quit)
        self.add_action(action)

    def do_activate(self):
        # We only allow a single window and raise any existing ones
        if not self.window:
            # Windows are associated with the application
            # when the last one is closed the application shuts down
            self.window = LexicoAdderWindow(application=self,
                                            title="Lexicoadder")
            self.window.show_all()
        self.window.present()

    def do_command_line(self, command_line):
        options = command_line.get_options_dict()
        # convert GVariantDict -> GVariant -> dict
        options = options.end().unpack()
        if "test" in options:
            # This is printed on the main instance
            print("Test argument recieved: %s" % options["test"])
        self.activate()
        return 0

    def on_about(self, action, param):
        about_dialog = Gtk.AboutDialog(transient_for=self.window, modal=True)
        about_dialog.present()

    def on_quit(self, action, param):
        self.quit()


if __name__ == "__main__":
    app = LexicoAdderApplication()
    app.run(argv)

