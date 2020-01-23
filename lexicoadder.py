#!/usr/bin/env -O python3
"""First prototype for an dictionary extension workflow app."""

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk


class LexicoAdderWindow(Gtk.Window):
    """Main window of the app."""

    def __init__(self):
        """Initialise GTK GUI."""
        Gtk.Window.__init__(self, title="Hello World")

        headboard = Gtk.HeaderBar()
        headboard.set_show_close_button(True)
        headboard.props.title = "Add words to lexicons!!"
        self.set_titlebar(headboard)

        self.box = Gtk.Box(spacing=6)
        self.add(self.box)

        self.texti = Gtk.TextView()
        self.box.pack_start(self.texti, True, True, 0)


def main():
    """Parse args, create GUI."""
    win = LexicoAdderWindow()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()


if __name__ == "__main__":
    main()
