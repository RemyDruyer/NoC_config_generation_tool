# -*- coding: utf-8 -*-
#!/usr/bin/python
#--------------------------------------------------------------
#-- FILE NAME  : SECANOC.py                                  --
#-- AUTHORS   : Adel BENSAAD, Remy DRUYER                   --
#-- DATE     : 3 décembre 2016                             --
#-- VERSION  : 1.5                                           --
#--------------------------------------------------------------

from tkinter import *
from tkinter.messagebox import *
from functools import partial
import os
import shutil
import platform
#regex
import re


# Classe Vertical Scroll
# Cree une scroll bar verticale cote droit ajustable
class VerticalScrolledFrame(Frame):
    """
    * Use the 'interior' attribute to place widgets inside the scrollable frame
    """
    def __init__(self, parent, Largeur_Frame, Hauteur_Frame, *args, **kwargs):
        Frame.__init__(self, parent, *args, **kwargs)

        # create a canvas object and a vertical scrollbar for scrolling it
        vscrollbar = Scrollbar(self, orient=VERTICAL)
        vscrollbar.pack(fill=Y, side=RIGHT, expand=FALSE)

        LabelCanvas = Canvas(self, bd=0, highlightthickness=0, width = Largeur_Frame, height = 20)
        LabelCanvas.pack(side=TOP, fill=BOTH, expand=TRUE)

        canvas = Canvas(self, bd=0, highlightthickness=0, width = Largeur_Frame, height = Hauteur_Frame, yscrollcommand=vscrollbar.set)
        canvas.pack(side=TOP, fill=BOTH, expand=TRUE)
        vscrollbar.config(command=canvas.yview)


        # reset the view
        canvas.xview_moveto(0)
        canvas.yview_moveto(0)

        # create a frame inside the canvas which will be scrolled with it
        self.Label_interior = Label_interior = Frame(LabelCanvas)
        Label_interior_id = LabelCanvas.create_window(0, 0, window=Label_interior, anchor=NW )

        self.interior = interior = Frame(canvas)
        interior_id = canvas.create_window(0, 0, window=interior, anchor=NW )

        # track changes to the canvas and frame width and sync them,
        # also updating the scrollbar
        def _configure_interior(event):
            # update the scrollbars to match the size of the inner frame
            size = (interior.winfo_reqwidth(), interior.winfo_reqheight())
            canvas.config(scrollregion="0 0 %s %s" % size)
            if interior.winfo_reqwidth() != canvas.winfo_width():
                # update the canvas's width to fit the inner frame
                canvas.config(width=interior.winfo_reqwidth())
        interior.bind('<Configure>', _configure_interior)

        def _configure_canvas(event):
            if interior.winfo_reqwidth() != canvas.winfo_width():
                # update the inner frame's width to fill the canvas
                canvas.itemconfigure(interior_id, width=canvas.winfo_width())
        canvas.bind('<Configure>', _configure_canvas)



class ScrollableTable(Frame):
    def __init__(self, *args, **kw):
        Frame.__init__(self, *args, **kw)
        self.grid()

        # barre de defilement verticale
        self.VerticalScrollBar = Scrollbar(self, orient="vertical")
        self.VerticalScrollBar.grid(row=0, column=20, sticky = N+S)
        # barre de defilement horizontale
        self.HorizontalScrollBar = Scrollbar(self, orient="horizontal")
        self.HorizontalScrollBar.grid(row=20, column=0, sticky = E+W)

        # CANVAS PRINCIPAL : contient tous les autres Canvas de la "ScrollableTable"
        # reglage de la taille du widget Scrollabable table
        self.Canvas_principal = Canvas(self, width = 1000, height = 570, highlightthickness=0)
        self.Canvas_principal.grid_propagate(False)
        self.Canvas_principal.grid(row=0, column=0)

        # CANVAS EMPTY : positionne tout en haut a gauche contient une case vide
        if platform.system() == "Linux":
            self.Canvas_empty = Canvas(self.Canvas_principal, width = 98, height = 45, highlightthickness=0)
        elif platform.system() == "Windows":
            self.Canvas_empty = Canvas(self.Canvas_principal, width = 80, height = 35, highlightthickness=0)


        self.Canvas_empty.grid(row=1, column=1, sticky=N+W)
        self.Canvas_empty.grid_propagate(False)

        # CANVAS LEFT : axe vertical de numerotation des routeurs
        #affecte par la barre de defilement verticale
        if platform.system() == "Linux":
            self.Canvas_left = Canvas(self.Canvas_principal , width = 98, height = 520, highlightthickness=0, yscrollcommand = self.VerticalScrollBar.set)
        elif platform.system() == "Windows":
            self.Canvas_left = Canvas(self.Canvas_principal , width = 80, height = 520, highlightthickness=0, yscrollcommand = self.VerticalScrollBar.set)
        self.Canvas_left.grid(row=2, column=1, sticky=NW)
        self.Canvas_left.grid_propagate(False)

        # CANVAS TOP : barre en supérieur contenant le bouton "connecté à routeur"
        #affecte par la barre de defilement horizontale
        if platform.system() == "Linux":
            self.Canvas_top = Canvas(self.Canvas_principal, width = 950, height = 45, highlightthickness=0, xscrollcommand = self.HorizontalScrollBar.set)
        elif platform.system() == "Windows":
            self.Canvas_top = Canvas(self.Canvas_principal, width = 950, height = 35, highlightthickness=0, xscrollcommand = self.HorizontalScrollBar.set)

        self.Canvas_top.grid(row=1, column=2, sticky=N+W)
        self.Canvas_top.grid_propagate(False)

        # CANVAS CENTER : damier au centre contenant les cases pour l'initialisation des connexions entre les routeurs
        #affecte par les barres de defilement verticales et horizontales
        self.Canvas_center = Canvas(self.Canvas_principal, width = 950, height = 520, highlightthickness=0, yscrollcommand = self.VerticalScrollBar.set, xscrollcommand = self.HorizontalScrollBar.set)
        self.Canvas_center.grid(row=2, column=2, sticky=N+W)
        self.Canvas_center.grid_propagate(False)

        #action des deux barres de defilement sur les CANVAS via les fonctions "_vb_yview" et "_vb_xview"
        self.VerticalScrollBar.config(command=self._vb_yview)
        self.HorizontalScrollBar.config(command=self._vb_xview)

        #declaration des frames contenant les cases -> necessaires pour le fonctinnement des barres de defilement
        self.Canvas_left_interior_Frame = Canvas_left_interior_Frame = Frame(self.Canvas_left)
        Canvas_left_interior_Frame_id = self.Canvas_left.create_window(0, 0, window=Canvas_left_interior_Frame, anchor =NW)

        self.Canvas_top_interior_Frame = Canvas_top_interior_Frame = Frame(self.Canvas_top)
        Canvas_top_interior_Frame_id = self.Canvas_top.create_window(0, 0, window=Canvas_top_interior_Frame, anchor=NW)

        self.Canvas_center_interior_Frame = Canvas_center_interior_Frame = Frame(self.Canvas_center)
        Canvas_center_interior_Frame_id = self.Canvas_center.create_window(0, 0, window=Canvas_center_interior_Frame, anchor=NW)


    ### Fonctions de defilement des Canvas
    # pour la barre de defilement verticale : Canvas_left & Canvas_center
    def _vb_yview(self, *args):
        self.Canvas_left.yview(*args)
        self.Canvas_center.yview(*args)
    # pour la barre de defilement horizontale : Canvas_top & Canvas_center
    def _vb_xview(self, *args):
        self.Canvas_top.xview(*args)
        self.Canvas_center.xview(*args)


# Creation of one class which inherit from Tkinter.Tk
class MainInterface(Frame):
    # Init
    def __init__(self, fenetre_tk, **kwargs):
        Frame.__init__(self, fenetre_tk, width=1100, height=870, **kwargs)
        self.grid()
        #axe vertial de n° du routeur
        self.liste_num_routeur_gauche = list()
        self.liste_EntryNbrMaitre = list()
        self.liste_EntryNbrEsclave = list()
        #variable de contrôles de saisie du nombre de routeurs
        self.NbrMinRouteurAutorise = 3
        self.NbrMaxRouteurAutorise = 64
        self.offset_grid_ligne = 3
        self.offset_grid_colonne = 3
        self.flag_checkbouton_moniteur_securite = 0
        self.flag_checkBouton_Connexions_Locales = 0
        self.flag_checkbouton_decodeurs_adresse =0
        self.flag_checkBouton_Connexions_Paquets = 0
        self.flag_clic_bouton_run = 0
        self.i_Cases_Connexions_Routeurs_X = 0
        self.i_Cases_Connexions_Routeurs_Y = 0
        self.liste_Cases_Connexions_Routeurs = list()
        self.nb_routeur_precedente_generation = 0
        #Paramètres fixes du NoC
        self.nbr_port_routeur_max = 16
        #Variables globales de paramètrage du NoC
        self.nbr_R = 0
        self.nbr_M_par_routeur = []
        self.nbr_S_par_routeur = []
        self.nbr_RP_par_routeur = []
        self.somme_tot_nbr_M = 0
        self.somme_tot_nbr_S = 0
        self.somme_tot_connexions_R = 0
        self.somme_tot_nbr_RP = 0
        self.master_address_decoder_range = StringVar(value=32)
        self.security_monitor_activation = IntVar(value=0)
        self.rang_nbr_M = []
        self.rang_nbr_S = []
        self.nbr_interface_routeur = []
        self.type_interface_par_routeur = []
        self.type_interface_par_routeur.append([])
        self.Connexions_locales = [[]]
        self.Connexions_paquets = [[]]
        self.IntVar_checkBouton_Connexions_Locales = IntVar()
        self.IntVar_checkBouton_Connexions_Paquets = IntVar()

        self.maitre_possede_decodage_adresse_esclave = [[[[]]]]
        self.interface_maitre_adresse_basse_decodage_esclave = [[[[]]]]
        self.interface_maitre_adresse_haute_decodage_esclave = [[[[]]]]
        self.Taille_table_decodeur_adr_maitre =[[]]
        self.Premier_routeur_du_chemin_entre_2_routeurs = [[]]
        self.flag_sauvegarde_parametre_generaux = 0
        self.precedent_nbr_M_par_routeur = []
        self.precedent_nbr_S_par_routeur = []
        self.Taille_decodeur_adr_maitre_est_de_un =[[]]
        self.offset_taille_total_decod_maitre = 0

        self.Rapport_d_erreur = ""

        # Espace Menu Barre
        # Creation de la menu barre
        self.barremenu = Menu(self)
        # Creation du menu "Fichier"
        self.fichier = Menu(self.barremenu, tearoff = 0)
        self.barremenu.add_cascade(label="Fichier", menu = self.fichier)
        self.fichier.add_command(label = "Nouveau", command=self.quit)
        self.fichier.add_command(label = "Ouvrir", command=self.quit)
        self.fichier.add_command(label = "Enregistrer", command=self.quit)
        self.fichier.add_command(label = "Enregistrer-sous", command=self.quit)
        self.fichier.add_command(label = "Fermer", command=self.quit)
        # Afficher le menu
        fenetre_tk.config(menu=self.barremenu)

        # nombre routeurs Label & Entry
        self.nbr_R = Label(self, text="Nombre de routeurs dans le réseau (entre 3 et 64) :")
        self.nbr_R.grid(row=0, column=1)
        #creation de la case d'entree "nombre de routeurs" : largeur 5, texte centre
        self.EntryNbrRouteur = Entry(self, width = 5, justify = CENTER)
        self.EntryNbrRouteur.grid(row=0, column=2)
        self.EntryNbrRouteur.insert(0,"3")

        self.Matrice_connexions_routeurs_LabelFrame = LabelFrame(self, text="Matrice de paramètrage des connexions et du nombre d'interfaces maitres/esclaves des routeurs", padx=5, pady=5)
        self.Matrice_connexions_routeurs_LabelFrame.grid(row=1, column=0, columnspan=8)

        self.Scrollable_Table = ScrollableTable(self.Matrice_connexions_routeurs_LabelFrame)
        self.Scrollable_Table.grid(row=0, column=0)


        # Bouton RUN
        self.bouton_run = Button(self, text=" Génération de la matrice de connexions des routeurs ", command=self.run_action)
        self.bouton_run.grid(row=0, column=3, sticky = W)
        # Bouton d'information
        self.bouton_info = Button(self, text=" ? ", command=self.bouton_info_action, width=2, bg = "orange")
        self.bouton_info.grid(row=0, column=5, sticky = E)
        # Encadré du bouton de sauvegarde des paramètres généraux du réseau
        self.Label_Frame_save_param = LabelFrame(self, text="Etat : sauvegarde non à jour.")
        self.Label_Frame_save_param.grid(row=2, column=2, pady=10)
        # Bouton sauvegarde des paramètres de connexions et d'interfaces
        self.bouton_save_param = Button(self.Label_Frame_save_param, text="Sauvegarde des paramètres\ngénéraux des routeurs", command=self.Bouton_sauvegarde_parametre_generaux_routeur, state=DISABLED)
        self.bouton_save_param.grid(row=0, column=0)
        # Case a cocher "Activation des moniteurs de securite"
        self.checkbouton_moniteur_securite = Checkbutton(self, text="Activation des moniteurs \n de securité", command= self.checkbouton_moniteur_securite_action, variable= self.security_monitor_activation, state=DISABLED)
        self.checkbouton_moniteur_securite.grid(row=3, column=0, sticky=NSEW)
        # Bouton - appel fenêtre secondaire "Configuration des moniteurs de securite"
        self.bouton_moniteur_securite = Button(self, text="Configuration des moniteurs \n de securité", state=DISABLED)
        self.bouton_moniteur_securite.grid(row=4, column=0, sticky=NSEW)
        # # Case a cocher "Interfaces toutes connectees en local"
        self.checkBouton_Connexions_Locales = Checkbutton(self, text="Interfaces toutes \n connectées en local", command= self.checkBouton_Connexions_Locales_action, variable = self.IntVar_checkBouton_Connexions_Locales, state=DISABLED)
        self.checkBouton_Connexions_Locales.grid(row=3, column=1, sticky=NSEW)
        # # Bouton - appel fenêtre secondaire "Configuration des connexions locales"
        self.Bouton_Connexions_Locales = Button(self, text="Configuration des \n connexions locales", command=self.FenetreSecondaire_ConnexionLocale, state=DISABLED)
        self.Bouton_Connexions_Locales.grid(row=4, column=1, sticky=NSEW)
        # # Case a cocher "Interfaces toutes connectees en paquets"
        self.checkBouton_Connexions_Paquets = Checkbutton(self, text="Interfaces toutes \n connectées en paquets", command= self.checkBouton_Connexions_Paquets_action, variable = self.IntVar_checkBouton_Connexions_Paquets, state=DISABLED)
        self.checkBouton_Connexions_Paquets.grid(row=3, column=2, sticky=NSEW)
        # # Bouton - appel fenêtre secondaire "Configuration des connexions en paquets"
        self.Bouton_Connexions_Paquets = Button(self, text="Configuration des \n connexions en paquets", command=self.FenetreSecondaire_ConnexionPaquet, state=DISABLED)
        self.Bouton_Connexions_Paquets.grid(row= 4, column=2, sticky=NSEW)
        # # Bouton - appel fenêtre secondaire "Configuration des decodeurs d'adresse"
        self.bouton_decodeurs_adresses = Button(self, text="Configuration des décodeurs \n d'adresse", command=self.FenetreSecondaire_DecodeurAdresse, state=DISABLED)
        self.bouton_decodeurs_adresses.grid(row= 4, column=3, sticky=NSEW)
        # # bouton "Generation du VHDL"
        self.bouton_generation_vhdl = Button(self, text="Génération \n du VHDL", command= self.on_buttonGenerate_clicked, state=DISABLED)
        self.bouton_generation_vhdl.grid(row= 4, column=5, sticky=NSEW)

        # self.bouton_chargement_save_exemple = Button(self, text="Chargement Save", commasnd=self.Chargement_sauvegarde_exemple)
        # self.bouton_chargement_save_exemple.grid(row=2, column=3, padx=2, pady=2)


    # Action du bouton "RUN/Generation de la matrice de connexions des routeurs"
    def run_action(self):

        def _modification_des_parametres_generaux(event):
            self.Label_Frame_save_param.config(text="Etat : sauvegarde non a jour.")

        ##fonction d'activation des cases : initialisation des connexions entre les routeurs
        #lors du clic sur un bouton, le colorer en orange ainsi que le bouton de coordonnees inverses
        #cela permet d'initialiser une connexion entre deux routeurs : par exemple clic sur le bouton 0 2 initialise aussi le bouton 2 0
        def _case_definir_connexion(event):
            #parametre generaux modifie -> maj du label frame
            _modification_des_parametres_generaux(event)
            #Récupération de toute les infos de poistionnement grid() du bouton
            info_grid_bouton=event.widget.grid_info()
            #extraction des coordonnées X Y du boutons par rapport au info grid()
            var_Coord_X_bouton = info_grid_bouton["column"]-self.offset_grid_ligne
            var_Coord_Y_bouton = info_grid_bouton["row"]-self.offset_grid_ligne

            #Coloration du bouton
            if event.widget["background"] == "orange":
                #lui rendre sa couleur initiale selon qu'il est positionne sur une ligne paire ou impair
                if var_Coord_Y_bouton % 2 == 0:
                    event.widget.config(bg="SystemButtonFace")
                else:
                    event.widget.config(bg="gainsboro")
                #rendre la couleur du bouton de coordonnees inverses
                if var_Coord_X_bouton %2 == 0:
                    self.liste_Cases_Connexions_Routeur[var_Coord_X_bouton][var_Coord_Y_bouton].config(bg="SystemButtonFace")
                else:
                    self.liste_Cases_Connexions_Routeur[var_Coord_X_bouton][var_Coord_Y_bouton].config(bg="gainsboro")
            #sinon il n'est pas colore en orange -> le colorer en orange ainsi que le bouton de coordonnees inverses
            else:
                event.widget.config(bg="orange")
                self.liste_Cases_Connexions_Routeur[var_Coord_X_bouton][var_Coord_Y_bouton].config(bg="orange")



        def _generation_grille_routeur(self):
            #initialiser le flag "bouton run cliqué"
            self.flag_clic_bouton_run = 1
            #Conversion du contenu du champ "Nombre de routeurs" en int et initialisation de "nbr_R"
            self.nbr_R = int(self.EntryNbrRouteur.get())
            #Initialisation d'un tableau a deux dimensions (nb_routeurs * nb_routeurs)
            self.liste_Cases_Connexions_Routeur = [[] for _ in range(self.nbr_R)]

            self.nbr_R = int(self.EntryNbrRouteur.get())

            #placement d'une case inactive dans le coin en haut a gauche de la matrice/damier de connexions de routeurs
            if platform.system() == "Linux":
                self.TopLeft_Corner_Case = Button(self.Scrollable_Table.Canvas_empty, text ="Routeur", borderwidth=1, height = 2, width = 9)
            elif platform.system() == "Windows":
                self.TopLeft_Corner_Case = Button(self.Scrollable_Table.Canvas_empty, text ="Routeur", borderwidth=1, height = 2, width = 10)
            self.TopLeft_Corner_Case.grid(row=1, column=1, padx=0)
            self.TopLeft_Corner_Case.grid_propagate(False)

            #Case horizontale "Connecté à routeur" dans Canvas_top_interior_frame
            ligne = 2

            if platform.system() == "Linux":
                self.Case_Label_top_matrice =  Button(self.Scrollable_Table.Canvas_top_interior_Frame, borderwidth=2, text = "Connecté à routeur", height = 1, background = "gainsboro", width = self.nbr_R ,padx = (self.nbr_R-1)*19)
            elif platform.system() == "Windows":
                self.Case_Label_top_matrice =  Button(self.Scrollable_Table.Canvas_top_interior_Frame, borderwidth=2, text = "Connecté à routeur", height = 1, background = "gainsboro", width = self.nbr_R ,padx = (self.nbr_R-1)*8)

            self.Case_Label_top_matrice.grid(row= ligne, column=self.nbr_R+self.offset_grid_colonne, sticky=N+W+S)

            #Placement des champs d'entête de saisie du nombre d'interface maître et esclave par routeurs dans Canvas_top_interior_frame
            self.Case_LabelNbrMaitre = Button(self.Scrollable_Table.Canvas_top_interior_Frame, width=20, bd=1, text="Nombre d'interfaces \n maitres du routeur")
            self.Case_LabelNbrMaitre.grid(row= 2, column=self.nbr_R+self.offset_grid_colonne+1, columnspan = 1, sticky= NE)
            self.Case_LabelNbrEsclave = Button(self.Scrollable_Table.Canvas_top_interior_Frame, width=20, bd=1, text="Nombre d'interfaces \n esclaves du routeur")
            self.Case_LabelNbrEsclave.grid(row= 2, column=self.nbr_R+self.offset_grid_colonne+2, columnspan = 1,sticky= NE)

            #Cases de numero des routeurs de l'axe vertical dans Canvas_left_interior_Frame
            self.i_num_routeur_gauche = 0
            for ligne in range (self.offset_grid_ligne,self.nbr_R+self.offset_grid_ligne):
                colonne = 2
                #si ligne pair : couleur grise claire
                if (ligne %2 ==0):
                    self.liste_num_routeur_gauche.append( Button(self.Scrollable_Table.Canvas_left_interior_Frame, text ="%s" % (ligne-3), height = 1, width = 10, background = "gainsboro", borderwidth=1, font=("Helvetica", 9)))
                #sinon case de couleur normale
                else:
                    self.liste_num_routeur_gauche.append( Button(self.Scrollable_Table.Canvas_left_interior_Frame, text ="%s" % (ligne-3), height = 1, width = 10, borderwidth=1, font=("Helvetica", 9)))

                if platform.system() == "Linux":
                    self.liste_num_routeur_gauche[self.i_num_routeur_gauche].grid(row= ligne, column=colonne,sticky=W+E+N+S)
                elif platform.system() == "Windows":
                    self.liste_num_routeur_gauche[self.i_num_routeur_gauche].grid(row= ligne, column=colonne, sticky=W+E+N+S)

                self.i_num_routeur_gauche +=1

            #Cases principales du damier
            self.i_Cases_Connexions_Routeurs_X = 0
            self.i_Cases_Connexions_Routeurs_Y = 0
            for ligne in range (self.offset_grid_ligne,self.nbr_R+self.offset_grid_ligne):
                for colonne in range (self.offset_grid_colonne,self.nbr_R+self.offset_grid_colonne):
                    # cases grises inactive pour la diagonale
                    if ligne == colonne:
                        self.liste_Cases_Connexions_Routeur[self.i_Cases_Connexions_Routeurs_Y].append( Button(self.Scrollable_Table.Canvas_center_interior_Frame, bg="grey", borderwidth=1, height = 1, width = 2))
                        self.liste_Cases_Connexions_Routeur[self.i_Cases_Connexions_Routeurs_Y][self.i_Cases_Connexions_Routeurs_X].grid(row= ligne, column=colonne, sticky=W+E+N+S)
                        self.i_Cases_Connexions_Routeurs_X +=1
                    # cases differentes de la diagonale
                    else:
                        # si ligne paire : case grise claire
                        if (ligne %2 ==0):
                            self.liste_Cases_Connexions_Routeur[self.i_Cases_Connexions_Routeurs_Y].append( Button(self.Scrollable_Table.Canvas_center_interior_Frame
                                ,text ="%s" %(self.i_Cases_Connexions_Routeurs_X), height = 1, padx = 1
                                ,background = "gainsboro", borderwidth=1, font=("Helvetica", 9)))
                        # sinon case de couleur normale ("SystemButtonFace")
                        else:
                            self.liste_Cases_Connexions_Routeur[self.i_Cases_Connexions_Routeurs_Y].append( Button(self.Scrollable_Table.Canvas_center_interior_Frame
                                ,text ="%s" %(self.i_Cases_Connexions_Routeurs_X) ,height = 1, width = 2, borderwidth=1, font=("Helvetica", 9)))
                        self.liste_Cases_Connexions_Routeur[self.i_Cases_Connexions_Routeurs_Y][self.i_Cases_Connexions_Routeurs_X].grid(row= ligne, column=colonne, sticky=W+E+N+S)
                        self.liste_Cases_Connexions_Routeur[self.i_Cases_Connexions_Routeurs_Y][self.i_Cases_Connexions_Routeurs_X].bind("<Button-1>",_case_definir_connexion)
                        self.i_Cases_Connexions_Routeurs_X +=1
                #reinitialiser X pour la prochaine ligne
                self.i_Cases_Connexions_Routeurs_X =0
                #incrementer le nombre de ligne
                self.i_Cases_Connexions_Routeurs_Y +=1

            #Champs de saisies nombre d'interface maître / nombre d'interface esclave par routeur
            self.i_EntryNbr_Maitre_Esclave = 0
            for ligne in range (self.offset_grid_ligne,self.nbr_R+self.offset_grid_ligne):
                colonne = self.nbr_R+3
                self.liste_EntryNbrMaitre.append(Entry(self.Scrollable_Table.Canvas_center_interior_Frame, justify=CENTER, width=24))
                self.liste_EntryNbrMaitre[self.i_EntryNbr_Maitre_Esclave].grid(row= ligne, column=self.nbr_R+4, sticky= NSEW)
                self.liste_EntryNbrMaitre[self.i_EntryNbr_Maitre_Esclave].bind('<KeyPress>',_modification_des_parametres_generaux)
                #valeur contenue dans la case initialisee a 0
                self.liste_EntryNbrMaitre[self.i_EntryNbr_Maitre_Esclave].insert(0,"0")
                self.liste_EntryNbrEsclave.append(Entry(self.Scrollable_Table.Canvas_center_interior_Frame, justify=CENTER, width=24))
                self.liste_EntryNbrEsclave[self.i_EntryNbr_Maitre_Esclave].grid(row= ligne, column=self.nbr_R+5, sticky= NSEW)
                self.liste_EntryNbrEsclave[self.i_EntryNbr_Maitre_Esclave].bind('<KeyPress>',_modification_des_parametres_generaux)
                #valeur contenue dans la case initialisee a 0
                self.liste_EntryNbrEsclave[self.i_EntryNbr_Maitre_Esclave].insert(0,"0")
                self.i_EntryNbr_Maitre_Esclave +=1


            #Mise a jour des zones defilables de Canvas_top, Canvas_left & Canvas_center pour le fonctionnement des barres de fonctionnement
            self.Scrollable_Table.Canvas_top_interior_Frame.update_idletasks()
            self.Scrollable_Table.Canvas_top.configure(scrollregion=self.Scrollable_Table.Canvas_top.bbox("all"))

            self.Scrollable_Table.Canvas_left_interior_Frame.update_idletasks()
            self.Scrollable_Table.Canvas_left.configure(scrollregion=self.Scrollable_Table.Canvas_left.bbox("all"))

            self.Scrollable_Table.Canvas_center_interior_Frame.update_idletasks()
            self.Scrollable_Table.Canvas_center.configure(scrollregion=self.Scrollable_Table.Canvas_center.bbox("all"))




        def _reinitialisation_grille_routeur (self):

            #case inactive dans le coin en haut a gauche de la matrice/damier de connexions de routeurs
            self.TopLeft_Corner_Case.destroy()
            #Case label "Connecte a" en haut du damier des connexions routeurs placée dans Canvas_top_interior_frame
            self.Case_Label_top_matrice.destroy()
            #Champs d'entête de saisie du nombre d'interface maître et esclave par routeurs dans Canvas_top_interior_frame
            self.Case_LabelNbrMaitre.destroy()
            self.Case_LabelNbrEsclave.destroy()

            #Cases de numero des routeurs de l'axe vertical dans Canvas_left_interior_Frame
            self.i_num_routeur_gauche = 0
            for ligne in range (self.offset_grid_ligne,self.nbr_R+self.offset_grid_ligne):
                colonne = 2
                self.liste_num_routeur_gauche[self.i_num_routeur_gauche].destroy()
                self.i_num_routeur_gauche +=1
            #réinit de la liste
            self.liste_num_routeur_gauche = list()

            #Cases principales du damier
            self.i_Cases_Connexions_Routeurs_X = 0
            self.i_Cases_Connexions_Routeurs_Y = 0
            for ligne in range (self.offset_grid_ligne,self.nbr_R+self.offset_grid_ligne):
                for colonne in range (self.offset_grid_colonne,self.nbr_R+self.offset_grid_colonne):
                    # cases grises inactive pour la diagonale
                    if ligne == colonne:
                        self.liste_Cases_Connexions_Routeur[self.i_Cases_Connexions_Routeurs_Y][self.i_Cases_Connexions_Routeurs_X].destroy()
                        self.i_Cases_Connexions_Routeurs_X +=1
                    # cases differentes de la diagonale
                    else:
                        self.liste_Cases_Connexions_Routeur[self.i_Cases_Connexions_Routeurs_Y][self.i_Cases_Connexions_Routeurs_X].destroy()
                        self.i_Cases_Connexions_Routeurs_X +=1
                #reinitialiser X pour la prochaine ligne
                self.i_Cases_Connexions_Routeurs_X =0
                #incrementer le nombre de ligne
                self.i_Cases_Connexions_Routeurs_Y +=1
            #réinit de la liste
            self.liste_Cases_Connexions_Routeur = list()


            #Champs de saisies nombre d'interface maître / nombre d'interface esclave par routeur
            self.i_EntryNbr_Maitre_Esclave = 0
            for ligne in range (self.offset_grid_ligne,self.nbr_R+self.offset_grid_ligne):
                colonne = self.nbr_R+3
                self.liste_EntryNbrMaitre[self.i_EntryNbr_Maitre_Esclave].destroy()
                self.liste_EntryNbrEsclave[self.i_EntryNbr_Maitre_Esclave].destroy()
                self.i_EntryNbr_Maitre_Esclave +=1
            #réinit des listes
            self.liste_EntryNbrMaitre = list()
            self.liste_EntryNbrEsclave = list()


            #Mise a jour des zones defilables de Canvas_top, Canvas_left & Canvas_center pour le fonctionnement des barres de fonctionnement
            self.Scrollable_Table.Canvas_top_interior_Frame.update_idletasks()
            self.Scrollable_Table.Canvas_top.configure(scrollregion=self.Scrollable_Table.Canvas_top.bbox("all"))
            self.Scrollable_Table.Canvas_left_interior_Frame.update_idletasks()
            self.Scrollable_Table.Canvas_left.configure(scrollregion=self.Scrollable_Table.Canvas_left.bbox("all"))
            self.Scrollable_Table.Canvas_center_interior_Frame.update_idletasks()
            self.Scrollable_Table.Canvas_center.configure(scrollregion=self.Scrollable_Table.Canvas_center.bbox("all"))

        ### MAIN DU BOUTON RUN ###
        # Contrôle de saisie : champ "Nombre de routeurs" non vide et contient une valeur comprise entre 3 et 64
        if self.EntryNbrRouteur.get()=="" or not  ((int(self.EntryNbrRouteur.get()) >= self.NbrMinRouteurAutorise) and (int(self.EntryNbrRouteur.get()) <= self.NbrMaxRouteurAutorise)) :
            showerror("Erreur", 'Vous devez choisir un nombre de routeurs compris entre 3 et 64' )


        #bouton run déjà cliqué & nb routeur renseigné valide : réinitialisation de tous les paramètres après confirmation
        elif (self.flag_clic_bouton_run == 1):
            #nb routeurs différent du precedent nombre de routeurs générés
            if (self.nbr_R != int(self.EntryNbrRouteur.get())):
                #message de demande de confirmation de la reinitialisation de la conf
                if askyesno("Attention : réinitialisation de toute la configuration !", "Vous souhaitez modifier le nombre de routeurs dans le réseau, cela va réinitialiser toute la configuration.\n\nEtes-vous sur ?"):
                    _reinitialisation_grille_routeur(self)
                    _generation_grille_routeur(self)

        #bouton run jamais cliqué & nb de routeur renseigné valide
        else :
            _generation_grille_routeur(self)
            self.bouton_save_param.config(state=NORMAL)



    def bouton_info_action(self):
        showinfo("Fonctionnement de l'outil", "Cet outil permet de générer les fichiers de configuration noc_config.vhd et noc_security.conf.vhd ainsi qu’un rapport d’erreur sous format texte : \n- Sélectionner le nombre de routeurs dans le réseau et le nombre d’interface maitre et esclave pour chaque routeur. \n- Dans la matrice des routeurs, chaque ligne et chaque colonne correspond à un routeur. Pour établir une connexion entre deux routeurs il suffit de cliquer sur la case à l’intersection de la ligne et de la colonne correspondant aux deux routeurs à connecter (la case réciproque est automatiquement cochée). \n- Les connexions locales définissent les interfaces maitres et esclaves pouvant communiquer ensemble au sein d’un même routeur. \n- Les connexions en paquets permettent aux interfaces maitres et esclaves n’appartenant pas au même routeur de communiquer entre elles.\n- Pour chaque maitre le décodage d’adresse définit avec quelle interface esclave il peut communiquer dans le réseau (en mode paquet ou local) et à quelle adresse il peut l’atteindre. Le décodage d’adresse pour les IP étant connectées en local est automatiquement activé. \n- Un algorithme du plus court chemin est utilisé pour initialiser le contenu des tables de routage mais il ne comprend pas une notion de « poids » qui ferait le choix entre deux chemins de taille égale en fonction de leur utilisation. Pour l’instant, c’est le premier plus court chemin entre deux routeurs qui est sélectionné.\n\n ATTENTION : modifier le nombre de routeurs ou les paramètres généraux et relancer une génération risque d’entrainer une perte des configurations déjà établies. \n\nAutres :\n- Numérotation des routeurs : de 0 a i. \n- Nombre minimal de routeur = 3 ; nombre maximale de routeur = 64. \n- Nombre maximum d’interfaces maitre et esclave confondues pour chaque routeur = 15.\n- Nombre maximum interface maitre, interface esclave et connexion a d’autre routeur pour chaque routeur = 16.\n- Ordre de numérotation des interfaces : de 0 à j : d’abord les interfaces maitre, puis interfaces esclaves et enfin les interfaces entre les routeurs (port de routage).")
    def checkbouton_moniteur_securite_action(self):
        if self.security_monitor_activation.get() == 1:
            self.bouton_moniteur_securite.config(state=NORMAL)
        else:
            self.bouton_moniteur_securite.config(state=DISABLED)

    def controle_parametre_generaux(self):
        flag_erreur_detectee = 0


        #Comptage et initialisation du nombre d'interface Maitre et Esclave par routeur
        self.nbr_M_par_routeur = [0 for i in range(self.nbr_R)]
        self.nbr_S_par_routeur = [0 for i in range(self.nbr_R)]

        for r in range(self.nbr_R):
            self.nbr_M_par_routeur[r] = int(self.liste_EntryNbrMaitre[r].get())
            self.nbr_S_par_routeur[r] = int(self.liste_EntryNbrEsclave[r].get())

        #Somme totale d'interface maître et esclave de tous les routeurs
        for r in range(self.nbr_R):
            self.somme_tot_nbr_M += self.nbr_M_par_routeur[r]
            self.somme_tot_nbr_S += self.nbr_S_par_routeur[r]

        #Nombre de port de routage par routeur et nombre total de port de routage(une connexion entre deux routeurs = 2 ports de routage -> 1 par routeur)
        #pour chaque routeur
        self.nbr_RP_par_routeur = [0 for i in range(self.nbr_R)]
        for ligne in range (self.nbr_R):
            for colonne in range (self.nbr_R):
                #on ne prend que la partie au dessus/à droite de la diagonale pour générer compter les connexions et éviter de créer des doubles
                if colonne > ligne:
                    #si la case est orange et donc qu'une connexion existe
                    if self.liste_Cases_Connexions_Routeur[ligne][colonne]["background"]=="orange":
                        #incrémentation de l'index du nombre de port de routage pour les deux routeurs de la connexion
                        self.nbr_RP_par_routeur[ligne] += 1
                        self.nbr_RP_par_routeur[colonne] += 1
                        self.somme_tot_nbr_RP += 2
                        self.somme_tot_connexions_R +=1


        #Controles
        for r in range (self.nbr_R):
            if self.nbr_M_par_routeur[r] + self.nbr_S_par_routeur[r]  > 15:
                showerror("Impossible de poursuivre", "Au moins une erreur détectée : Nombre cumulé d'interface maitre et esclave du Routeur %d est supérieur au maximum autorisé de 15" %r)
                flag_erreur_detectee = 1

            if self.nbr_M_par_routeur[r] + self.nbr_S_par_routeur[r] + self.nbr_RP_par_routeur[r] > 16:
                showerror("Impossible de poursuivre", "Au moins une erreur detectée : Nombre cumulé d'interface maitre, esclave et connexion vers d'autre routeur du Routeur %d est supérieur au maximum autorisé de 16" %r)
                flag_erreur_detectee = 1

            if flag_erreur_detectee:
                break

        if flag_erreur_detectee:
            return "erreur"
        else:
            return "Ok"

    def Bouton_sauvegarde_parametre_generaux_routeur(self):
        if askyesno("Attention", "Vous êtes sur le point de sauvegarder les paramètres généraux du réseau pour pouvoir accèder aux configurations avancées.\n\nSi vous effectuez des modifications plus tard, vous devrez effectuer à nouveau une sauvegarde pour que les changements soient pris en compte dans les configurations avances et dans ce cas vous risquez de perdre des données déjà renseignées dans vos configurations avancées.\n\nVoulez-vous continuer aux configurations avancées ?"):
            if self.controle_parametre_generaux() == "Ok":

                #mise à jour du label frame du bouton de sauvegarde des paramètres généraux
                self.Label_Frame_save_param.config(text="Etat : sauvegarde à jour")
                #permettre l'accès aux boutons de configurations avancees
                self.checkBouton_Connexions_Locales.config(state=NORMAL)
                self.Bouton_Connexions_Locales.config(state=NORMAL)
                self.checkBouton_Connexions_Paquets.config(state=NORMAL)
                self.Bouton_Connexions_Paquets.config(state=NORMAL)
                self.bouton_decodeurs_adresses.config(state=NORMAL)
                self.bouton_generation_vhdl.config(state=NORMAL)
                self.checkbouton_moniteur_securite.config(state=NORMAL)



                #Calcul du rang du premier maitre et premier esclave pour chaque routeur dans le vecteur contenant toutes les signaux d'interfaces maitre et esclave (contraintes conception VHDL)
                self.rang_nbr_M = [0 for i in range(self.nbr_R)]
                self.rang_nbr_S = [0 for i in range(self.nbr_R)]
                #variables temporaires
                var_somme_rang_nbr_M = 0
                var_somme_rang_nbr_S = 0
                for r in range(1, self.nbr_R):
                    self.rang_nbr_M[r] = self.nbr_M_par_routeur[r-1] + var_somme_rang_nbr_M
                    var_somme_rang_nbr_M += self.nbr_M_par_routeur[r-1]
                    self.rang_nbr_S[r] = self.nbr_S_par_routeur[r-1] + var_somme_rang_nbr_S
                    var_somme_rang_nbr_S += self.nbr_S_par_routeur[r-1]


                #interface paquet des ports de routages
                self.Interfaces_paquets_routeur = [[0 for port_routeur in range(self.nbr_port_routeur_max)] for r in range(self.nbr_R)]

                #3) ROUTEUR CONNEXIONS
                self.nbr_interface_routeur = [0 for i in range(self.nbr_R)]

                #4) PACKET INTERFACE
                #identifie le type d'interface paquet de chaque port de chaque routeur
                #par défaut toutes les interfaces maîtres, esclaves et port de routage possèdent une interface paquet
                #1 = maitre ; 2 = esclave ; 3 = port de routage ; 0 = aucune interface paquet
                for r in range(self.nbr_R):
                    index_interface_paquet_du_routeur = 0
                    #rajoute une interface paquet maitre = '1' pour chaque interface maitre du routeur "self.nbr_M_par_routeur[r]"
                    for m in range(self.nbr_M_par_routeur[r]):
                        self.Interfaces_paquets_routeur[r][index_interface_paquet_du_routeur] = 1
                        index_interface_paquet_du_routeur += 1

                    #rajoute une interface paquet esclave = '2' pour chaque interface esclave du routeur "self.nbr_S_par_routeur[r]"
                    for s in range(self.nbr_S_par_routeur[r]):
                        self.Interfaces_paquets_routeur[r][index_interface_paquet_du_routeur] = 2
                        index_interface_paquet_du_routeur += 1

                    #rajoute une interface paquet port de routage = '3' pour chaque connexion à un autre routeur (colonne de chaque autre autre routeur croisant celle du routeur r == "orange" -> connexion)
                    for colonne in range(self.nbr_R):
                        if self.liste_Cases_Connexions_Routeur[r][colonne]["background"]=="orange":
                            self.Interfaces_paquets_routeur[r][index_interface_paquet_du_routeur] = 3
                            index_interface_paquet_du_routeur += 1


                #Connexions paquets & locales
                self.Connexions_locales = [[[IntVar(value=1) for s in range (self.nbr_S_par_routeur[r])] for m in range (self.nbr_M_par_routeur[r])] for r in range (self.nbr_R)]
                self.Connexions_paquets = [[IntVar(value=1) for m_s in range(self.nbr_M_par_routeur[r]+self.nbr_S_par_routeur[r])] for r in range(self.nbr_R)]


                #5) ADD DECODER TABLE SIZE, 6) SLAVE ADDRESS MAPPING (32-bits), 9) ADDRESS DECODER TABLES, 10) ADDRESS DECODER PARAMETER MATRIX
                self.Taille_table_decodeur_adr_maitre = [[0 for m in range(self.nbr_M_par_routeur[r])] for r in range(self.nbr_R)]
                self.Nombre_total_regles_decodeur_adresse = 0
                self.maitre_possede_decodage_adresse_esclave = [[[[IntVar(value=0) for s in range(self.nbr_S_par_routeur[r_esclave])] for r_esclave in range(self.nbr_R)] for m in range(self.nbr_M_par_routeur[r])] for r in range(self.nbr_R)]
                self.interface_maitre_adresse_basse_decodage_esclave = [[[[StringVar(value="00000000") for s in range(self.nbr_S_par_routeur[r_esclave])] for r_esclave in range(self.nbr_R)] for m in range(self.nbr_M_par_routeur[r])] for r in range(self.nbr_R)]
                self.interface_maitre_adresse_haute_decodage_esclave = [[[[StringVar(value="00000000") for s in range(self.nbr_S_par_routeur[r_esclave])] for r_esclave in range(self.nbr_R)] for m in range(self.nbr_M_par_routeur[r])] for r in range(self.nbr_R)]

                #12) LOCAL CONNEXION
                self.Matrices_connexions_locales = [[[0 for max_maitre in range(self.nbr_port_routeur_max+1)] for max_esclave in range(self.nbr_port_routeur_max+1)] for r in range(self.nbr_R)]

            #erreur detectee dans la configuration
            else:
                #permettre l'accès aux boutons de configurations avancees
                self.checkBouton_Connexions_Locales.config(state=DISABLED)
                self.Bouton_Connexions_Locales.config(state=DISABLED)
                self.checkBouton_Connexions_Paquets.config(state=DISABLED)
                self.Bouton_Connexions_Paquets.config(state=DISABLED)
                self.bouton_decodeurs_adresses.config(state=DISABLED)
                self.bouton_generation_vhdl.config(state=DISABLED)
                self.checkbouton_moniteur_securite.config(state=DISABLED)

                # self.nbr_R


            # else:


                # Utilisés en cas de modification des paramètres généraux
                # self.precedent_nbr_M_par_routeur = [0 for i in range(self.nbr_R)]
                # self.precedent_nbr_S_par_routeur = [0 for i in range(self.nbr_R)]
                # for r in range(self.nbr_R):
                    # self.precedent_nbr_M_par_routeur[r] = int(self.liste_EntryNbrMaitre[r].get())
                    # self.precedent_nbr_S_par_routeur[r] = int(self.liste_EntryNbrEsclave[r].get()


    def Chargement_sauvegarde_exemple(self):
        CHARGED_FROM_SAVE_nbr_routeur = 4
        #chaque valeur correspond à un routeur
        CHARGED_FROM_SAVE_nbr_M_par_routeur = [4,2,3,2]
        CHARGED_FROM_SAVE_nbr_S_par_routeur = [2,2,3,0]
        #pour chaque routeur, voir s'ils sont connectés aux autres routeurs (ne peuvent être connectés à eux-même)
        CHARGED_FROM_SAVE_connexions_routeurs = [[0,1,0,1],[1,0,1,0],[0,1,0,0],[1,0,0,0]]
        #pour chaque maitre, définit si il est connecté à un esclave en local ('1' = connecté) -> [[0]] = aucune connexion dans le routeur
        CHARGED_FROM_SAVE_connexions_locales = [[[1,1],[0,0],[0,0],[1,1]], [[1,1],[0,0]], [[0,0,0],[0,0,0],[0,0,0],[0,0,0]], [[0]]]
        #pour chaque maitre et chaque esclave définit si il est connecté en interface paquet ('1' = connecté) -> [[0]] = aucune connexion dans le routeur
        CHARGED_FROM_SAVE_connexions_paquets = [[1,1,1,1,1,1],[0,0,1,1],[1,0,1,0,1,0],[0,0]]
        #un entier pour chaque maitre de chaque routeur
        CHARGED_FROM_SAVE_taille_table_decodage = [[4,2,3,5], [7,3], [1,2,3], [7,7]]

        #un entier (0 ou 1) pour chaque esclave -> chaque routeur_esclave -> chaque maitre -> de chaque routeur
        CHARGED_FROM_SAVE_decodage_esclave_actif =  [
        [ #Routeur 0
            [ #maitre0
                [ #routeur0_esclave
                    1,#esclave0
                    1 #esclave1
                ],
                [ #routeur1_esclave
                    1,#esclave0
                    1 #esclave1
                ],
                [ #routeur2_esclave
                    0, #esclave0
                    0,#esclave1
                    0 #esclave2
                ]
            ],
            [ #maitre1
                [ #routeur0_esclave
                    0,#esclave0
                    0 #esclave1
                ],
                [ #routeur1_esclave
                    1,#esclave0
                    1 #esclave1
                ],
                [ #routeur2_esclave
                    0,#esclave0
                    0,#esclave1
                    0 #esclave2
                ]
            ],
            [ #maitre2
                [ #routeur0_esclave
                    0,#esclave0
                    0 #esclave1
                ],
                [ #routeur1_esclave
                    0,#esclave0
                    0 #esclave1
                ],
                [ #routeur2_esclave
                    1,#esclave0
                    1,#esclave1
                    1 #esclave2
                ]
            ],
            [ #maitre3
                [ #routeur0_esclave
                    1,#esclave0
                    1 #esclave1
                ],
                [ #routeur1_esclave
                    0,#esclave0
                    0 #esclave1
                ],
                [ #routeur2_esclave
                    1,#esclave0
                    1,#esclave1
                    1 #esclave2
                ]
            ]
        ],
        [ #Routeur 1
            [ #maitre0
                [ #routeur0_esclave
                   1,#esclave0
                   1 #esclave1
                ],
                [ #routeur1_esclave
                   1,#esclave0
                   1 #esclave1
                ],
                [ #routeur2_esclave
                    1,#esclave0
                    1,#esclave1
                    1 #esclave2
                ]
            ],
            [ #maitre1
                [ #routeur0_esclave
                    0,#esclave0
                    0 #esclave1
                ],
                [ #routeur1_esclave
                    0,#esclave0
                    0#esclave1
                ],
                [ #routeur2_esclave
                    1,#esclave0
                    1,#esclave1
                    1 #esclave2
                ]
            ]
        ],
        [ #Routeur 2
            [ #maitre0
                [ #routeur0_esclave
                    0,#esclave0
                    1 #esclave1
                ],
                [ #routeur1_esclave
                    0,#esclave0
                    0#esclave1
                ],
                [ #routeur2_esclave
                    0,#esclave0
                    0,#esclave1
                    0 #esclave2
                ]
            ],
            [ #maitre1
                [ #routeur0_esclave
                    1,#esclave0
                    1 #esclave1
                ],
                [ #routeur1_esclave
                    0,#esclave0
                    0 #esclave1
                ],
                [ #routeur2_esclave
                    0,#esclave0
                    0,#esclave1
                    0 #esclave2
                ]
            ],
            [ #maitre2
                [ #routeur0_esclave
                    0,#esclave0
                    0 #esclave1
                ],
                [ #routeur1_esclave
                    0,#esclave0
                    0#esclave1
                ],
                [ #routeur2_esclave
                    1,#esclave0
                    1,#esclave1
                    1 #esclave2
                ]
            ]
        ],
        [ #Routeur 3

            [ #maitre0
                [ #routeur0_esclave
                    1,#esclave0
                    1 #esclave1
                ],
                [ #routeur1_esclave
                    1,#esclave0
                    1 #esclave1
                ],
                [ #routeur2_esclave
                    1,#esclave0
                    1,#esclave1
                    1 #esclave2
                ]
            ],
            [ #maitre1
                [ #routeur0_esclave
                    1,#esclave0
                    1 #esclave1
                ],
                [ #routeur1_esclave
                    1,#esclave0
                    1 #esclave1
                ],
                [ #routeur2_esclave
                    1,#esclave0
                    1,#esclave1
                    1 #esclave2
                ]
            ]
        ]]
        #une chaîne de caractère "" pour chaque esclave -> chaque routeur_esclave -> chaque maitre -> de chaque routeur
        CHARGED_FROM_SAVE_adresses_basses = [
        [ #Routeur 0
            [ #maitre0
                [ #routeur0_esclave
                    "00000000", #esclave0
                    "00000001" #esclave1
                ],
                [ #routeur1_esclave
                    "00000010", #esclave0
                    "00000011"#esclave1
                ],
                [ #routeur2_esclave
                    "00000020", #esclave0
                    "00000021", #esclave1
                    "00000022" #esclave2
                ]
            ],
            [ #maitre1
                [ #routeur0_esclave
                    "01000000", #esclave0
                    "01000001" #esclave1
                ],
                [ #routeur1_esclave
                    "01000010", #esclave0
                    "01000011"#esclave1
                ],
                [ #routeur2_esclave
                    "01000020", #esclave0
                    "01000021", #esclave1
                    "01000022" #esclave2
                ]
            ],
            [ #maitre2
                [ #routeur0_esclave
                    "02000000", #esclave0
                    "02000001" #esclave1
                ],
                [ #routeur1_esclave
                    "02000010", #esclave0
                    "02000011"#esclave1
                ],
                [ #routeur2_esclave
                    "02000020", #esclave0
                    "02000021", #esclave1
                    "02000022" #esclave2
                ]
            ],
            [ #maitre3
                [ #routeur0_esclave
                    "03000000", #esclave0
                    "03000001" #esclave1
                ],
                [ #routeur1_esclave
                    "03000010", #esclave0
                    "03000011"#esclave1
                ],
                [ #routeur2_esclave
                    "03000020", #esclave0
                    "03000021", #esclave1
                    "03000022" #esclave2
                ]
            ]
        ],
        [ #Routeur 1
            [ #maitre0
                [ #routeur0_esclave
                    "10000000", #esclave0
                    "10000001" #esclave1
                ],
                [ #routeur1_esclave
                    "10000010", #esclave0
                    "10000011"#esclave1
                ],
                [ #routeur2_esclave
                    "10000020", #esclave0
                    "10000021", #esclave1
                    "10000022" #esclave2
                ]
            ],
            [ #maitre1
                [ #routeur0_esclave
                    "11000000", #esclave0
                    "11000001" #esclave1
                ],
                [ #routeur1_esclave
                    "11000010", #esclave0
                    "11000011"#esclave1
                ],
                [ #routeur2_esclave
                    "11000020", #esclave0
                    "11000021", #esclave1
                    "11000022" #esclave2
                ]
            ]
        ],
        [ #Routeur 2
            [ #maitre0
                [ #routeur0_esclave
                    "20000000", #esclave0
                    "20000001" #esclave1
                ],
                [ #routeur1_esclave
                    "20000010", #esclave0
                    "20000011"#esclave1
                ],
                [ #routeur2_esclave
                    "20000020", #esclave0
                    "20000021", #esclave1
                    "20000022" #esclave2
                ]
            ],
            [ #maitre1
                [ #routeur0_esclave
                    "21000000", #esclave0
                    "21000001" #esclave1
                ],
                [ #routeur1_esclave
                    "21000010", #esclave0
                    "21000011"#esclave1
                ],
                [ #routeur2_esclave
                    "21000020", #esclave0
                    "21000021", #esclave1
                    "21000022" #esclave2
                ]
            ],
            [ #maitre2
                [ #routeur0_esclave
                    "22000000", #esclave0
                    "22000001" #esclave1
                ],
                [ #routeur1_esclave
                    "22000010", #esclave0
                    "22000011"#esclave1
                ],
                [ #routeur2_esclave
                    "22000020", #esclave0
                    "22000021", #esclave1
                    "22000022" #esclave2
                ]
            ]
        ],
        [ #Routeur 3

            [ #maitre0
                [ #routeur0_esclave
                    "30000000", #esclave0
                    "30000001" #esclave1
                ],
                [ #routeur1_esclave
                    "30000010", #esclave0
                    "30000011"#esclave1
                ],
                [ #routeur2_esclave
                    "30000020", #esclave0
                    "30000021", #esclave1
                    "30000022" #esclave2
                ]
            ],
            [ #maitre1
                [ #routeur0_esclave
                    "31000000", #esclave0
                    "31000001" #esclave1
                ],
                [ #routeur1_esclave
                    "31000010", #esclave0
                    "31000011"#esclave1
                ],
                [ #routeur2_esclave
                    "31000020", #esclave0
                    "31000021", #esclave1
                    "31000022" #esclave2
                ]
            ]
        ]]
        #une chaîne de carctère "" pour chaque esclave -> chaque routeur_esclave -> chaque maitre -> de chaque routeur
        CHARGED_FROM_SAVE_adresses_hautes = [
        [ #Routeur 0
            [ #maitre0
                [ #routeur0_esclave
                    "00000000", #esclave0
                    "FFFF0001" #esclave1
                ],
                [ #routeur1_esclave
                    "FFFF0010", #esclave0
                    "FFFF0011"#esclave1
                ],
                [ #routeur2_esclave
                    "FFFF0020", #esclave0
                    "FFFF0021", #esclave1
                    "FFFF0022" #esclave2
                ]
            ],
            [ #maitre1
                [ #routeur0_esclave
                    "01FFFF00", #esclave0
                    "01FFFF01" #esclave1
                ],
                [ #routeur1_esclave
                    "01FFFF10", #esclave0
                    "01FFFF11"#esclave1
                ],
                [ #routeur2_esclave
                    "01FFFF20", #esclave0
                    "01FFFF21", #esclave1
                    "01FFFF22" #esclave2
                ]
            ],
            [ #maitre2
                [ #routeur0_esclave
                    "02FFFF00", #esclave0
                    "02FFFF01" #esclave1
                ],
                [ #routeur1_esclave
                    "02FFFF10", #esclave0
                    "02FFFF11"#esclave1
                ],
                [ #routeur2_esclave
                    "02FFFF20", #esclave0
                    "02FFFF21", #esclave1
                    "02FFFF22" #esclave2
                ]
            ],
            [ #maitre3
                [ #routeur0_esclave
                    "03FFFF00", #esclave0
                    "03FFFF01" #esclave1
                ],
                [ #routeur1_esclave
                    "03FFFF10", #esclave0
                    "03FFFF11"#esclave1
                ],
                [ #routeur2_esclave
                    "03FFFF20", #esclave0
                    "03FFFF21", #esclave1
                    "03FFFF22" #esclave2
                ]
            ]
        ],
        [ #Routeur 1
            [ #maitre0
                [ #routeur0_esclave
                    "1FFFF000", #esclave0
                    "1FFFF001" #esclave1
                ],
                [ #routeur1_esclave
                    "1FFFF010", #esclave0
                    "1FFFF011"#esclave1
                ],
                [ #routeur2_esclave
                    "1FFFF020", #esclave0
                    "1FFFF021", #esclave1
                    "1FFFF022" #esclave2
                ]
            ],
            [ #maitre1
                [ #routeur0_esclave
                    "11FFFF00", #esclave0
                    "11FFFF01" #esclave1
                ],
                [ #routeur1_esclave
                    "11FFFF10", #esclave0
                    "11FFFF11"#esclave1
                ],
                [ #routeur2_esclave
                    "11FFFF20", #esclave0
                    "11FFFF21", #esclave1
                    "11FFFF22" #esclave2
                ]
            ]
        ],
        [ #Routeur 2
            [ #maitre0
                [ #routeur0_esclave
                    "2FFFF000", #esclave0
                    "2FFFF001" #esclave1
                ],
                [ #routeur1_esclave
                    "2FFFF010", #esclave0
                    "2FFFF011"#esclave1
                ],
                [ #routeur2_esclave
                    "2FFFF020", #esclave0
                    "2FFFF021", #esclave1
                    "2FFFF022" #esclave2
                ]
            ],
            [ #maitre1
                [ #routeur0_esclave
                    "21FFFF00", #esclave0
                    "21FFFF01" #esclave1
                ],
                [ #routeur1_esclave
                    "21FFFF10", #esclave0
                    "21FFFF11"#esclave1
                ],
                [ #routeur2_esclave
                    "21FFFF20", #esclave0
                    "21FFFF21", #esclave1
                    "21FFFF22" #esclave2
                ]
            ],
            [ #maitre2
                [ #routeur0_esclave
                    "22FFFF00", #esclave0
                    "22FFFF01" #esclave1
                ],
                [ #routeur1_esclave
                    "22FFFF10", #esclave0
                    "22FFFF11"#esclave1
                ],
                [ #routeur2_esclave
                    "22FFFF20", #esclave0
                    "22FFFF21", #esclave1
                    "22FFFF22" #esclave2
                ]
            ]
        ],
        [ #Routeur 3

            [ #maitre0
                [ #routeur0_esclave
                    "3FFFF000", #esclave0
                    "3FFFF001" #esclave1
                ],
                [ #routeur1_esclave
                    "3FFFF010", #esclave0
                    "3FFFF011"#esclave1
                ],
                [ #routeur2_esclave
                    "3FFFF020", #esclave0
                    "3FFFF021", #esclave1
                    "3FFFF022" #esclave2
                ]
            ],
            [ #maitre1
                [ #routeur0_esclave
                    "31FFFF00", #esclave0
                    "31FFFF01" #esclave1
                ],
                [ #routeur1_esclave
                    "31FFFF10", #esclave0
                    "31FFFF11"#esclave1
                ],
                [ #routeur2_esclave
                    "31FFFF20", #esclave0
                    "31FFFF21", #esclave1
                    "31FFFF22" #esclave2
                ]
            ]
        ]]

        #chargement du nbr de routeur
        self.EntryNbrRouteur.delete(0,END)
        self.EntryNbrRouteur.insert(0,CHARGED_FROM_SAVE_nbr_routeur)
        ##Bouton de génération de la matrice
        self.run_action()

        #chargement des connexions entre les routeurs (self.nbr_R initisalité dans run_action() donc utilisable)
        for ligne in range (self.nbr_R):
            for colonne in range (self.nbr_R):
                if CHARGED_FROM_SAVE_connexions_routeurs[ligne][colonne] == 1:
                    self.liste_Cases_Connexions_Routeur[ligne][colonne]["background"]="orange"

        #chargement du nombre d'interface/maitre esclave par routeur
        for r in range(self.nbr_R):
            self.liste_EntryNbrMaitre[r].delete(0,END)
            self.liste_EntryNbrMaitre[r].insert(0,CHARGED_FROM_SAVE_nbr_M_par_routeur[r])
            self.liste_EntryNbrEsclave[r].delete(0,END)
            self.liste_EntryNbrEsclave[r].insert(0,CHARGED_FROM_SAVE_nbr_S_par_routeur[r])

        ##Bouton sauvegarde principaux paramètres routeurs
        self.Bouton_sauvegarde_parametre_generaux_routeur()

        #chargement des connexions locales
        for r in range(self.nbr_R):
            for m in range(self.nbr_M_par_routeur[r]):
                for s in range(self.nbr_S_par_routeur[r]):
                    self.Connexions_locales[r][m][s].set(value=CHARGED_FROM_SAVE_connexions_locales[r][m][s])

        #chargement des connexions paquets
        for r in range(self.nbr_R):
            for m_s in range(self.nbr_M_par_routeur[r]+self.nbr_S_par_routeur[r]):
                self.Connexions_paquets[r][m_s].set(value=CHARGED_FROM_SAVE_connexions_paquets[r][m_s])

        #chargement des adresses basses & hautes des décodeurs ainsi que des tailles de des tables de décodage d'adresse pour chaque maître
        for r in range(self.nbr_R):
            for m in range(self.nbr_M_par_routeur[r]):
                self.Taille_table_decodeur_adr_maitre[r][m] = CHARGED_FROM_SAVE_taille_table_decodage[r][m]
                for r_esclave in range(self.nbr_R):
                    for s in range(self.nbr_S_par_routeur[r_esclave]):
                        self.interface_maitre_adresse_basse_decodage_esclave[r][m][r_esclave][s].set(value=CHARGED_FROM_SAVE_adresses_basses[r][m][r_esclave][s])
                        self.interface_maitre_adresse_haute_decodage_esclave[r][m][r_esclave][s].set(value=CHARGED_FROM_SAVE_adresses_hautes[r][m][r_esclave][s])
                        self.maitre_possede_decodage_adresse_esclave[r][m][r_esclave][s].set(CHARGED_FROM_SAVE_decodage_esclave_actif[r][m][r_esclave][s])


    def checkBouton_Connexions_Locales_action(self):
        #tout connecter
        if self.IntVar_checkBouton_Connexions_Locales.get() == 1:
            self.Bouton_Connexions_Locales.config(state = DISABLED)
            for r in range(self.nbr_R):
                for m in range(self.nbr_M_par_routeur[r]):
                    for s in range(self.nbr_S_par_routeur[r]):
                        self.Connexions_locales[r][m][s].set(value=1)
        #permettre le paramètrage
        else:
            self.Bouton_Connexions_Locales.config(state = NORMAL)


    def checkBouton_Connexions_Paquets_action(self):
        #tout connecter
        if self.IntVar_checkBouton_Connexions_Paquets.get() == 1:
            self.Bouton_Connexions_Paquets.config(state = DISABLED)
            for r in range(self.nbr_R):
                for m_s in range(self.nbr_M_par_routeur[r]+self.nbr_S_par_routeur[r]):
                    self.Connexions_paquets[r][m_s].set(value=1)
        #permettre le paramètrage
        else:
            self.Bouton_Connexions_Paquets.config(state = NORMAL)


    #Méthode pour gérer le paramètrage des connexions locales
    def FenetreSecondaire_ConnexionLocale(self):

        def _Bouton_ToutConnecter_Local_action():
            #tout connecter
            if self.flag_tout_connecter_local==0:
                for i in range(len(CheckButt_Connexions_locales)):
                    CheckButt_Connexions_locales[i].select()
                self.flag_tout_connecter_local = 1
            #tout déconnecter
            else:
                for i in range(len(CheckButt_Connexions_locales)):
                    CheckButt_Connexions_locales[i].deselect()
                self.flag_tout_connecter_local = 0

        def _Bouton_Ok_action():
            #initialisation de l'activation du décodage d'adresse (pour chaque maitre) pour esclaves connectés en local au maitre
            for r in range (self.nbr_R):
                for m in range (self.nbr_M_par_routeur[r]):
                    for s in range (self.nbr_S_par_routeur[r]):
                        if self.Connexions_locales[r][m][s].get() == 1:
                            self.maitre_possede_decodage_adresse_esclave[r][m][r][s].set(value=1)

            #maj du nombre de regle de décodage d'adresse par routeur/maitre
            for r in range (self.nbr_R):
                for m in range (self.nbr_M_par_routeur[r]):
                    self.Taille_table_decodeur_adr_maitre[r][m] = 0
                    for r_esclave in range (self.nbr_R):
                        for s in range (self.nbr_S_par_routeur[r_esclave]):
                             if self.maitre_possede_decodage_adresse_esclave[r][m][r_esclave][s].get() == 1:
                                self.Taille_table_decodeur_adr_maitre[r][m] += 1


            #maj du nombre de total de regle de decodage d'adresse
            self.Nombre_total_regles_decodeur_adresse = 0
            for r in range (self.nbr_R):
                for m in range (self.nbr_M_par_routeur[r]):
                    self.Nombre_total_regles_decodeur_adresse += self.Taille_table_decodeur_adr_maitre[r][m]


            #fermeture de la fenêtre pop-up
            Fenetre_ConnexionLocale.destroy()

        def _on_buttonsave_clicked():
            print("Configuration des connexions locales")
            self.quit()

        #Main méthode : FenetreSecondaire_ConnexionLocale #
        #popup
        Fenetre_ConnexionLocale = Toplevel(fenetre_tk)
        #Frame avec une barre verticale de défilement dans le popup
        self.frame = VerticalScrolledFrame(Fenetre_ConnexionLocale, Largeur_Frame=200, Hauteur_Frame=500)
        self.frame.grid(row=0, column=0,sticky=N)

        Cases_Routeurs                  = []
        Cases_Maitres                   = []
        Cases_Esclaves                  = []
        CheckButt_Connexions_locales    = []
        Scrollable_Label_Colon          = []
        Scrollable_Label_Arrow          = []

        self.flag_tout_connecter_local  = 1
        Label_Routeurs  = Label(self.frame.Label_interior, text="Routeur", width=7, justify = CENTER).grid(row=0, column=0)
        Label_Empty_1   = Label(self.frame.Label_interior, text=" ", width=2, justify = CENTER).grid(row=0, column=1)
        Label_Maitres   = Label(self.frame.Label_interior, text="Maitre", width=8, justify = CENTER).grid(row=0, column=2)
        Label_Empty_2   = Label(self.frame.Label_interior, text=" ", width=8, justify = CENTER).grid(row=0, column=3)
        Label_Esclaves  = Label(self.frame.Label_interior, text="Esclave", width=5, justify = CENTER).grid(row=0, column=4)
        Label_Connexions_locales = Label(self.frame.Label_interior, text="Connexion", width=10, justify = CENTER).grid(row=0, column=5)

        #Placement des cases pour Maitre X(fois) Esclave pour chaque routeur
        for r in range(self.nbr_R):
            for m in range(self.nbr_M_par_routeur[r]):
                for s in range(self.nbr_S_par_routeur[r]):
                    Cases_Routeurs.append(Button(self.frame.interior, text= str(r), state=DISABLED, width=7))
                    Cases_Maitres.append(Button(self.frame.interior, text= str(m), state=DISABLED, width=7))
                    Cases_Esclaves.append(Button(self.frame.interior, text= str(s+self.nbr_M_par_routeur[r]), state=DISABLED, width=7))
                    CheckButt_Connexions_locales.append(Checkbutton(self.frame.interior, variable=self.Connexions_locales[r][m][s], width=5))
                    Scrollable_Label_Arrow.append(Label(self.frame.interior, text="<=>", width=7, justify = CENTER))
                    Scrollable_Label_Colon.append(Label(self.frame.interior, text=":", width=2, justify = CENTER))


        for i in range(len(Cases_Routeurs)):
            Cases_Routeurs[i].grid(row=i, column=0)
            Scrollable_Label_Colon[i].grid(row=i, column=1)
            Cases_Maitres[i].grid(row=i, column=2)
            Scrollable_Label_Arrow[i].grid(row=i, column=3)
            Cases_Esclaves[i].grid(row=i, column=4)
            CheckButt_Connexions_locales[i].grid(row=i, column=5)

        Button(Fenetre_ConnexionLocale, text="Tout connecter/deconnecter", width=22, command=_Bouton_ToutConnecter_Local_action).grid(row=1, column=0, pady=5)
        Button(Fenetre_ConnexionLocale, text="Ok", width=22, command=_Bouton_Ok_action).grid(row=2, column=0, pady=5)


    #methode pour gerer la fenêtre des connexions en paquets
    def FenetreSecondaire_ConnexionPaquet(self):

        def _Bouton_ToutConnecter_Paquet_action():

            #tout connecter
            if self.flag_bouton_tout_connecter_paquet==1:
                for i in range(len(CheckButt_Connexions_paquet_maitre)):
                    CheckButt_Connexions_paquet_maitre[i].select()
                for i in range(len(CheckButt_Connexions_paquet_esclave)):
                    CheckButt_Connexions_paquet_esclave[i].select()
                self.flag_bouton_tout_connecter_paquet=0

            #tout déconnecter
            else:
                for i in range(len(CheckButt_Connexions_paquet_maitre)):
                    CheckButt_Connexions_paquet_maitre[i].deselect()
                for i in range(len(CheckButt_Connexions_paquet_esclave)):
                    CheckButt_Connexions_paquet_esclave[i].deselect()
                self.flag_bouton_tout_connecter_paquet=1


        # Main méthode : FenetreSecondaire_ConnexionPaquet #
        Fenetre_ConnexionPaquet = Toplevel(fenetre_tk)
        self.frame = VerticalScrolledFrame(Fenetre_ConnexionPaquet, Largeur_Frame=200, Hauteur_Frame=500)
        self.frame.grid(row=0, column=0, sticky=N)

        Cases_num_routeur_co_maitre                    = []
        Cases_num_routeur_co_esclave                   = []
        Cases_maitres_connexion_paquet                 = []
        Cases_esclaves_connexion_paquet                = []
        CheckButt_Connexions_paquet_maitre             = []
        CheckButt_Connexions_paquet_esclave            = []
        self.flag_bouton_tout_connecter_paquet  = 1


        #déclaration & positionnement des labels dans "Label_interior" de la "VerticalScrolledFrame"
        Label_Routeur_co_maitre = Label(self.frame.Label_interior, text="Routeur", width=7, justify = CENTER).grid(row=0, column=0)
        Label_Routeur_co_esclave = Label(self.frame.Label_interior, text="Routeur", width=8, justify = CENTER).grid(row=0, column=3)
        Label_Interface_maitre = Label(self.frame.Label_interior, text="Interface", width=7, justify = CENTER).grid(row=0, column=1)
        Label_Interface_esclave = Label(self.frame.Label_interior, text="Interface", width=8, justify = CENTER).grid(row=0, column=4)
        Label_Connexion_co_maitre = Label(self.frame.Label_interior, text="Connexion paquet", width=15, justify = CENTER).grid(row=0, column=2)
        Label_Connexion_co_esclave = Label(self.frame.Label_interior, text="Connexion paquet", width=15, justify = CENTER).grid(row=0, column=5)

       #déclaration des cases maitres
        for r in range(self.nbr_R):
            for m in range(self.nbr_M_par_routeur[r]):
                Cases_num_routeur_co_maitre.append(Button(self.frame.interior, text=str(r), state=DISABLED, width=7))
                Cases_maitres_connexion_paquet.append(Button(self.frame.interior, text=str(m)+" (Maitre)", state=DISABLED, width=8))
                CheckButt_Connexions_paquet_maitre.append(Checkbutton(self.frame.interior, variable=self.Connexions_paquets[r][m], width = 10))
        #déclaration des cases esclaves
        for r in range(self.nbr_R):
            for s in range(self.nbr_M_par_routeur[r],self.nbr_M_par_routeur[r]+self.nbr_S_par_routeur[r]):
                Cases_num_routeur_co_esclave.append(Button(self.frame.interior, text=str(r), state=DISABLED, width=7))
                Cases_esclaves_connexion_paquet.append(Button(self.frame.interior, text=str(s)+" (Esclave)", state=DISABLED, width=8))
                CheckButt_Connexions_paquet_esclave.append(Checkbutton(self.frame.interior, variable=self.Connexions_paquets[r][s], width=10))



        #affichage cases maitres
        for i in range(len(Cases_maitres_connexion_paquet)):
            Cases_num_routeur_co_maitre[i]  .grid(row=i, column=0)
            Cases_maitres_connexion_paquet[i]   .grid(row=i, column=1)
            CheckButt_Connexions_paquet_maitre[i].grid(row=i, column=2)
        #affichage cases esclaves
        for i in range(len(Cases_maitres_connexion_paquet),len(Cases_maitres_connexion_paquet)+len(Cases_esclaves_connexion_paquet)):
            Cases_num_routeur_co_esclave[i-len(Cases_maitres_connexion_paquet)].grid(row=i-len(Cases_maitres_connexion_paquet), column=3)
            Cases_esclaves_connexion_paquet[i-len(Cases_maitres_connexion_paquet)].grid(row=i-len(Cases_maitres_connexion_paquet), column=4)
            CheckButt_Connexions_paquet_esclave[i-len(Cases_maitres_connexion_paquet)].grid(row=i-len(Cases_maitres_connexion_paquet), column=5)

        Button(Fenetre_ConnexionPaquet, text="Tout connecter/deconnecter", width=22, command= _Bouton_ToutConnecter_Paquet_action, pady=5).grid(row=2, column=0)
        Button(Fenetre_ConnexionPaquet, text="Ok", width=22, command=lambda:Fenetre_ConnexionPaquet.destroy(), pady=5).grid(row=3, column=0)


    #Méthode pour gerer la fenêtre secondaire de configuration des decodeurs d'adresses
    def FenetreSecondaire_DecodeurAdresse(self):

        def _reinit_decodeur_adresse():
            if askyesno("Demande de confirmation", "Voulez-vous totalement réinitialiser la configuration des décodeurs d'adresse ?"):

                for r in range (self.nbr_R):
                    for m in range (self.nbr_M_par_routeur[r]):
                        for r_esclave in range (self.nbr_R):
                            for s in range (self.nbr_S_par_routeur[r_esclave]):
                                self.maitre_possede_decodage_adresse_esclave[r][m][r_esclave][s].set(value=0)
                                self.interface_maitre_adresse_basse_decodage_esclave[r][m][r_esclave][s].set(value="")
                                self.interface_maitre_adresse_haute_decodage_esclave[r][m][r_esclave][s].set(value="")

                for r in range (self.nbr_R):
                    for m in range (self.nbr_M_par_routeur[r]):
                        self.Taille_table_decodeur_adr_maitre[r][m] = 0

                self.Nombre_total_regles_decodeur_adresse = 0



        #recherche du rang du n° du routeur contenant premier maitre dans la configuration (le n° du premier maitre est forcement 0)
        i_routeur_premier_maitre = 0
        flag_presence_maitre = 0
        for r in range (self.nbr_R):
            for m in range (self.nbr_M_par_routeur[r]):
                i_routeur_premier_maitre = r
                flag_presence_maitre = 1
                break
            if flag_presence_maitre == 1:
                break
        #si aucun maitre dans le réseau => erreur
        if  flag_presence_maitre == 0 :
            showerror("Erreur", "Aucune interface maitre n'est spécifiée dans la configuration." )
        #sinon : ouvrir la fenêtre
        else:

            # Main méthode : FenetreSecondaire_DecodeurAdresse #
            Fenetre_DecodeurAdresse = Toplevel(fenetre_tk)
            #encadré en haut à gauche
            Taille_Table_Label_Frame = LabelFrame(Fenetre_DecodeurAdresse)
            Taille_Table_Label_Frame.grid(row=0,column=1)
            #variable de type StringVar contenant le texte du label "Label_taille_table_adr_decod_maitre" contenu dans "Taille_Table_Label_Frame"
            self.StringVar_Label_Taille_Table_Decodeur_Adresse_Maitre = StringVar(value = "Taille de la table du décodeur d'adresse : Routeur %d Maitre 0 = %d" %(i_routeur_premier_maitre,self.Taille_table_decodeur_adr_maitre[i_routeur_premier_maitre][0]))
            #déclaration de l'étiquette "Label_taille_table_adr_decod_maitre" et placement dans "Taille_Table_Label_Frame"
            self.Label_taille_table_adr_decod_maitre = Label(Taille_Table_Label_Frame, justify = CENTER, textvariable = self.StringVar_Label_Taille_Table_Decodeur_Adresse_Maitre).grid(row=0,column=0, sticky = N+S+E+W)

            #variable de type StringVar contenant le texte du label "Label_taille_table_adr_decod_maitre" contenu dans "Taille_Table_Label_Frame"
            self.StringVar_Label_Total_Taille_Table_Decodeur_Adresse_Maitre = StringVar(value = "Taille totale des tables de décodage d'adresses cumulées = %d" %(self.Nombre_total_regles_decodeur_adresse))
            #déclaration de l'étiquette "Label_taille_table_adr_decod_maitre" et placement dans "Taille_Table_Label_Frame"
            self.Label_Total_taille_table_adr_decod_maitre = Label(Fenetre_DecodeurAdresse, justify = CENTER, underline =1, textvariable = self.StringVar_Label_Total_Taille_Table_Decodeur_Adresse_Maitre).grid(row=1,column=1, sticky = N+S+E+W)

            Bouton_reinitialisation_decod_adr = Button(Fenetre_DecodeurAdresse, text = "Réinit.\ndecodeur adresse", command = _reinit_decodeur_adresse)
            Bouton_reinitialisation_decod_adr.grid(row=0, column=0, sticky = N+S)


            #déclaration d'un encadré avec une barre de défilement
            self.frame = VerticalScrolledFrame(Fenetre_DecodeurAdresse, Largeur_Frame=350, Hauteur_Frame=500)
            self.frame.grid(row=2,column=1)

            #liste de sélection contenant tous les maitres du réseau
            Listbox_maitres = Listbox(Fenetre_DecodeurAdresse)
            Listbox_maitres.grid(row=2,column=0, sticky = N+S)
            #initialisation des items de la listbox des maitres
            items_Listbox_Maitres =[]
            for r in range (self.nbr_R):
                for m in range (self.nbr_M_par_routeur[r]):
                    items_Listbox_Maitres.append("Routeur %d - Maitre %d" %(r,m))
            #chargement de la listebox des maitres
            for index in range(len(items_Listbox_Maitres)):
                Listbox_maitres.insert(END, items_Listbox_Maitres[index])

            #déclaration des listes contenant les widgets
            Cases_Routeurs = []
            Cases_Esclaves = []
            Cases_Adresse_basse = []
            Cases_Adresse_haute = []
            CheckButt_decodage_esclave = []
            #labels placés dans la partie "Label_interior" de la "VerticalScrolledFrame" qui n'est pas affectée par la barre de défilement
            Label_Routeur = Label(self.frame.Label_interior, text="Routeur", width=9, justify=CENTER).grid(row=0, column=0)
            Label_Esclave = Label(self.frame.Label_interior, text="Esclave", width=8, justify=CENTER).grid(row=0, column=1)
            Label_Adresse_basse = Label(self.frame.Label_interior, text="Adresse basse (Hex)", width=17, justify=CENTER).grid(row=0, column=2)
            Label_Adresse_haute = Label(self.frame.Label_interior, text="Adresse haute (Hex)", width=17, justify=CENTER).grid(row=0, column=3)
            Label_Communication_Avec_Esclave = Label(self.frame.Label_interior, text="Communication avec l'esclave", justify=CENTER).grid(row=0, column=4)

            #déclaration et placement des cases pour chaque esclaves du réseau dans la "VerticalScrolledFrame"
            i_grid_row = 0
            for r in range(self.nbr_R):
                for s in range(self.nbr_S_par_routeur[r]):
                    #ajout des widgets dans leurs listes respectives
                    Cases_Routeurs.append(Button(self.frame.interior, text=str(r), state=DISABLED, width=8))
                    Cases_Esclaves.append(Button(self.frame.interior, text=str(self.nbr_M_par_routeur[r]+s), state=DISABLED, width=8))
                    Cases_Adresse_basse.append(Entry(self.frame.interior, justify = CENTER, width=20, textvariable = self.interface_maitre_adresse_basse_decodage_esclave[i_routeur_premier_maitre][0][r][s]))
                    Cases_Adresse_haute.append(Entry(self.frame.interior, justify = CENTER, width=20, textvariable = self.interface_maitre_adresse_haute_decodage_esclave[i_routeur_premier_maitre][0][r][s]))
                    CheckButt_decodage_esclave.append(Checkbutton(self.frame.interior, width = 20, variable = self.maitre_possede_decodage_adresse_esclave[i_routeur_premier_maitre][0][r][s]))
                    #placement des widgets sur la grille de "self.frame.interior"
                    Cases_Routeurs[i_grid_row].grid(row=i_grid_row, column=0, padx=1)
                    Cases_Esclaves[i_grid_row].grid(row=i_grid_row, column=1, padx=1)
                    Cases_Adresse_basse[i_grid_row].grid(row=i_grid_row, column=2)
                    Cases_Adresse_haute[i_grid_row].grid(row=i_grid_row, column=3)
                    CheckButt_decodage_esclave[i_grid_row].grid(row=i_grid_row, column=4)
                    #incrémentation du n° de ligne
                    i_grid_row += 1

            #mise à jour des valeurs liées au "précédent maitre sélectionné"
            self.i_routeur_precedent_maitre_selectionne = i_routeur_premier_maitre
            #valeur d'initialisation à 0 car le premier maitre d'un routeur se situe forcement au rang 0
            self.i_precedent_maitre_selectionne = 0


            #met à jour l'état de d'activation des champs de saisies en fonction de l'état actuel des checkbutt (donné par l'attribut "self.maitre_possede_decodage_adresse_esclave")
            i_grid_row = 0
            for r in range(self.nbr_R):
                for s in range(self.nbr_S_par_routeur[r]):
                    if self.maitre_possede_decodage_adresse_esclave[self.i_routeur_precedent_maitre_selectionne][self.i_precedent_maitre_selectionne][r][s].get() == 1:
                        Cases_Adresse_basse[i_grid_row].configure(state = NORMAL)
                        Cases_Adresse_haute[i_grid_row].configure(state = NORMAL)
                    else:
                        Cases_Adresse_basse[i_grid_row].configure(state = DISABLED)
                        Cases_Adresse_haute[i_grid_row].configure(state = DISABLED)
                    i_grid_row += 1



            Label(Fenetre_DecodeurAdresse, text="Taille de la plage de\ndecodage d'adresse (en bits)").grid(row=3, column=0)
            Entry(Fenetre_DecodeurAdresse, textvariable = self.master_address_decoder_range, width = 5, justify = CENTER).grid(row=4, column=0)

            #Bouton pour quitter la fenêtre
            Button(Fenetre_DecodeurAdresse, text="Ok", width=12, command=lambda:Fenetre_DecodeurAdresse.destroy()).grid(row=4, column=1)


            ##Fonction appelée lors du clic d'une case cochable (checkbutton) ayant pour but :
            #- d'activer ou désactiver la modification des champs d'adresses de décodage esclave (haut & bas)
            #- d'incrémenter ou décrementer la taille de la table décodage d'adresse pour le maitre en question
            #(taille de la table = nombre d'adresse de décodage d'esclave que possède le maitre = nombre de case cochée)
            def _cochage_checkbutt_decodage_esclave(event):

                infos_grid_du_widget = event.widget.grid_info()
                ligne_de_la_case_cliquee = infos_grid_du_widget["row"]

                #à partir "ligne_de_la_case_cliquee" on retrouve le rangs du routeur et de l'esclave auxquels la ligne est associée
                i_grid_row = 0
                flag_rang_trouve = 0
                for r in range(self.nbr_R):
                    for s in range(self.nbr_S_par_routeur[r]):
                        if i_grid_row == ligne_de_la_case_cliquee:
                            flag_rang_trouve = 1
                            # on récupère l'index du routeur et de l'esclave pour la case cliquée
                            i_routeur_de_la_case = r
                            i_esclave_de_la_case = s
                            break # on sort de la boucle
                        i_grid_row += 1
                    if flag_rang_trouve == 1 :
                        break # on sort de la boucle

                #grâce au rang récupéré on peut lire l'état de "cochage" du checkbutton surlequel l'utilisateur a cliqué dans "self.maitre_possede_decodage_adresse_esclave" -> IntVar() lié à chaque checkbutton
                #/!\ l'évènement <Button-1> qui appelle cette fonction se déclenche avant que la valeur d'IntVar "self.maitre_possede_decodage_adresse_esclave" liée au Checkbutton et contenant son état de "cochage" soit mis à jour /!\
                #/!\ donc sa valeur est inversée lors de la vérification /!\ -> 0 = coché ; 1 = décoché
                #si le checkbutton cliqué est coché -> permettre de modifier les adresse de décodages pour l'esclave correspondant (state=NORMAL)
                #sinon -> griser les champs de saisies d'adresse de décodage (state=DISABLED)
                if self.maitre_possede_decodage_adresse_esclave[self.i_routeur_precedent_maitre_selectionne][self.i_precedent_maitre_selectionne][i_routeur_de_la_case][i_esclave_de_la_case].get() == 0:
                    self.Taille_table_decodeur_adr_maitre[self.i_routeur_precedent_maitre_selectionne][self.i_precedent_maitre_selectionne] += 1
                    Cases_Adresse_basse[ligne_de_la_case_cliquee].configure(state = NORMAL)
                    Cases_Adresse_haute[ligne_de_la_case_cliquee].configure(state = NORMAL)
                else:
                    self.Taille_table_decodeur_adr_maitre[self.i_routeur_precedent_maitre_selectionne][self.i_precedent_maitre_selectionne] -= 1
                    Cases_Adresse_basse[ligne_de_la_case_cliquee].configure(state = DISABLED)
                    Cases_Adresse_haute[ligne_de_la_case_cliquee].configure(state = DISABLED)

                #mise à jour du label affichant la taille de la table de décodage d'adresse pour le maitre sélectionné (taille = nombre de case cochée pour le mettre en question)
                self.StringVar_Label_Taille_Table_Decodeur_Adresse_Maitre.set(value="Taille de la table du décodeur d'adresse : Routeur %d Maitre %d = %d" %(self.i_routeur_precedent_maitre_selectionne,self.i_precedent_maitre_selectionne,self.Taille_table_decodeur_adr_maitre[self.i_routeur_precedent_maitre_selectionne][self.i_precedent_maitre_selectionne]))

               #calcul somme nombre total de regles des décodeurs d'adresses et mise à jour du label associé
                self.Nombre_total_regles_decodeur_adresse = 0
                for r in range (self.nbr_R):
                    for m in range (self.nbr_M_par_routeur[r]):
                        self.Nombre_total_regles_decodeur_adresse += self.Taille_table_decodeur_adr_maitre[r][m]
                self.StringVar_Label_Total_Taille_Table_Decodeur_Adresse_Maitre.set(value = "Taille totale des decodeurs d'adresse cumules = %d" %(self.Nombre_total_regles_decodeur_adresse))

            #liaison de toutes les cases à cocher avec la fonction commande "_cochage_checkbutt_decodage_esclave"
            for c in range (len(CheckButt_decodage_esclave)):
                CheckButt_decodage_esclave[c].bind('<Button-1>', _cochage_checkbutt_decodage_esclave)


            ##Fonction appelée lors de la sélection d'un maitre dans la liste de sélection des maitres
            # -> efface les champs de saisie "adresse haute" & "adresse basse" du précédent maitre utilisés pour chaque esclave
            # -> les remplace par des champs liés au maître sélectionné
            def _selection_maitre_listbox(event):

                #récupération du texte de la ligne sélectionnée dans le widget
                contenu_ligne_selectionnee = event.widget.get(event.widget.curselection(),event.widget.curselection())
                #utilisation d'un regex pour extraire les numéro de routeur et maitre de la ligne (conversion du contenu de la ligne en String pour utilisation du regex)
                entier_extrait_regex = re.findall(r'\d+', str(contenu_ligne_selectionnee))
                #le numéro du routeur est le premier entier à apparaître, le numéro du maitre le deuxième
                i_routeur_selectionne = int(entier_extrait_regex[0])
                i_maitre_selectionne = int(entier_extrait_regex[1])

                #Mise à jour du contenu du Label "taille table de décodage d'adresse du maitre
                self.StringVar_Label_Taille_Table_Decodeur_Adresse_Maitre.set(value="Taille de la table du decodeur d'adresse : Routeur %d Maitre %d = %d" %(i_routeur_selectionne,i_maitre_selectionne,self.Taille_table_decodeur_adr_maitre[i_routeur_selectionne][i_maitre_selectionne]))

                #Calcul somme nombre total de regles des décodeurs d'adresses et mise à jour du label associé
                self.Nombre_total_regles_decodeur_adresse = 0
                for r in range (self.nbr_R):
                    for m in range (self.nbr_M_par_routeur[r]):
                        self.Nombre_total_regles_decodeur_adresse += self.Taille_table_decodeur_adr_maitre[r][m]
                self.StringVar_Label_Total_Taille_Table_Decodeur_Adresse_Maitre.set(value = "Taille totale des decodeurs d'adresse cumules = %d" %(self.Nombre_total_regles_decodeur_adresse))

                #destruction des cases précédentes
                i_grid_row = 0
                for r in range(self.nbr_R):
                    for s in range(self.nbr_S_par_routeur[r]):
                        Cases_Adresse_basse[i_grid_row].destroy()
                        Cases_Adresse_haute[i_grid_row].destroy()
                        CheckButt_decodage_esclave[i_grid_row].destroy()
                        i_grid_row += 1

                #placement des nouvelles cases
                i_grid_row = 0
                for r in range(self.nbr_R):
                    for s in range(self.nbr_S_par_routeur[r]):
                        Cases_Adresse_basse[i_grid_row] = Entry(self.frame.interior, justify = CENTER, width=20, textvariable = self.interface_maitre_adresse_basse_decodage_esclave[i_routeur_selectionne][i_maitre_selectionne][r][s])
                        Cases_Adresse_haute[i_grid_row] = Entry(self.frame.interior, justify = CENTER, width=20, textvariable = self.interface_maitre_adresse_haute_decodage_esclave[i_routeur_selectionne][i_maitre_selectionne][r][s])
                        CheckButt_decodage_esclave[i_grid_row] = Checkbutton(self.frame.interior, width = 20, variable = self.maitre_possede_decodage_adresse_esclave[i_routeur_selectionne][i_maitre_selectionne][r][s])
                        Cases_Adresse_basse[i_grid_row].grid(row=i_grid_row, column=2)
                        Cases_Adresse_haute[i_grid_row].grid(row=i_grid_row, column=3)
                        CheckButt_decodage_esclave[i_grid_row].grid(row=i_grid_row, column=4, sticky = E+W)
                        i_grid_row += 1


                #liaison de toutes les cases à cocher avec la fonction commande "_cochage_checkbutt_decodage_esclave"
                for c in range (len(CheckButt_decodage_esclave)):
                    CheckButt_decodage_esclave[c].bind('<Button-1>', _cochage_checkbutt_decodage_esclave)

                #mise à jour du "précédent maitre sélectionné à partir des rangs du maitre sélectionné
                self.i_routeur_precedent_maitre_selectionne = i_routeur_selectionne
                self.i_precedent_maitre_selectionne = i_maitre_selectionne

                #met à jour l'état de d'activation des champs de saisies en fonction de l'état actuel des checkbutt (donné par l'attribut "self.maitre_possede_decodage_adresse_esclave")
                i_grid_row = 0
                for r in range(self.nbr_R):
                    for s in range(self.nbr_S_par_routeur[r]):
                        if self.maitre_possede_decodage_adresse_esclave[self.i_routeur_precedent_maitre_selectionne][self.i_precedent_maitre_selectionne][r][s].get() == 1:
                            Cases_Adresse_basse[i_grid_row].configure(state = NORMAL)
                            Cases_Adresse_haute[i_grid_row].configure(state = NORMAL)
                        else:
                            Cases_Adresse_basse[i_grid_row].configure(state = DISABLED)
                            Cases_Adresse_haute[i_grid_row].configure(state = DISABLED)
                        i_grid_row += 1



            #lie la selection d'un item dans la listbox à l'appel d'une fonction
            #doit être appelé après la déclaration de la fonction liée
            Listbox_maitres.bind('<<ListboxSelect>>', _selection_maitre_listbox)


    # Action bouton Generation code VHDL
    def on_buttonGenerate_clicked(self):
        print("Generate the NOC files")
        self.generate_vhdl_file()


    # Generation VHDL : ----- GLOBAL CONSTANTS -----
    def generate_configurable_part_0(self):
        outputdir = "./Noc0__"
        if not os.path.exists(outputdir):
            os.makedirs(outputdir)



        ch='''
--------------------------------------------------------------
-- IP   	: noc_config PACKAGE              				--
-- AUTHOR 	: R.Druyer                              		--
-- DATE   	:  8 novembre 2016                           	--
-- VERSION	: 1.6                                   		--
--------------------------------------------------------------


library IEEE;
use IEEE.std_logic_1164.all;
use ieee.numeric_std.all;
use ieee.math_real.log2;
use ieee.math_real.ceil;

package noc_config is

----------------------------------------------------------------
				----- GLOBAL CONSTANTS  -----
----------------------------------------------------------------
'''
        #generation du code VHDL dans un fichier specifique
        fw= open(outputdir + "/noc_config_configurable_part_0.vhd", 'w')
        fw.write("%s" %ch)
        fw.write('constant TOTAL_MASTER_NB          : integer := %d ;\n' %self.somme_tot_nbr_M)
        fw.write('constant TOTAL_SLAVE_NB           : integer := %d ;\n' %self.somme_tot_nbr_S)
        fw.write('constant TOTAL_ROUTER_CONNEXIONS  : integer := %d ;\n' %self.somme_tot_connexions_R)
        fw.write('constant TOTAL_ROUTING_PORT_NB    : integer := %d ;\n' %self.somme_tot_nbr_RP)
        fw.write('constant TOTAL_ROUTER_NB          : integer := %d ;\n' %self.nbr_R)
        fw.write('constant SECURITY_MONITOR_ACTIVATION : integer := %d ;\n' %self.security_monitor_activation.get())
        fw.write('constant MASTER_ADDRESS_DECODER_RANGE	: integer := %s;\n' %self.master_address_decoder_range.get())

        fw.close()



    def generate_fixed_part(self):
        outputdir = "./Noc0__"
        if not os.path.exists(outputdir):
            os.makedirs(outputdir)


        ch='''
----------------------------------------------------------------
						----- FIXED PART -----
----------------------------------------------------------------
-- INTEGER --
constant	DATA_WIDTH						: integer := 32; 	--(in bits)
constant	ADD_SIZE   							: integer := 32; 	--(in bits)
constant	PORT_ADD_SIZE 						: integer := 4; 	--(in bits)
constant	ROUTER_ADD_SIZE 					: integer := 6; 	--(in bits)
constant	NOC_ADD_SIZE   						: integer := PORT_ADD_SIZE + ROUTER_ADD_SIZE; --(in bits)
constant	BYTEENABLE_SIZE					: integer := 4;	--(in 4-bits)
constant	REQSIZE_VECTOR_SIZE				: integer := 8;	--(define the size of the std_logic_vector of REQSIZE) example : if REQSIZE_VECTOR_SIZE = 8 -> REQSIZE can count 2^REQSIZE_VECTOR_SIZE = 256 bytes
constant 	MAX_PORT_NB_BY_ROUTER			: integer := 16;
constant	PACKET_PAYLOAD_MAXIMUM_FLITSIZE	: integer := 8; 						--(in 32 bits words)
constant 	MAX_REQSIZE_in_byte					: integer := PACKET_PAYLOAD_MAXIMUM_FLITSIZE*4; 	--(in 32 bits words)
constant 	MASTER_ADDRESS_DECODER_RANGE	: integer := 32;

-- FIFO ALTERA --
constant 	ROUTING_PORT_FIFO_DATA_DEPTH	: integer := 8;
constant 	ROUTING_PORT_FIFO_ADDR_WIDTH	: integer := 3; -- = log2(FIFO_ALTERA_DATA_DEPTH)

-- constant FIFO_ALTERA_DATA_DEPTH	: integer := 16;
-- constant FIFO_ALTERA_ADDR_WIDTH	: integer := 4; -- = log2(FIFO_ALTERA_DATA_DEPTH)

-- constant FIFO_ALTERA_DATA_DEPTH	: integer := 256;
-- constant FIFO_ALTERA_ADDR_WIDTH	: integer := 8; -- = log2(FIFO_ALTERA_DATA_DEPTH)

---- FIFO DEPTH MUST BE AT LEAST EQUAL TO MAXIMUM PACKET PAYLOAD SIZE + 1 AND MUST BE POWER OF 2
constant	ACK_PACKETIZER_FIFO_DEPTH 		: integer := 16;
-- packetizer address width must be a log2 of PACKETIZER_FIFO_DEPTH
constant	ACK_PACKETIZER_FIFO_ADDR_WIDTH 	: integer := 4;

-- SUBTYPE --
subtype 	regADD			is std_logic_vector((ADD_SIZE-1) downto 0);
subtype 	regPORTADD 	is std_logic_vector((PORT_ADD_SIZE-1) downto 0);
subtype 	regROUTERADD 	is std_logic_vector((ROUTER_ADD_SIZE-1) downto 0);
subtype 	regNOCADD 		is std_logic_vector((NOC_ADD_SIZE-1) downto 0);
subtype 	regDATA 		is std_logic_vector((DATA_WIDTH-1) downto 0);
subtype 	regBYTEENAB 	is std_logic_vector((BYTEENABLE_SIZE-1) downto 0);
subtype 	regREQSIZE 		is std_logic_vector((REQSIZE_VECTOR_SIZE-1) downto 0);
subtype 	reg32 			is std_logic_vector(31 downto 0);

-- REG CONSTANT --
constant	reg_PACKET_PAYLOAD_MAX_FLITSIZE 	: regREQSIZE := std_logic_vector(to_unsigned(PACKET_PAYLOAD_MAXIMUM_FLITSIZE,8));
constant	reg_PACKET_PAYLOAD_MAX_BYTESIZE 	: regREQSIZE := std_logic_vector(to_unsigned(PACKET_PAYLOAD_MAXIMUM_FLITSIZE*4,8));

-- SIZE ARRAY --
type 	arrayADD			is array(natural RANGE <>) of regADD;
type 	arrayPORTADD 		is array(natural RANGE <>) of regPORTADD;
type 	arrayROUTERADD 	is array(natural RANGE <>) of regROUTERADD;
type 	arrayNOCADD 		is array(natural RANGE <>) of regNOCADD;
type 	arrayDATA 			is array(natural RANGE <>) of regDATA;
type 	arrayBYTEENAB 		is array(natural RANGE <>) of regBYTEENAB;
type 	arrayREQSIZE 		is array(natural RANGE <>) of regREQSIZE;
type 	array32				is array(natural RANGE <>) of reg32;


-- RECORD --
type record_master_interface_address_decode_routing_table is record
	SLAVE_BASE_ADD 					: regADD;
	SLAVE_HIGH_ADD					: regADD;
	LOCAL_PORT_DESTINATION_ADD 		: regPORTADD;
	PACKET_DESTINATION_ADD 			: regNOCADD;
end record;

type record_routing_table is record
	ROUTER_DESTINATION_ADD			: regROUTERADD;
	LOCAL_PORT_DESTINATION_ADD 		: regPORTADD;
end record;

type record_master_routport_slave_nb_by_router is record
	MASTER_NB						: integer;
	SLAVE_NB						: integer;
	ROUTING_PORT_NB					: integer;
end record;

type record_router_connexion is record
	SOURCE_ROUTER					: integer;
	SOURCE_ROUTING_PORT				: integer;
	DESTINATION_ROUTER				: integer;
	DESTINATION_ROUTING_PORT		: integer;
end record;

type record_packet_master is record
	REQ_PM							: std_logic;
	DOUT_PM							: regDATA;
	ACK_PM							: std_logic;
end record;

type record_packet_slave is record
	REQ_PS							: std_logic;
	DIN_PS							: regDATA;
	ACK_PS							: std_logic;
end record;

type record_decod_add_parameter is record
	MASTER_TABLE_RANK_NB			: integer;
	MASTER_DECOD_TABLE_SIZE			: integer;
end record;

-- ARRAY --

--Routing table
type routing_table_array is array (0 to TOTAL_ROUTER_NB-2) of record_routing_table;
type array_all_routing_tables is array (0 to TOTAL_ROUTER_NB-1) of routing_table_array;
--Master and slave numbers by router
type array_all_record_master_routport_slave_nb_by_router is array (0 to TOTAL_ROUTER_NB-1) of record_master_routport_slave_nb_by_router;
--Packet interface port address
type packet_interface_portadd_vector is array (0 to 15) of integer;
type array_all_router_packet_interface_portadd is array (0 to TOTAL_ROUTER_NB-1) of packet_interface_portadd_vector;

--Router connexions
type array_all_router_connexion is array (0 to TOTAL_ROUTER_CONNEXIONS-1) of record_router_connexion;
--Routing ports by router
type vector_all_router_routing_port_nb is array (0 to TOTAL_ROUTER_NB-1) of integer;

--RANK (indicates the rank of master and slave into the general vector)
type master_rank_in_vector is array (0 to TOTAL_ROUTER_NB-1) of integer;
type slave_rank_in_vector is array (0 to TOTAL_ROUTER_NB-1) of integer;

--Master packet interfaces
type array_ROUTING_PORT_REQ_PM is array (0 to TOTAL_ROUTER_NB-1) of std_logic_vector(0 to 15);
type array_ROUTING_PORT_DOUT_PM is array (0 to TOTAL_ROUTER_NB-1) of arrayDATA(0 to 15);
type array_ROUTING_PORT_ACK_PM is array (0 to TOTAL_ROUTER_NB-1) of std_logic_vector(0 to 15);
--Slave packet interfaces
type array_ROUTING_PORT_REQ_PS is array (0 to TOTAL_ROUTER_NB-1) of std_logic_vector(0 to 15);
type array_ROUTING_PORT_DIN_PS is array (0 to TOTAL_ROUTER_NB-1) of arrayDATA(0 to 15);
type array_ROUTING_PORT_ACK_PS is array (0 to TOTAL_ROUTER_NB-1) of std_logic_vector(0 to 15);

-- local matrix
type integer_vector is array (0 to 16) of integer;
type local_connexion_matrix is array (0 to 16) of integer_vector;
type array_all_local_connexion_matrix is array (0 to TOTAL_ROUTER_NB-1) of local_connexion_matrix;

--decoding address table matrix
type vector_add_decoder_parameter is array (0 to 14) of record_decod_add_parameter;
type matrix_add_decoder_parameter is array (0 to TOTAL_ROUTER_NB-1) of vector_add_decoder_parameter;


-- ROUTER, MASTER and SLAVE ADDRESSES (in bits) --
constant ROUTER0 	: regROUTERADD:= "000000";
constant ROUTER1 	: regROUTERADD:= "000001";
constant ROUTER2 	: regROUTERADD:= "000010";
constant ROUTER3 	: regROUTERADD:= "000011";
constant ROUTER4 	: regROUTERADD:= "000100";
constant ROUTER5 	: regROUTERADD:= "000101";
constant ROUTER6 	: regROUTERADD:= "000110";
constant ROUTER7 	: regROUTERADD:= "000111";
constant ROUTER8 	: regROUTERADD:= "001000";
constant ROUTER9 	: regROUTERADD:= "001001";

constant ROUTER10 	: regROUTERADD:= "001010";
constant ROUTER11 	: regROUTERADD:= "001011";
constant ROUTER12 	: regROUTERADD:= "001100";
constant ROUTER13 	: regROUTERADD:= "001101";
constant ROUTER14 	: regROUTERADD:= "001110";
constant ROUTER15 	: regROUTERADD:= "001111";
constant ROUTER16 	: regROUTERADD:= "010000";
constant ROUTER17 	: regROUTERADD:= "010001";
constant ROUTER18 	: regROUTERADD:= "010010";
constant ROUTER19 	: regROUTERADD:= "010011";

constant ROUTER20 	: regROUTERADD:= "010100";
constant ROUTER21 	: regROUTERADD:= "010101";
constant ROUTER22 	: regROUTERADD:= "010110";
constant ROUTER23 	: regROUTERADD:= "010111";
constant ROUTER24 	: regROUTERADD:= "011000";
constant ROUTER25 	: regROUTERADD:= "011001";
constant ROUTER26 	: regROUTERADD:= "011010";
constant ROUTER27 	: regROUTERADD:= "011011";
constant ROUTER28 	: regROUTERADD:= "011100";
constant ROUTER29 	: regROUTERADD:= "011101";

constant ROUTER30 	: regROUTERADD:= "011110";
constant ROUTER31 	: regROUTERADD:= "011111";
constant ROUTER32 	: regROUTERADD:= "100000";
constant ROUTER33 	: regROUTERADD:= "100001";
constant ROUTER34 	: regROUTERADD:= "100010";
constant ROUTER35 	: regROUTERADD:= "100011";
constant ROUTER36 	: regROUTERADD:= "100100";
constant ROUTER37 	: regROUTERADD:= "100101";
constant ROUTER38 	: regROUTERADD:= "100110";
constant ROUTER39 	: regROUTERADD:= "100111";

constant ROUTER40	: regROUTERADD:= "101000";
constant ROUTER41	: regROUTERADD:= "101001";
constant ROUTER42	: regROUTERADD:= "101010";
constant ROUTER43	: regROUTERADD:= "101011";
constant ROUTER44	: regROUTERADD:= "101100";
constant ROUTER45	: regROUTERADD:= "101101";
constant ROUTER46	: regROUTERADD:= "101110";
constant ROUTER47	: regROUTERADD:= "101111";
constant ROUTER48	: regROUTERADD:= "110000";
constant ROUTER49	: regROUTERADD:= "110001";

constant ROUTER50 	: regROUTERADD:= "110010";
constant ROUTER51 	: regROUTERADD:= "110011";
constant ROUTER52 	: regROUTERADD:= "110100";
constant ROUTER53 	: regROUTERADD:= "110101";
constant ROUTER54 	: regROUTERADD:= "110110";
constant ROUTER55 	: regROUTERADD:= "110111";
constant ROUTER56 	: regROUTERADD:= "111000";
constant ROUTER57 	: regROUTERADD:= "111001";
constant ROUTER58 	: regROUTERADD:= "111010";
constant ROUTER59 	: regROUTERADD:= "111011";

constant ROUTER60 	: regROUTERADD:= "111100";
constant ROUTER61 	: regROUTERADD:= "111101";
constant ROUTER62 	: regROUTERADD:= "111110";
constant ROUTER63 	: regROUTERADD:= "111111";

constant MASTER0 	: regPORTADD:= "0000";
constant MASTER1 	: regPORTADD:= "0001";
constant MASTER2 	: regPORTADD:= "0010";
constant MASTER3 	: regPORTADD:= "0011";
constant MASTER4 	: regPORTADD:= "0100";
constant MASTER5 	: regPORTADD:= "0101";
constant MASTER6 	: regPORTADD:= "0110";
constant MASTER7 	: regPORTADD:= "0111";
constant MASTER8 	: regPORTADD:= "1000";
constant MASTER9 	: regPORTADD:= "1001";
constant MASTER10	: regPORTADD:= "1010";
constant MASTER11	: regPORTADD:= "1011";
constant MASTER12	: regPORTADD:= "1100";
constant MASTER13	: regPORTADD:= "1101";
constant MASTER14	: regPORTADD:= "1110";
constant MASTER15	: regPORTADD:= "1111";

constant SLAVE0 	: regPORTADD:= "0000";
constant SLAVE1 	: regPORTADD:= "0001";
constant SLAVE2 	: regPORTADD:= "0010";
constant SLAVE3 	: regPORTADD:= "0011";
constant SLAVE4 	: regPORTADD:= "0100";
constant SLAVE5 	: regPORTADD:= "0101";
constant SLAVE6 	: regPORTADD:= "0110";
constant SLAVE7 	: regPORTADD:= "0111";
constant SLAVE8 	: regPORTADD:= "1000";
constant SLAVE9 	: regPORTADD:= "1001";
constant SLAVE10 	: regPORTADD:= "1010";
constant SLAVE11 	: regPORTADD:= "1011";
constant SLAVE12 	: regPORTADD:= "1100";
constant SLAVE13 	: regPORTADD:= "1101";
constant SLAVE14 	: regPORTADD:= "1110";
constant SLAVE15 	: regPORTADD:= "1111";

constant ROUTINGPORT0 	: regPORTADD:= "0000";
constant ROUTINGPORT1 	: regPORTADD:= "0001";
constant ROUTINGPORT2 	: regPORTADD:= "0010";
constant ROUTINGPORT3 	: regPORTADD:= "0011";
constant ROUTINGPORT4 	: regPORTADD:= "0100";
constant ROUTINGPORT5 	: regPORTADD:= "0101";
constant ROUTINGPORT6 	: regPORTADD:= "0110";
constant ROUTINGPORT7 	: regPORTADD:= "0111";
constant ROUTINGPORT8 	: regPORTADD:= "1000";
constant ROUTINGPORT9 	: regPORTADD:= "1001";
constant ROUTINGPORT10 	: regPORTADD:= "1010";
constant ROUTINGPORT11 	: regPORTADD:= "1011";
constant ROUTINGPORT12 	: regPORTADD:= "1100";
constant ROUTINGPORT13 	: regPORTADD:= "1101";
constant ROUTINGPORT14 	: regPORTADD:= "1110";
constant ROUTINGPORT15 	: regPORTADD:= "1111";
'''
        fw= open(outputdir + "/noc_config_fixed_part.vhd", 'w')
        fw.write("%s" %ch)
        fw.close()

    #Génération VHDL : ------ 1) MASTER, SLAVE and ROUTING PORT NUMBERS by ROUTER ------
    def generate_configurable_part_1(self):
        outputdir = "./Noc0__"
        if not os.path.exists(outputdir):
            os.makedirs(outputdir)


        ch='''
----------------------------------------------------------------
				 ----- CONFIGURABLE PART  -----
----------------------------------------------------------------

------ 1) MASTER, SLAVE and ROUTING PORT NUMBERS by ROUTER ------
--for each router, declare the number of master interface port(s), slave interface port(s) and routing port(s)'''

        fw= open(outputdir + "/noc_config_configurable_part_1.vhd", 'w')
        fw.write("%s" %ch)
        fw.write("\n")
        for r in range (self.nbr_R):
            fw.write("constant R%d_MASTER_SLAVE_ROUTPORT_NB : record_master_routport_slave_nb_by_router :=(%d,%d,%d);\n" %(r, self.nbr_M_par_routeur[r], self.nbr_S_par_routeur[r], self.nbr_RP_par_routeur[r]))
        fw.write("\n -- => AGGREGATING ARRAY <= --\n")
        fw.write("--aggregate all the 'Ri_MASTER_SLAVE_ROUTPORT_NB' in this array\n")
        fw.write(" constant ALL_ROUTER_MASTER_SLAVE_ROUTPORT_NB : array_all_record_master_routport_slave_nb_by_router:=(\n")
        for r in range (self.nbr_R-1):
            fw.write("      R%d_MASTER_SLAVE_ROUTPORT_NB,\n" %r)

        fw.write("      R%d_MASTER_SLAVE_ROUTPORT_NB\n" %(self.nbr_R-1))
        fw.write(" );\n")

        fw.close()


    #Génération VHDL : ------ 2) MASTER and SLAVE RANKS ------
    def generate_configurable_part_2(self):
        outputdir = "./Noc0__"

        ch='''
------ 2) MASTER and SLAVE RANKS ------
--a vector composed of all the masters and a vector composed of all the slaves are used to assignate
--the master and slave interface signals to each router. These ranks are used to indicate at which location
--are situated the first master interface and the slave interface of each router in the vectors containing all master
--signals and all slave signals.
--These 2 variables must have a value for each router:
-- a) The first value is always '0'
-- b) If the current router does not have any MASTER/SLAVE the value must be '0' (MASTER for MASTER_RANK and SLAVE for SLAVE_RANK)
-- c) The value for the next router is equal to the current value plus the number of MASTER/SLAVE in the current router (cumulated sum of all the precedent MASTER/SLAVE)'''

        fw= open(outputdir + "/noc_config_configurable_part_2.vhd", 'w')
        fw.write("%s" %ch)
        fw.write("\nconstant MASTER_RANK : master_rank_in_vector := (")
        for r in range(self.nbr_R-1):
            fw.write("%d," %self.rang_nbr_M[r])
        fw.write("%d);" %self.rang_nbr_M[self.nbr_R-1])

        fw.write("\nconstant SLAVE_RANK : slave_rank_in_vector := (")
        for r in range(self.nbr_R-1):
            fw.write("%d," %self.rang_nbr_S[r])
        fw.write("%d);" %self.rang_nbr_S[self.nbr_R-1])
        fw.write("\n\n")
        fw.close()



    # Génération VHDL : ------ 3) ROUTER CONNEXIONS (topology)------
    def generate_configurable_part_3(self):
        outputdir = "./Noc0__"
        if not os.path.exists(outputdir):
            os.makedirs(outputdir)


        ch='''
------ 3) ROUTER CONNEXIONS (topology)------
--define a record for each connexion between routers
--when two routers are connected : only one ROUTER_CONNEXION constant must be defined
--4 values to define for each connexion:
-- 1) SOURCE_ROUTER
-- 2) SOURCE_ROUTING_PORT
-- 3) DESTINATION_ROUTER
-- 4) DESTINATION_ROUTING_PORT'''

        fw= open(outputdir + "/noc_config_configurable_part_3.vhd", 'w')
        fw.write("%s" %ch)
        fw.write("\n")
        #index du nombre total de connexion entre les routeurs

        #comptage de toutes les interfaces maitre & esclaves de chaque routeur
        for r in range (self.nbr_R):
            self.nbr_interface_routeur[r] = self.nbr_M_par_routeur[r] + self.nbr_S_par_routeur[r]

        i_num_connexion = 0
        #pour chaque routeur
        for ligne in range (self.nbr_R):
            for colonne in range (self.nbr_R):
                #on ne prend que la partie au dessus/à droite de la diagonale pour générer compter les connexions et éviter de créer des doubles
                if colonne > ligne:
                    #si la case est orange et donc qu'une connexion existe
                    if self.liste_Cases_Connexions_Routeur[ligne][colonne]["background"]=="orange":
                        #ecrire la connexion correspondante avec comme paramètre dans l'ordre : 1) N° de la connexion courante (en partant de 0) ; 2) Adresse du routeur en Y ; 3) Adresse du port de routage du routeur en Y ; 4) Adresse du routeur en X ; 5) N° du port de routage du routeur en X
                        fw.write("constant ROUTER_CONNEXION_%d : record_router_connexion :=(%d,%d,%d,%d);" %(i_num_connexion, ligne, self.nbr_interface_routeur[ligne] , colonne, self.nbr_interface_routeur[colonne]))
                        fw.write("\n")
                        #incrémentation de l'index du nombre de connexion
                        i_num_connexion += 1
                        #incrémentation de l'index du prochain port de routage potentiel utilisé dans une connexion pour le routeur source et le routeur destination de la connexion venant d'être écrite
                        self.nbr_interface_routeur[ligne] += 1
                        self.nbr_interface_routeur[colonne] += 1

        #écriture du tableau d'aggregation des connexions routeurs
        fw.write("\n-- => AGGREGATING ARRAY <= --\n")
        fw.write("constant ALL_ROUTER_CONNEXIONS : array_all_router_connexion:=(\n")
        #ecriture de toutes les ROUTER_CONNEXION jusqu'à l'avant dernière avec une virgule à la fin
        for i in range (i_num_connexion-1):
            fw.write("      ROUTER_CONNEXION_%d,\n" %i)
        #ecriture de la dernière ROUTER_CONNEXION sans virgule à la fin
        fw.write("      ROUTER_CONNEXION_%d\n" % (i_num_connexion-1))
        fw.write(");\n")
        fw.close()


    # Génération VHDL : ------ 4) PACKET INTERFACE DECLARATION ------
    def generate_configurable_part_4(self):
        outputdir = "./Noc0__"

        ch='''
------ 4) PACKET INTERFACE DECLARATION ------
--define a Ri_PACKET_INTERFACE_PORT_ADD constant for each router.
--this constants have a value for each port of the router (0 to 15).
--the value tells if the current router port have a packet interface and which type is it.
--There is four different choices for each router port:
-- '0': no packet interface
-- '1': master packet interface
-- '2': slave packet interface
-- '3': routing port interface
--The first value correspond to "PORT0" of the router, second value to "PORT1" of the ROUTER, etc ...
'''

        fw= open(outputdir + "/noc_config_configurable_part_4.vhd", 'w')
        fw.write("%s" %ch)
        fw.write("\n")

        for r in range(self.nbr_R):
            for m in range(self.nbr_M_par_routeur[r]):
                if self.Connexions_paquets[r][m].get() ==1 :
                    self.Interfaces_paquets_routeur[r][m] = 1
                else:
                    self.Interfaces_paquets_routeur[r][m] = 0

            for s in range(self.nbr_M_par_routeur[r],self.nbr_S_par_routeur[r]+self.nbr_M_par_routeur[r]):
                if self.Connexions_paquets[r][s].get() == 1:
                    self.Interfaces_paquets_routeur[r][s] = 2
                else:
                    self.Interfaces_paquets_routeur[r][s] = 0

        for r in range (self.nbr_R):
            fw.write("constant R%d_PACKET_INTERFACE_PORT_ADD : packet_interface_portadd_vector := (" %r)
            for p in range (self.nbr_port_routeur_max):
                if (p==self.nbr_port_routeur_max-1):
                    fw.write("%d);\n" %self.Interfaces_paquets_routeur[r][p])
                else:
                    fw.write("%d," %self.Interfaces_paquets_routeur[r][p])


        fw.write("\n-- => AGGREGATING ARRAY <= --\n")
        fw.write("constant ALL_ROUTER_PACKET_INTERFACE_PORT_ADD : array_all_router_packet_interface_portadd:=(\n")
        for r in range (self.nbr_R):
            if (r==self.nbr_R-1):
                fw.write("	    R%d_PACKET_INTERFACE_PORT_ADD\n" %r)
            else:
                fw.write("	    R%d_PACKET_INTERFACE_PORT_ADD,\n" %r)
        fw.write(");\n")
        fw.close()


    # Génération VHDL : ------ 5) ADDRESS DECODER TABLE SIZES  ------
    def generate_configurable_part_5(self):
        outputdir = "./Noc0__"

        ch='''
------ 5) ADDRESS DECODER TABLE SIZES  ------
--define the size of each address decoding table of each master of each router (in the number of rules that it contain)
'''

        self.Taille_decodeur_adr_maitre_est_de_un = [[0 for m in range (self.nbr_M_par_routeur[r])] for r in range (self.nbr_R)]

        fw= open(outputdir + "/noc_config_configurable_part_5.vhd", 'w')
        fw.write("%s" %ch)
        for r in range (self.nbr_R):
            for m in range (self.nbr_M_par_routeur[r]):
                if self.Taille_table_decodeur_adr_maitre[r][m] != 1:
                    self.Taille_decodeur_adr_maitre_est_de_un[r][m] = 0
                    fw.write("constant ROUTER%d_MASTER%d_ADD_DECOD_TABLE_SIZE 	: integer := %d;\n" %(r,m,self.Taille_table_decodeur_adr_maitre[r][m]))
                    if (m==self.nbr_M_par_routeur[r]-1):
                        fw.write("\n")
                #cas particulier : la table de décodage d'adresse n'est composée d'une seule règle, sauf qu'en vhdl on ne peut avoir des array à une entrée -> donc on duplique la dernière règle pour en avoir 2 dans la table
                else:
                    self.Taille_decodeur_adr_maitre_est_de_un[r][m] = 1
                    fw.write("constant ROUTER%d_MASTER%d_ADD_DECOD_TABLE_SIZE 	: integer := %d;\n" %(r,m,self.Taille_table_decodeur_adr_maitre[r][m]+1))
                    if (m==self.nbr_M_par_routeur[r]-1):
                        fw.write("\n")


        fw.write(" --define the total number of address decoding rules (for all the masters)\n")
        fw.write("constant TOTAL_ADDRESS_DECOD_SIZE 				: integer := %d;\n\n" % self.Nombre_total_regles_decodeur_adresse)

        fw.close()


    # Génération VHDL : ------ 6) SLAVE ADDRESS MAPPING (32-bits) ------
    def generate_configurable_part_6(self):
        outputdir = "./Noc0__"

        ch='''
------ 6) SLAVE ADDRESS MAPPING (32-bits) ------
--This address mapping is used inside the address decoding tables.
--for each master of each router, define the address mapping of slave interfaces that can be reached by the master
--for each slave -> define a BASE_ADD and a HIGH_ADD
'''

        fw= open(outputdir + "/noc_config_configurable_part_6.vhd", 'w')
        fw.write("%s" %ch)

        for r in range(self.nbr_R):
            for m in range(self.nbr_M_par_routeur[r]):
                for r_esclave in range(self.nbr_R):
                    for s in range(self.nbr_S_par_routeur[r_esclave]):
                        if self.maitre_possede_decodage_adresse_esclave[r][m][r_esclave][s].get() == 1:
                            fw.write("""constant 	ROUTER%d_MASTER%d_address_mapping_for_ROUTER%d_SLAVE%d_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"%s";\n""" %(r, m, r_esclave, s+self.nbr_M_par_routeur[r_esclave], self.interface_maitre_adresse_basse_decodage_esclave[r][m][r_esclave][s].get()))
                            fw.write("""constant 	ROUTER%d_MASTER%d_address_mapping_for_ROUTER%d_SLAVE%d_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"%s";\n""" %(r, m, r_esclave, s+self.nbr_M_par_routeur[r_esclave], self.interface_maitre_adresse_haute_decodage_esclave[r][m][r_esclave][s].get()))

        fw.close()


 # Génération VHDL : ---- 7) ROUTING TABLE CONTENTS ------
    def generate_configurable_part_7(self):
        outputdir = "./Noc0__"
        if not os.path.exists(outputdir):
            os.makedirs(outputdir)

        ch='''
---- 7) ROUTING TABLE CONTENTS ------
--define the address port that must take a packet to reach the DESTINATION ROUTER FROM the current ROUTER
--for each router a port address must be defined to reach all the other routers of the network
'''
        #Création d'une liste pour chaque routeur contenant tous les routeurs avec lesquels il est directement connecté
        Routeurs_directement_connectes = [[] for r in range (self.nbr_R)]
        for Routeur_ligne in range (self.nbr_R):
            for Routeur_colonne in range (self.nbr_R):
                # #si la case est orange et donc qu'une connexion existe
                if self.liste_Cases_Connexions_Routeur[Routeur_ligne][Routeur_colonne]["background"]=="orange":
                    Routeurs_directement_connectes[Routeur_ligne].append(Routeur_colonne)


        #Création d'un graph de type dictionnaire
        graph = dict()
        #initialisation du graph dictionnaire -> à partir de "Routeurs_directement_connectes"
        #format exemple : Routeur0 [1,2] ; Routeur1 [0,3], Routeur2 [0], Router3 [1]
        for r in range (self.nbr_R):
            graph["Routeur" + str(r)] = []
            for r_connectes in range (len(Routeurs_directement_connectes[r])):
                   graph["Routeur" + str(r)].append("Routeur" + str(Routeurs_directement_connectes[r][r_connectes]))

        #fonction de recherche du plus court chemin
        def find_shortest_path(graph, start, end, path=[]):
            path = path + [start]
            if start == end:
                return path
            if start not in graph:
                return None
            shortest = None
            for node in graph[start]:
                if node not in path:
                    newpath = find_shortest_path(graph, node, end, path)
                    if newpath:
                        if not shortest or len(newpath) < len(shortest):
                            shortest = newpath
            return shortest


        #Initialisation de l'objet "self.Premier_routeur_du_chemin_entre_2_routeurs" avec la valeur du premier routeur traversé dans le plus court chemin entre chaque paire de routeur du réseau
        self.Premier_routeur_du_chemin_entre_2_routeurs = [["" for r in range (self.nbr_R)] for r in range (self.nbr_R)]
        for Routeur_source in range (self.nbr_R):
            for Routeur_destination in range (self.nbr_R):
                if Routeur_source != Routeur_destination:
                    if find_shortest_path(graph, 'Routeur' + str(Routeur_source), 'Routeur' + str(Routeur_destination)) != None:
                        self.Premier_routeur_du_chemin_entre_2_routeurs[Routeur_source][Routeur_destination] = find_shortest_path(graph, 'Routeur' + str(Routeur_source), 'Routeur' + str(Routeur_destination))[1]
                    else:
                        self.Rapport_d_erreur += ("\nAucun chemin trouvé menant du Routeur " + str(Routeur_source) + " au Routeur" + str(Routeur_destination) + ".")


        #Comptage de toutes les interfaces maitre & esclaves de chaque routeur
        for r in range (self.nbr_R):
            self.nbr_interface_routeur[r] = self.nbr_M_par_routeur[r] + self.nbr_S_par_routeur[r]

        #pour chaque routeur
        for ligne in range (self.nbr_R):
            for colonne in range (self.nbr_R):
                #si la case est orange et donc qu'une connexion existe
                if self.liste_Cases_Connexions_Routeur[ligne][colonne]["background"]=="orange":
                    for index_r in range (self.nbr_R):
                        #pour chaque routeur destination dans "Premier_routeur_du_chemin_entre_2_routeurs" le remplacer le port de routage correspondant
                        if self.Premier_routeur_du_chemin_entre_2_routeurs[ligne][index_r] == "Routeur" + str(colonne):
                            self.Premier_routeur_du_chemin_entre_2_routeurs[ligne][index_r] = "ROUTINGPORT" + str(self.nbr_interface_routeur[ligne])
                    self.nbr_interface_routeur[ligne] += 1

        #écriture dans le fichier VHDL
        fw= open(outputdir + "/noc_config_configurable_part_7.vhd", 'w')
        fw.write("%s" %ch)
        for ligne in range (self.nbr_R):
            for colonne in range (self.nbr_R):
                if ligne != colonne:
                    fw.write("constant from_ROUTER%d_to_ROUTER%d_destination_port : regPORTADD:= %s;\n" %(ligne, colonne, self.Premier_routeur_du_chemin_entre_2_routeurs[ligne][colonne]))
            fw.write("\n")
        fw.close()


 # Génération VHDL : ------ 8) ADDRESS DECODER TYPES ------
    def generate_configurable_part_8(self):
        outputdir = "./Noc0__"
        if not os.path.exists(outputdir):
            os.makedirs(outputdir)


        ch='''
------ 8) ADDRESS DECODER TYPES ------
--define the size of each address decoding table of each master of each router (in the number of rules that it contain)
'''
        fw= open(outputdir + "/noc_config_configurable_part_8.vhd", 'w')
        fw.write("%s" %ch)
        for r in range(self.nbr_R):
            for m in range (self.nbr_M_par_routeur[r]):
                fw.write("type router%d_master%d_record_address_decod_table is array (0 to ROUTER%d_MASTER%d_ADD_DECOD_TABLE_SIZE-1) of record_master_interface_address_decode_routing_table;\n" %(r,m,r,m))
                if (m == self.nbr_M_par_routeur[r]-1):
                    fw.write("\n")
        fw.write("type unconstrained_array_record_address_decod_table is array (natural range <>) of record_master_interface_address_decode_routing_table;\n")
        fw.close()



 # Génération VHDL : ------ 9) ADDRESS DECODER TABLES ------
    def generate_configurable_part_9(self):
        outputdir = "./Noc0__"
        if not os.path.exists(outputdir):
            os.makedirs(outputdir)
        ch='''
------ 9) ADDRESS DECODER TABLES ------
-- constant ROUTERi_MASTERj_ADDRESS_DECODER_TABLE : router0_master0_record_address_decod_table:=(
-- |    destination slave   |   destination slave 	    |   		   Routing table 				  | slave destination |
-- |	   base address	    | 	   high address         |	 	    local port noc address		  	  |      address      |
'''
        fw= open(outputdir + "/noc_config_configurable_part_9.vhd", 'w')
        fw.write("%s" %ch)

        for r in range(self.nbr_R):
            for m in range(self.nbr_M_par_routeur[r]):
                fw.write("constant ROUTER%d_MASTER%d_ADDRESS_DECODER_TABLE : router%d_master%d_record_address_decod_table:=(\n" %(r,m,r,m))
                i_nbr_decodage_adresse = 0
                #puis écrire le reste
                for r_esclave in range(self.nbr_R):
                    for s in range(self.nbr_S_par_routeur[r_esclave]):
                        if self.maitre_possede_decodage_adresse_esclave[r][m][r_esclave][s].get() == 1:
                            #Si esclave connecté au même routeur : port local de routage = "SLAVEj"
                            if r_esclave == r:
                                fw.write("      (ROUTER%d_MASTER%d_address_mapping_for_ROUTER%d_SLAVE%d_BASE_ADD, ROUTER%d_MASTER%d_address_mapping_for_ROUTER%d_SLAVE%d_HIGH_ADD, SLAVE%d, ROUTER%d & SLAVE%d)" %(r,m,r_esclave,s+self.nbr_M_par_routeur[r_esclave],r,m,r_esclave,s+self.nbr_M_par_routeur[r_esclave],s+self.nbr_M_par_routeur[r_esclave],r_esclave,s+self.nbr_M_par_routeur[r_esclave]))
                            #Sinon port local de routage = "from_ROUTERk_to_ROUTERl"
                            else:
                                fw.write("      (ROUTER%d_MASTER%d_address_mapping_for_ROUTER%d_SLAVE%d_BASE_ADD, ROUTER%d_MASTER%d_address_mapping_for_ROUTER%d_SLAVE%d_HIGH_ADD, from_ROUTER%d_to_ROUTER%d_destination_port, ROUTER%d & SLAVE%d)" %(r,m,r_esclave,s+self.nbr_M_par_routeur[r_esclave],r,m,r_esclave,s+self.nbr_M_par_routeur[r_esclave],r,r_esclave,r_esclave,s+self.nbr_M_par_routeur[r_esclave]))
                            i_nbr_decodage_adresse += 1

                            #cas particulier : la table n'est composée que d'une seule règle -> seulement il n'est pas possible d'ecrire des tableaux (array) à une entrée en VHDL, donc on duplique la seule règle. Cette règle n'est pas prise en compte dans l'AGGREGATING ARRAY et la configuration des décodeurs d'adresse dans le noc
                            if self.Taille_decodeur_adr_maitre_est_de_un[r][m]==1:
                                #Si esclave connecté au même routeur : port local de routage = "SLAVEj"
                                if r_esclave == r:
                                    fw.write("\n      (fROUTER%d_MASTER%d_address_mapping_for_ROUTER%d_SLAVE%d_BASE_ADD, ROUTER%d_MASTER%d_address_mapping_for_ROUTER%d_SLAVE%d_HIGH_ADD, SLAVE%d, ROUTER%d & SLAVE%d));\n\n" %(r,m,r_esclave,s+self.nbr_M_par_routeur[r_esclave],r,m,r_esclave,s+self.nbr_M_par_routeur[r_esclave],s+self.nbr_M_par_routeur[r_esclave],r_esclave,s+self.nbr_M_par_routeur[r_esclave]))
                                #Sinon port local de routage = "from_ROUTERk_to_ROUTERl"
                                else:
                                    fw.write("\n      (fROUTER%d_MASTER%d_address_mapping_for_ROUTER%d_SLAVE%d_BASE_ADD, ROUTER%d_MASTER%d_address_mapping_for_ROUTER%d_SLAVE%d_HIGH_ADD, from_ROUTER%d_to_ROUTER%d_destination_port, ROUTER%d & SLAVE%d));\n\n" %(r,m,r_esclave,s+self.nbr_M_par_routeur[r_esclave],r,m,r_esclave,s+self.nbr_M_par_routeur[r_esclave],r,r_esclave,r_esclave,s+self.nbr_M_par_routeur[r_esclave]))

                            #sinon si la denière règle de la table : mettre un point-virgule sinon une virgule
                            elif i_nbr_decodage_adresse == self.Taille_table_decodeur_adr_maitre[r][m]:
                                fw.write(");\n\n")
                            else:
                                fw.write(",\n")


        fw.write("\n-- => AGGREGATING ARRAY <= --\n")
        fw.write("--aggregates all master address decoder rules : starting from ROUTER0 - MASTER0 - RULES0 => first increment RULE number, then increment MASTER number, and finally increment ROUTER number\n")
        fw.write("--concantenate all the rules with a &\n")
        fw.write("constant ALL_MASTER_ADDRESS_DECODER_TABLES : unconstrained_array_record_address_decod_table:=(\n")

        for r in range(self.nbr_R):
            for m in range(self.nbr_M_par_routeur[r]):
                for t in range(self.Taille_table_decodeur_adr_maitre[r][m]):
                    fw.write("ROUTER%d_MASTER%d_ADDRESS_DECODER_TABLE(%d)"%(r,m,t))
                    if (r == self.nbr_R-1) and   (m == self.nbr_M_par_routeur[r]-1) and (t==self.Taille_table_decodeur_adr_maitre[r][m]-1) :
                        fw.write("\n );\n")
                    else:
                        fw.write(" &\n")

        fw.close()


 # Génération VHDL : ------ 10) ADDRESS DECODER PARAMETER MATRIX ------
    def generate_configurable_part_10(self):
        outputdir = "./Noc0__"
        if not os.path.exists(outputdir):
            os.makedirs(outputdir)

        ch='''
------ 10) ADDRESS DECODER PARAMETER MATRIX ------
--one line for each router (from 0 to y)
--one column for each master of each router (from 0 to 14)
--the goal is to define one couple of value "(MASTER_TABLE_RANK_NB, MASTER_DECOD_TABLE_SIZE)" for each master of each router
--MASTER_TABLE_RANK_NB = rank of the address decoding rule in the total number of rules (it is equal to the cumulated number of rules in the previous master address decoders)
--MASTER_DECOD_TABLE_SIZE = number of address decoding rule in the current master address decoder table
constant ADD_DECODER_PARAMETER_MX :  matrix_add_decoder_parameter :=(
'''

        taille_table_decodeur_adresse_maitre_cumulees = 0

        fw= open(outputdir + "/noc_config_configurable_part_10.vhd", 'w')
        fw.write("%s" %ch)
        for r in range (self.nbr_R):
            fw.write("  (")
            for m in range (self.nbr_M_par_routeur[r]):
                fw.write(" (%d,%d)" %(taille_table_decodeur_adresse_maitre_cumulees,self.Taille_table_decodeur_adr_maitre[r][m]))
                taille_table_decodeur_adresse_maitre_cumulees += self.Taille_table_decodeur_adr_maitre[r][m]
                if m != (15-self.nbr_M_par_routeur[r]-1):
                    fw.write(",")


            #si il n'y pas 15 interfaces maitre au routeur, remplir le reste de (0,0),
            for o in range (15-self.nbr_M_par_routeur[r]):
                fw.write(" (0,0)")
                if (o != 15-self.nbr_M_par_routeur[r]-1):
                    fw.write(",")

            if (r == self.nbr_R-1):
                fw.write(")); -- ROUTER %d\n" %r)
            else:
                fw.write("), -- ROUTER %d\n" %r)

        fw.write("--MASTER	MASTER		MASTER		MASTER		MASTER		MASTER		MASTER		MASTER	MASTER...\n")
        fw.write("--0			1			2			3			4			5			6			7		8		9	   10	  11    12     13      14\n")
        fw.close()

 # Génération VHDL : ------ 11) ROUTING TABLE  -------
    def generate_configurable_part_11(self):
        outputdir = "./Noc0__"
        if not os.path.exists(outputdir):
            os.makedirs(outputdir)

        ch='''
------ 11) ROUTING TABLE  -------
--define for each router a routing table that gives the destination port to take
--to reach all the other routers of the network.
-- 1rst value) router destination address in regROUTERADD format.
-- 2nd value) local router port address'''

        fw= open(outputdir + "/noc_config_configurable_part_11.vhd", 'w')
        fw.write("%s" %ch)
        for r in range (self.nbr_R):
            fw.write("\n constant ROUTER%d_ROUTING_TABLE : routing_table_array:=( \n" %r)
            for r_dest in range (self.nbr_R):
                #Pour la dernière de la table de routage du dernier routeur
                if r==self.nbr_R-1 and r_dest==(self.nbr_R-2):
                    fw.write("      (ROUTER%d, from_ROUTER%d_to_ROUTER%d_destination_port));\n" %(r_dest,r,r_dest))
                #Pour la dernière ligne de la table de routage tous les autres routeurs
                elif r!=r_dest and r_dest == self.nbr_R-1:
                    fw.write("      (ROUTER%d, from_ROUTER%d_to_ROUTER%d_destination_port));\n" %(r_dest,r,r_dest))
                #Pour toute les autres lignes de la table de routage de tous les routeurs
                elif r!=r_dest and r_dest != self.nbr_R:
                    fw.write("      (ROUTER%d, from_ROUTER%d_to_ROUTER%d_destination_port),\n" %(r_dest,r,r_dest))

        fw.write("\n -- => AGGREGATING ARRAY <= --\n")
        fw.write("constant ALL_ROUTING_TABLES : array_all_routing_tables:=(\n")
        for r in range (self.nbr_R-1):
            fw.write("      ROUTER%d_ROUTING_TABLE,\n" %r)
        fw.write("      ROUTER%d_ROUTING_TABLE\n" %(self.nbr_R-1))
        fw.write(" );\n\n")
        fw.close()



 # Génération VHDL : ------ 12) LOCAL CONNEXIONS MATRIX ------
    def generate_configurable_part_12(self):
        outputdir = "./Noc0__"

        fw= open(outputdir + "/noc_config_configurable_part_12.vhd", 'w')
        fw.write("------ 12) LOCAL CONNEXIONS MATRIX ------ \n")

        #variable pour calcul de : single_slave, slave_rank, single_master & master_rank
        nbr_esclave_connecte_au_maitre = [[0 for m in range(self.nbr_M_par_routeur[r])] for r in range(self.nbr_R)]
        nbr_maitre_connecte_a_esclave = [[0 for s in range(self.nbr_S_par_routeur[r])] for r in range(self.nbr_R)]

        rang_dernier_esclave_connecte_au_maitre = [[0 for m in range(self.nbr_M_par_routeur[r])] for r in range(self.nbr_R)]
        rang_dernier_maitre_connecte_a_esclave = [[0 for s in range(self.nbr_S_par_routeur[r])] for r in range(self.nbr_R)]

        #Initilisation des matrices "self.Matrices_connexions_locales" à partir des connexions "self.Connexions_locales"
        #Attention les esclaves dans "self.Connexions_locales[r][m][s]" sont comptés à partir de 0 alors que dans "self.Matrices_connexions_locales"
        #ils sont comptés à partir du n° du dernier maitre du routeur "self.nbr_M_par_routeur[r]"
        for r in range(self.nbr_R):
            for m in range(self.nbr_M_par_routeur[r]):
                for s in range(self.nbr_S_par_routeur[r]):
                    if self.Connexions_locales[r][m][s].get() == 1 :
                        self.Matrices_connexions_locales[r][s+self.nbr_M_par_routeur[r]][m] = 1
                        nbr_esclave_connecte_au_maitre[r][m] += 1
                        rang_dernier_esclave_connecte_au_maitre[r][m] = s + self.nbr_M_par_routeur[r]
                        nbr_maitre_connecte_a_esclave[r][s] += 1
                        rang_dernier_maitre_connecte_a_esclave[r][s] = m
                    else:
                        self.Matrices_connexions_locales[r][s+self.nbr_M_par_routeur[r]][m] = 0

        #placement résultats des variables : single_slave, slave_rank, single_master & master_rank dans Matrices_connexions_locales au rang 15 et 16
        for r in range(self.nbr_R):
            for m in range(self.nbr_M_par_routeur[r]):
                if nbr_esclave_connecte_au_maitre[r][m] == 1 :
                    self.Matrices_connexions_locales[r][15][m] = 1
                    self.Matrices_connexions_locales[r][16][m] = rang_dernier_esclave_connecte_au_maitre[r][m]

            for s in range(self.nbr_S_par_routeur[r]):
                if nbr_maitre_connecte_a_esclave[r][s] == 1 :
                    self.Matrices_connexions_locales[r][s+self.nbr_M_par_routeur[r]][15] = 1
                    self.Matrices_connexions_locales[r][s+self.nbr_M_par_routeur[r]][16] = rang_dernier_maitre_connecte_a_esclave[r][s]


        #ecriture d'une matrice de connexion locale par routeur à partir de "self.Matrices_connexions_locales"
        for r in range(self.nbr_R):
            fw.write('constant ROUTER%d_LOCAL_MX    : local_connexion_matrix :=(\n' %r)
            for s in range(self.nbr_port_routeur_max+1):
                fw.write("      (")
                for m in range(self.nbr_port_routeur_max+1):
                    if (m == self.nbr_port_routeur_max):
                        fw.write("%d" %self.Matrices_connexions_locales[r][s][m])
                    else:
                        fw.write("%d," %self.Matrices_connexions_locales[r][s][m])

                if (s == self.nbr_port_routeur_max-1): #avant dernière ligne = single slave
                    fw.write("), --single_slave\n")
                elif (s == self.nbr_port_routeur_max):  #dernière ligne =  slave rank
                    fw.write("));--slave_rank\n")
                else:                                 #autre lignes (normales)
                    fw.write("),-- slave%d\n" %s)

            fw.write("     --m m m m m m m m m m m m m m m s m                                                          \n")
            fw.write("     --a a a a a a a a a a a a a a a i r                                                          \n")
            fw.write("     --s s s s s s s s s s s s s s s n a                                                          \n")
            fw.write("     --t t t t t t t t t t t t t t t g n                                                          \n")
            fw.write("     --e e e e e e e e e e e e e e e l k                                                          \n")
            fw.write("     --r r r r r r r r r r r r r r r e                                                            \n")
            fw.write("     --0 1 2 3 4 5 6 7 8 9 1 1 1 1 1 m                                                            \n")
            fw.write("     --                    0 1 2 3 4                                                              \n")
            fw.write("\n")
            fw.write("\n")


        fw.write("-- => AGGREGATING ARRAY <= --\n")
        fw.write("constant ALL_ROUTER_LOCAL_MATRIX : array_all_local_connexion_matrix:=(\n")
        for r in range(self.nbr_R):
            fw.write("      ROUTER%d_LOCAL_MX" %r)
            if (r==self.nbr_R-1):
                fw.write("\n);\n")
            else:
                fw.write(",\n")
        fw.close()


    def generate_end_of_file_with_function(self):
        outputdir = "./Noc0__"
        if not os.path.exists(outputdir):
            os.makedirs(outputdir)

        ch='''
    --- FUNCTION DECLARATION ---
    function or_reduce(V: std_logic_vector) return std_logic;
end noc_config;

package body noc_config is

    ---- FUNCTION DEFINTION ----
    --function that apply a logic OR to all bits of a std_logic_vector
    function or_reduce(V: std_logic_vector)
        return std_logic is
        variable result: std_logic;
    begin
        for i in V'range loop
            if i = V'left then
                result := V(i);
            else
                result := result OR V(i);
            end if;
            exit when result ='1';
        end loop;
        return result;
    end or_reduce;

end noc_config;

        '''
        fw= open(outputdir + "/noc_config_end_of_file_with_function.vhd", 'w')
        fw.write("%s" %ch)
        fw.close()

    def generate_noc_security_conf(self):
        outputdir = "./Noc0__"
        if not os.path.exists(outputdir):
            os.makedirs(outputdir)
        ch0='''
--------------------------------------------------------------
-- IP   		: noc_security_conf PACKAGE              	--
-- DESCRIPTION 	: security monitor configuration			--
-- AUTHOR 		: R.Druyer                              	--
-- DATE   		: 3 décembre 2016                        	--
-- VERSION		: 2.0                                   	--
--------------------------------------------------------------

library IEEE;
use IEEE.std_logic_1164.all;
use work.noc_config.all;

package noc_security_conf is
        '''

        ch1='''
constant	ACCESS_RIGHT_SIZE							: integer := 8;
constant	SECURITY_MONITOR_CONFIGURATION_PACKET_SIZE	: integer := 16;

subtype		regACCESS_RIGHT		is std_logic_vector((ACCESS_RIGHT_SIZE-1) downto 0);
subtype		regCONF_PACKET		is std_logic_vector((SECURITY_MONITOR_CONFIGURATION_PACKET_SIZE-1) downto 0);
subtype		reg5bits			is std_logic_vector(4 downto 0);
subtype		reg3bits			is std_logic_vector(2 downto 0);

type	arrayCONF_PACKET			is array(natural RANGE <>) of regCONF_PACKET;

type master_monitor_security_rule_record is record
	SLAVE_BASE_ADD 					: regADD;
	SLAVE_HIGH_ADD					: regADD;
	SECURITY_POLICY 				: regACCESS_RIGHT;
end record;

type slave_monitor_security_rule_record is record
	SOURCE_ROUTER_ADD 				: regROUTERADD;
	SOURCE_MASTER_ADD 				: regPORTADD;
	SLAVE_BASE_ADD					: regADD;
	SLAVE_HIGH_ADD					: regADD;
	SECURITY_POLICY 				: regACCESS_RIGHT;
end record;

type security_monitor_configuration_record is record
	SECURITY_MONITOR_TABLE_RANK			: integer;
	SECURITY_MONITOR_TABLE_SIZE			: integer;
end record;


constant RULE_ACTIVATED			 : std_logic :='1';
constant RULE_DEACTIVATED		 : std_logic :='0';

constant WRITE_AUTHORIZED		 : std_logic :='1';
constant WRITE_DENIED			 : std_logic :='0';
constant READ_AUTHORIZED		 : std_logic :='1';
constant READ_DENIED			 : std_logic :='0';

constant DATA_CYCLE				 : std_logic_vector(1 downto 0) :="00";
constant KEY_CYCLE				 : std_logic_vector(1 downto 0) :="01";
constant IV_CYCLE				 : std_logic_vector(1 downto 0) :="10";
constant CONTEXT_CYCLE			 : std_logic_vector(1 downto 0) :="11";

constant reg5_null_bits			 : reg5bits :=(others =>'0');
constant reg3_null_bits			 : reg3bits :=(others =>'0');

type monitor_configuration_table_size_vector is array (0 to 15) of security_monitor_configuration_record;
type security_monitor_configuration_matrix is array (0 to TOTAL_ROUTER_NB-1) of monitor_configuration_table_size_vector;


type integer_router_monitor_reconfigurability is array (0 to 17) of integer;
type router_monitor_reconfigurability_matrix is array (0 to TOTAL_ROUTER_NB-1) of integer_router_monitor_reconfigurability;

type unconstrained_array_master_security_monitor is array (natural range <>) of master_monitor_security_rule_record;
type unconstrained_array_slave_security_monitor is array (natural range <>) of slave_monitor_security_rule_record;

------------------------     # CONFIGURABLE PART #      ------------------------
'''

        ch_security_monitor_deactivated='''
        ### SECURITY MONITORS DEACTIVATED ###
constant MASTER_SECURITY_MONITOR_CONFIGURATION_MX   : security_monitor_configuration_matrix 		:=(others =>(others => (0,0)));
constant SLAVE_SECURITY_MONITOR_CONFIGURATION_MX    : security_monitor_configuration_matrix 		:=(others =>(others => (0,0)));
constant SECURITY_MONITOR_RECONFIGURABILITY_MX 		: router_monitor_reconfigurability_matrix 		:=(others =>(others => 0));
constant ALL_MASTER_SECURITY_MONITOR_RULES 			: unconstrained_array_master_security_monitor(0 to 2)	:=(others =>((others => '0'),(others => '0'),(others => '0')));
constant ALL_SLAVE_SECURITY_MONITOR_RULES 			: unconstrained_array_slave_security_monitor(0 to 2)	:=(others =>((others => '0'),(others => '0'),(others => '0'),(others => '0'),(others => '0')));
    '''

        fw= open(outputdir + "/noc_security_conf.vhd", 'w')
        fw.write("%s" %ch0)
        fw.write("%s" %ch1)
        if self.security_monitor_activation.get() == 0:
            fw.write("%s" %ch_security_monitor_deactivated)
        else:
            fw.write("Security monitor activated\n")

        fw.close()

    def generate_error_report(self):
        outputdir = "./Noc0__"
        if not os.path.exists(outputdir):
            os.makedirs(outputdir)

        fw= open(outputdir + "/rapport_erreur_config_noc.txt", 'w')


        if self.Rapport_d_erreur == "":
            fw.write("Pas d'erreur détectée dans la configuration.")
        else:
            fw.write(self.Rapport_d_erreur)
        fw.close()



    def generate_vhdl_file(self):
        error_found=0
        #Verifier que le dossier existe, il est cree si necessaire
        outputdir = "./Noc0__"
        if not os.path.exists(outputdir):
            os.makedirs(outputdir)
        generated_files=["/noc_config_configurable_part_0.vhd","/noc_config_fixed_part.vhd","/noc_config_configurable_part_1.vhd","/noc_config_configurable_part_2.vhd","/noc_config_configurable_part_3.vhd","/noc_config_configurable_part_4.vhd","/noc_config_configurable_part_5.vhd","/noc_config_configurable_part_6.vhd","/noc_config_configurable_part_7.vhd","/noc_config_configurable_part_8.vhd","/noc_config_configurable_part_9.vhd","/noc_config_configurable_part_10.vhd","/noc_config_configurable_part_11.vhd","/noc_config_configurable_part_12.vhd","/noc_config_end_of_file_with_function.vhd","/noc_security_conf.vhd"]
        self.generate_configurable_part_0()
        self.generate_fixed_part()
        self.generate_configurable_part_1()
        self.generate_configurable_part_2()
        self.generate_configurable_part_3()
        self.generate_configurable_part_4()
        self.generate_configurable_part_5()
        self.generate_configurable_part_6()
        self.generate_configurable_part_7()
        self.generate_configurable_part_8()
        self.generate_configurable_part_9()
        self.generate_configurable_part_10()
        self.generate_configurable_part_11()
        self.generate_configurable_part_12()
        self.generate_end_of_file_with_function()
        self.generate_noc_security_conf()
        self.generate_error_report()
        for i in range(len(generated_files)):
            if not os.path.exists(outputdir+generated_files[i]):
                error_found=1
        if error_found:
            showerror("Erreur", 'Enregistrer avant vos modifications dans (configuration des connexions locales), (configurations des decodeurs d\'adresses) ou (configurations des connexions en paquets)' )
        else:
            # genere le fichier de sortie
            with open(outputdir + "/noc_config.vhd",'w') as new_file:
                with open(outputdir + "/noc_config_configurable_part_0.vhd") as old_file:
                    for line in old_file:
                        new_file.write(line)
                with open(outputdir + "/noc_config_fixed_part.vhd") as old_file:
                    for line in old_file:
                        new_file.write(line)
                with open(outputdir + "/noc_config_configurable_part_1.vhd") as old_file:
                    for line in old_file:
                        new_file.write(line)
                with open(outputdir + "/noc_config_configurable_part_2.vhd") as old_file:
                    for line in old_file:
                        new_file.write(line)
                with open(outputdir + "/noc_config_configurable_part_3.vhd") as old_file:
                    for line in old_file:
                        new_file.write(line)
                with open(outputdir + "/noc_config_configurable_part_4.vhd") as old_file:
                    for line in old_file:
                        new_file.write(line)
                with open(outputdir + "/noc_config_configurable_part_5.vhd") as old_file:
                    for line in old_file:
                        new_file.write(line)
                with open(outputdir + "/noc_config_configurable_part_6.vhd") as old_file:
                    for line in old_file:
                        new_file.write(line)
                with open(outputdir + "/noc_config_configurable_part_7.vhd") as old_file:
                    for line in old_file:
                        new_file.write(line)
                with open(outputdir + "/noc_config_configurable_part_8.vhd") as old_file:
                    for line in old_file:
                        new_file.write(line)
                with open(outputdir + "/noc_config_configurable_part_9.vhd") as old_file:
                    for line in old_file:
                        new_file.write(line)
                with open(outputdir + "/noc_config_configurable_part_10.vhd") as old_file:
                    for line in old_file:
                        new_file.write(line)
                with open(outputdir + "/noc_config_configurable_part_11.vhd") as old_file:
                    for line in old_file:
                        new_file.write(line)
                with open(outputdir + "/noc_config_configurable_part_12.vhd") as old_file:
                    for line in old_file:
                        new_file.write(line)
                with open(outputdir + "/noc_config_end_of_file_with_function.vhd") as old_file:
                    for line in old_file:
                        new_file.write(line)


            os.remove(outputdir + "/noc_config_fixed_part.vhd")
            os.remove(outputdir + "/noc_config_configurable_part_0.vhd")
            os.remove(outputdir + "/noc_config_configurable_part_1.vhd")
            os.remove(outputdir + "/noc_config_configurable_part_2.vhd")
            os.remove(outputdir + "/noc_config_configurable_part_3.vhd")
            os.remove(outputdir + "/noc_config_configurable_part_4.vhd")
            os.remove(outputdir + "/noc_config_configurable_part_5.vhd")
            os.remove(outputdir + "/noc_config_configurable_part_6.vhd")
            os.remove(outputdir + "/noc_config_configurable_part_7.vhd")
            os.remove(outputdir + "/noc_config_configurable_part_8.vhd")
            os.remove(outputdir + "/noc_config_configurable_part_9.vhd")
            os.remove(outputdir + "/noc_config_configurable_part_10.vhd")
            os.remove(outputdir + "/noc_config_configurable_part_11.vhd")
            os.remove(outputdir + "/noc_config_configurable_part_12.vhd")
            os.remove(outputdir + "/noc_config_end_of_file_with_function.vhd")


# Main
if __name__ == "__main__":

    fenetre_tk = Tk()
    fenetre_tk.title("Outil de génération de configurations NoC (Version 1.0)")

    if platform.system() == "Linux":
        fenetre_tk.geometry('1290x810')
    elif platform.system() == "Windows":
        fenetre_tk.geometry('1070x810')

    Outil_Python = MainInterface(fenetre_tk)


    Outil_Python.mainloop()
