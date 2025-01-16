import tkinter as tk
from tkinter import ttk
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

CLIENT_ID = "b3272e0aed504f49b303155aae08a637"
CLIENT_SECRET = "db60aa52e06d4d09ba5cd6f1cfd24996"
REDIRECT_URI = "http://localhost:8888/callback/"
SCOPE = "user-read-private"

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=CLIENT_ID,
                                               client_secret=CLIENT_SECRET,
                                               redirect_uri=REDIRECT_URI,
                                               scope=SCOPE))

uzytkownik = sp.current_user()
nazwa_uzytkownika = uzytkownik['display_name']

otwarte_okno = None

def pobierz_playlisty_i_utwory():
    playlisty = sp.current_user_playlists()
    informacje_playlisty = []
    for playlista in playlisty['items']:
        nazwa = playlista['name']
        id_playlisty = playlista['id']
        liczba_utworow = sp.playlist_tracks(id_playlisty)['total']
        informacje_playlisty.append((nazwa, liczba_utworow, id_playlisty))
    return informacje_playlisty

def zaladuj_utwory(id_playlisty):
    utwory = sp.playlist_tracks(id_playlisty)['items']
    for item in utwory:
        utwor = item['track']
        nazwa_utworu = utwor['name']
        id_utworu = utwor['id']
        autor = ', '.join([artysta['name'] for artysta in utwor['artists']])
        tree2.insert("", tk.END, values=(nazwa_utworu, autor, id_utworu))

def wybierz_playliste(event):
    wybrany_element = tree.selection()
    if not wybrany_element:
        return
    nazwa_playlisty = tree.item(wybrany_element)['values'][0]
    for nazwa, liczba, id_playlisty in informacje_playlisty:
        if nazwa == nazwa_playlisty:
            for item in tree2.get_children():
                tree2.delete(item)
            zaladuj_utwory(id_playlisty)
            break

def pokaz_wykres():
    wybrany_element = tree.selection()
    if not wybrany_element:
        tk.messagebox.showinfo("Błąd", "Wybierz playlistę, aby wyświetlić wykres!")
        return
    nazwa_playlisty = tree.item(wybrany_element)['values'][0]
    for nazwa, liczba, id_playlisty in informacje_playlisty:
        if nazwa == nazwa_playlisty:
            utwory = sp.playlist_tracks(id_playlisty)['items']
            nazwy_utworow = []
            popularnosci = []
            for item in utwory:
                utwor = item['track']
                nazwy_utworow.append(utwor['name'])
                popularnosci.append(utwor['popularity'])
            okno_wykresu = tk.Toplevel(glowne_okno)
            okno_wykresu.title(f"Wykres popularności - {nazwa_playlisty}")
            okno_wykresu.geometry("1920x1080")
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.barh(nazwy_utworow, popularnosci, color='skyblue')
            ax.set_xlabel('Popularność')
            ax.set_title(f"Popularność utworów - {nazwa_playlisty}")
            ax.invert_yaxis()
            canvas = FigureCanvasTkAgg(fig, okno_wykresu)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            break

glowne_okno = tk.Tk()
glowne_okno.title("Aplikacja do analizy playlist Spotify")
glowne_okno.geometry("1200x600")

etykieta = tk.Label(glowne_okno, text=f"Zalogowano jako: {nazwa_uzytkownika}", font=("Arial", 14))
etykieta.pack(pady=10)

tree = ttk.Treeview(glowne_okno, columns=("Nazwa", "Liczba utworów"), show="headings", height=30)
tree.heading("Nazwa", text="Nazwa Playlisty")
tree.heading("Liczba utworów", text="Liczba utworów")
tree.pack(side=tk.LEFT, padx=5, pady=10)

tree2 = ttk.Treeview(glowne_okno, columns=("Nazwa", "Autor", "ID"), show="headings", height=30)
tree2.heading("Nazwa", text="Nazwa Utworu")
tree2.heading("Autor", text="Autor")
tree2.heading("ID", text="ID Utworu")
tree2.pack(side=tk.RIGHT, padx=5, pady=10)

informacje_playlisty = pobierz_playlisty_i_utwory()
for nazwa, liczba, id_playlisty in informacje_playlisty:
    tree.insert("", tk.END, values=(nazwa, liczba))

tree.bind("<ButtonRelease-1>", wybierz_playliste)

przycisk_wykresu = tk.Button(glowne_okno, text="Pokaż wykres popularności", command=pokaz_wykres)
przycisk_wykresu.pack(pady=10)

glowne_okno.mainloop()
