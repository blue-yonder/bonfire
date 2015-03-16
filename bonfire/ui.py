'''
Created on 13.03.15

@author = mharder
'''

from __future__ import division, print_function

import urwid


class LogListWalker(urwid.ListWalker):
    def __init__(self, api, query, fields=None):
        # TODO Adaptive query using offsets
        self.result = api.search(query)

        if fields is None:
            fields = ["message", "level"]

        field_lengths = dict(
            map(lambda f:
                (f, sorted(map(lambda m:
                               len(str(m.message_dict.get(f, ""))),
                               self.result.messages))[int(0.75*len(self.result.messages))]), fields)
        )

        def log_entry(entry):
            field_widgets = map(lambda f: ('weight', field_lengths[f], urwid.Text(str(entry.message_dict.get(f,"")))), fields)

            return urwid.Columns([(23, urwid.Text(entry.timestamp.format("YYYY-MM-DD HH:MM:ss.SSS")))] + field_widgets,
                                 dividechars = 1)

        self.widgets = map(log_entry, self.result.messages)
        self.focus = 0

    def get_focus(self):
        return (self.widgets[self.focus], self.focus)

    def set_focus(self, position):
        self.focus = position

    def get_next(self, position):
        if position >= len(self.widgets)-1:
            return (None, position)

        return (self.widgets[position+1], position+1)

    def get_prev(self, position):
        if position <= 0:
            return (None, position)

        return (self.widgets[position-1], position-1)


class LogListBox(urwid.ListBox):
    def __init__(self, api, query, fields=None):
        body = LogListWalker(api, query, fields)
        super(LogListBox, self).__init__(body)

    def keypress(self, size, key):
        key = super(LogListBox, self).keypress(size, key)
        if key == 'q':
            raise urwid.ExitMainLoop()
        return key


def run_ui(api, initial_query, fields=None):
    palette = [('I say', 'default,bold', 'default'),]

    log_list = LogListBox(api, initial_query, fields)

    main = urwid.Pile([log_list, (1, urwid.Text("Press 'q' to exit"))])
    urwid.MainLoop(main, palette).run()

