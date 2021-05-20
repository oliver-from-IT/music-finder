# Music Finder
# Oliver Spain
# ver 1.1.0

import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import json
import xml.etree.ElementTree as ET
from xml.dom.minidom import parseString
from tkinter import *
from tkinter import ttk
from random import randrange

class Main():

    def __init__(self):

        os.environ['SPOTIPY_CLIENT_ID']='68424f2fdeae4d95a19f0f0e2f1b1221'
        os.environ['SPOTIPY_CLIENT_SECRET']='3545842018874cba81a12e536dbce58e'

        auth_manager = SpotifyClientCredentials()
        self.sp = spotipy.Spotify(auth_manager=auth_manager)

        self.root = ET.Element('root')
        self.tree = ET.ElementTree(self.root)

        with open('genres.json', 'r') as f:
            genres_dict = json.load(f)
        self.genres_list = genres_dict[0]['genres']

    def search_criteria(self, genre):

        if genre in self.genres_list:
            return True
        else:
            return False

    def get_recommendations(self, required_genres, amount):

        if required_genres == []:
            return [False, 3, None]

        case = 1
        for genre in required_genres:
            if self.search_criteria(genre) == False:
                print(f'Genre {case} "{genre}" is invalid')
                return [False, case, genre]
            case += 1

        if 1 < amount < 100:
            pass
        else:
            return [False, 4, amount]

        print(f'Amount of recommendations: {amount}\nSelected genres: {required_genres}')
        results = self.sp.recommendations(seed_genres=required_genres, limit=amount)

        for tracks in results['tracks']:
            track = str(tracks['name'])
            uri = str(tracks['uri'])

            song = ET.SubElement(self.root, 'song', uri=uri)
            ET.SubElement(song, 'track').text = track

            artists_list = []
            for artists in tracks['artists']:
                artist = str(artists['name'])
                artists_list.append(artist)

            ET.SubElement(song, 'artists').text = (', '.join(artists_list))

            if tracks['album']['album_type'] == 'ALBUM':
                album =  tracks['album']['name']

                ET.SubElement(song, 'album').text = album

        self.tree.write('Recommendations.xml', 'utf-8')

        print('Search completed')
        try:
            xml = parseString(ET.tostring(self.root))
            xml_pretty = xml.toprettyxml()
            print(f'Results found: \n{xml_pretty}', end='')
        except:
            print(f'Invalid characters')

        return[self.root]

class App():

    def __init__(self, root):
        
        root.title('Music Finder')
        s = ttk.Style()
        s.theme_use('clam')

        mainframe = ttk.Frame(root, padding='5 5 5 5')
        mainframe.grid(column=0, row=0, sticky='NSEW')
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        root.minsize(550, 275)

        mainframe.columnconfigure(0, weight=1)
        mainframe.columnconfigure(1, weight=0)
        mainframe.columnconfigure(2, weight=0)
        mainframe.columnconfigure(3, weight=0)
        mainframe.rowconfigure(0, weight=1)
        mainframe.rowconfigure(1, weight=0)
        mainframe.rowconfigure(2, weight=0) 

        output_cmd = root.register(self.get_output)
        validate_cmd = root.register(self.validate)

        self.output_treeview = ttk.Treeview(mainframe, show='tree', height=20)
        self.output_treeview.grid(ipadx=150, column=0, row=0, columnspan=4, sticky='NSEW')

        output_scrollbar = ttk.Scrollbar(mainframe, orient='vertical', command=self.output_treeview.yview)
        output_scrollbar.grid(column=3, row=0, columnspan=4, sticky='NSE')
        self.output_treeview.configure(yscrollcommand=output_scrollbar.set)

        search_button = ttk.Button(mainframe, text='Get recommendations', command=output_cmd)
        search_button.grid(column=0, row=2, sticky='NSEW')

        self.options_var1 = StringVar()
        self.options_var1.set(Main().genres_list[randrange(1,126)])
        genre_input1 = ttk.Combobox(mainframe, values=Main().genres_list, textvariable=self.options_var1)
        genre_input1.grid(column=1, row=2, sticky='NSEW')

        self.options_var2 = StringVar()
        self.options_var2.set(Main().genres_list[randrange(1,126)])
        genre_input2 = ttk.Combobox(mainframe, values=Main().genres_list, textvariable=self.options_var2)
        genre_input2.grid(column=2, row=2, sticky='NSEW')

        self.amount_var = StringVar()
        self.amount_var.set(5)
        output_amount = ttk.Entry(mainframe, textvariable=self.amount_var, validate='key', validatecommand=(validate_cmd, '%P'))
        output_amount.grid(column=3, row=2, sticky='NSEW')

        self.popup_copy = Menu(self.output_treeview, tearoff=0)
        self.popup_copy.add_command(command=self.copy_selection, label='Copy')

        root.bind('<Return>', output_cmd)
        root.bind('<Control-c>', self.copy_menu)
        print(f'GUI set-up done')

    def validate(self, input):
        try:
            int(input)
        except ValueError:
            return False
        return True

    def get_output(self):
        selected_genres = []
        option1 = str(self.options_var1.get())
        option2 = str(self.options_var2.get())
        if option1 != '':
            selected_genres.append(option1)
        if option2 != '':
            selected_genres.append(option2)

        recommendation_amount = int(self.amount_var.get())

        recommendations = Main().get_recommendations(selected_genres, recommendation_amount)
        if recommendations[0] == False:
            print(f'Error!')
            condition = [recommendations[1], recommendations[2]]
            self.display_popup(condition)
            return
        else:
            pass

        self.output_treeview.delete(*self.output_treeview.get_children())

        # xml = 'Recommendations.xml'
        # with open(xml) as f:
        #     read_data = f.read()
        # rootNode = ET.fromstring(read_data)
    
        self.create_treeview(recommendations[0])

        print(f'Output print finished')

    def create_treeview(self, d, depth=0, parent=""):

        for child in d:
            if depth == 0:
                text_set = f'{child.tag} uri - {child.attrib["uri"]}'
            else:
                text_set = f'{child.tag} - {child.text}'

            item = self.output_treeview.insert(parent, 'end', None, text=text_set, open=True)

            if child.__len__() > 0:
                self.create_treeview(child, depth + 1, parent=item)

    def copy_selection(self):
        item = self.output_treeview.selection()[0]
        root.clipboard_clear()
        root.clipboard_append(self.output_treeview.item(item, option='text'))

        print(f'Copied: {root.clipboard_get()}')

    def copy_menu(self, event):
        self.output_treeview.identify_row(event.y)
        self.popup_copy.post(event.x_root, event.y_root)

    def display_popup(self, condition):

        self.win = Toplevel(padx=5, pady=5, bg='indian red')
        self.win.focus_force()
        self.win.title('Error!')

        self.win.columnconfigure(0, weight=1)
        self.win.rowconfigure(0, weight=1)
        self.win.rowconfigure(1, weight=1)

        resolve_cmd = root.register(lambda : self.resolve_error(condition[0]))

        if condition[0] == 3:
            label_text = f'Invalid input: \n\nat least one genre must be picked'
        elif condition[0] == 4:
            label_text = f'Invalid input: \n\namount of recommendations must be between 1 and 100'
        else:
            label_text = f'Invalid input: \n\ngenre {condition[0]} "{condition[1]}" does not exist'

        error_label = ttk.Label(self.win, text=label_text)
        error_label.grid(column=0, row=0, sticky='NSEW')

        resolve_button = ttk.Button(self.win, text='Resolve error', command=resolve_cmd)
        resolve_button.grid(column=0, row=1, sticky='NSEW')

        self.win.update_idletasks()
        self.win.minsize(200, self.win.winfo_height())

        self.win.bind('<Return>', resolve_cmd)

    def resolve_error(self, condition):

        if condition == 1:
            self.options_var1.set(Main().genres_list[randrange(1,126)])
        elif condition == 2:
            self.options_var2.set(Main().genres_list[randrange(1,126)])
        elif condition == 3:
            self.options_var1.set(Main().genres_list[randrange(1,126)])
            self.options_var2.set(Main().genres_list[randrange(1,126)])
        elif condition == 4:
            self.amount_var.set(5)
        self.win.destroy()

        print(f'Error resolved')

if __name__ == '__main__':
    root = Tk()
    App(root)
    root.mainloop()