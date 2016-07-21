# -*- coding: utf-8 -*-
from gi.repository import GObject, Gedit, Gio

actions = [
          ("bracket_match", "<Control>M", "GoTo Bracket Match")
          ]

brackets = '({[]})'


class BracketMatchingPyPluginAppActivatable( GObject.Object, Gedit.AppActivatable ):

    app = GObject.property(type=Gedit.App)

    def do_activate( self ):
        self.menu_ext = self.extend_menu("tools-section")
        for action_name, key, menu_name in actions:
            fullname = "win." + action_name
            self.app.add_accelerator(key, fullname, None)
            item = Gio.MenuItem.new(_(menu_name), fullname)
            self.menu_ext.append_menu_item(item)

    def do_deactivate( self ):
        for action_name, key, menu_name in actions:
            self.app.remove_accelerator("win." + action_name, None)
        self.menu_ext = None


class BracketMatchingPyPlugin( GObject.Object, Gedit.WindowActivatable ):
    __gtype_name__ = 'BracketMatchingPyPlugin'
    window = GObject.property(type=Gedit.Window)

    def __init__( self ):
        GObject.Object.__init__(self)

    def do_activate( self ):
        self.do_update_state()
        for action_name, key, menu_name in actions:
            action = Gio.SimpleAction(name=action_name)
            action.connect('activate', getattr(self, action_name))
            self.window.add_action(action)

    def do_update_state( self ):
        self.doc = self.window.get_active_document()
        self.view = self.window.get_active_view()

    def bracket_match( self, action=None, data=None ):
        pos = self.doc.get_iter_at_mark(self.doc.get_insert())
        bracket = pos.get_char()

        if not bracket or bracket not in brackets:
            # maybe the bracket is in front of the cursor?
            pos.backward_char()
            bracket = pos.get_char()

        if not bracket or bracket not in brackets:
            # print('Not a bracket')
            return

        i = brackets.index(bracket)
        match = brackets[i*-1 - 1]

        def find_match(pos, move_pos):
            nest_count = 0
            while move_pos():
                check_char = pos.get_char()

                if check_char == bracket:
                    nest_count += 1

                elif check_char == match and nest_count > 0:
                    nest_count -= 1

                elif check_char == match and nest_count == 0:
                    # found it!
                    self.doc.place_cursor(pos)
                    self.view.scroll_to_iter(pos, 0, False, 0, 0)
                    break

        if i < len(brackets)/2:
            # opening bracket, so search forward

            # lame... the _find_char functions don't work :(
            # if pos.forward_find_char(check_char, data, None):
            #     self.doc.place_cursor(pos)

            find_match(pos, pos.forward_char)

        else:
            # closing bracket, so search backward
            find_match(pos, pos.backward_char)


