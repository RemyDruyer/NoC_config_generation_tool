#!/usr/bin/python
# -*- coding: iso-8859-1 -*-
#--------------------------------------------------------------
#-- FILE NAME  : SECANOC.py                              --
#-- AUTHOR   : Adel BENSAAD                                      --
#-- DATE     : 20 octobre 2016                                   --
#-- VERSION  : 1.3                                           --
#--------------------------------------------------------------

from tkinter import *
from tkinter.messagebox import *
import os
import shutil
import re
from tkinter.messagebox import showerror

# Classe Vertical Scroll
# Crée une scroll bar verticale coté droit ajustable
class VerticalScrolledFrame(Frame):
    """
    * Use the 'interior' attribute to place widgets inside the scrollable frame
    """
    def __init__(self, parent, *args, **kw):
        Frame.__init__(self, parent, *args, **kw)

        # create a canvas object and a vertical scrollbar for scrolling it
        vscrollbar = Scrollbar(self, orient=VERTICAL)
        vscrollbar.pack(fill=Y, side=RIGHT, expand=FALSE)
        canvas = Canvas(self, bd=0, highlightthickness=0, width = 200, height = 280, yscrollcommand=vscrollbar.set)
        #canvas.config(scrollregion="0 0 110 110")
        canvas.pack(side=LEFT, fill=BOTH, expand=TRUE)
        vscrollbar.config(command=canvas.yview)

        # reset the view
        canvas.xview_moveto(0)
        canvas.yview_moveto(0)

        # create a frame inside the canvas which will be scrolled with it
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
# Creation of one class which inherit from Tkinter.Tk
class Interface(Frame):
    nbr_R_Global=64
    nbr_M_Global=0
    nbr_S_Global=0
    nbr_RP_Global=16

    # Init
    def __init__(self, fenetre, **kwargs):
        Frame.__init__(self, fenetre, width=768, height=576, **kwargs)
        self.grid()
        self.damierAChiffreLigne = list()
        self.damierAChiffreColonne = list()
        self.damierDiag = list()
        self.damierX = list()
        self.damierNbrMaitre = list()
        self.damierNbrEsclave = list()
        self.nbr_ligne = 0
        self.iAChiffreLigne = 0
        self.iAChiffreColonne = 0
        self.idamierDiag = 0
        self.idamierX = 0
        self.nbr_click_run = 0
        self.flag_checkbouton_moniteur_securite = 0
        self.flag_checkbouton_connexions_locales = 0
        self.flag_checkbouton_decodeurs_adresse =0
        self.flag_checkbouton_connexions_paquets = 0
        self.flag_cliquer0 = 0
        
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
        fenetre.config(menu=self.barremenu)
        
        # nombre routeurs Label & Entry
        self.champ_nbr_routeur = Label(self, text="Nombre de routeurs dans le reseau (entre 3 et 64):")
        self.champ_nbr_routeur.grid(row = 0, column = 0, columnspan = 9, sticky= NW)
        self.entry_nbr_routeur = Entry(self)
        self.entry_nbr_routeur.grid(row = 0, column = 10, columnspan = 9, sticky= W)
        self.entry_nbr_routeur.insert(0,"3")
        # Canvas & Scrollbar
        self.fenetre_canvas = VerticalScrolledFrame(self)
        self.fenetre_canvas.grid(row=8, column=1, columnspan = 40)
        
        # Init du damier dans le canva
        # Crée un damier avec un bouton Gris sur la case A1 (la grid commence à la ligne 8 colonne 1)
        # Création des 64 boutons sur la ligne A (sur la grid => ligne 8) "1 2 3 ... 64"
        # Création des 64 boutons sur la colonne 1 (sur la grid => colonne 1) "1 2 3 ... 64"
        # Création des 64 boutons diagonales en gris
        # Création de 2 boutons "vide" ou "X" en position A2 et B1 (sur la grid => [ligne 9 colonne 3] & [ligne 10colonne 2])
        for ligne in range(8,74):
            for colonne in range (1,67):
                if ligne == 8 and colonne == 1:
                    self.damierAA = Button(self.fenetre_canvas.interior, text =" ", borderwidth=1, bg="grey",height = 1, width = 1)
                    self.damierAA.grid(row = ligne, column = colonne, sticky=NSEW)
                elif ligne == 8:
                    self.damierAChiffreLigne.append( Button(self.fenetre_canvas.interior, text ="%s" % (colonne-1), borderwidth=1, height = 1, width = 1))
                    self.damierAChiffreLigne[self.iAChiffreLigne].grid(row = ligne, column = colonne, sticky=NSEW)
                    self.iAChiffreLigne +=1
                elif colonne == 1:
                    self.damierAChiffreColonne.append( Button(self.fenetre_canvas.interior, text ="%s" % (ligne-8), borderwidth=1, height = 1, width = 1))
                    self.damierAChiffreColonne[self.iAChiffreColonne].grid(row = ligne, column = colonne, sticky=NSEW)
                    self.iAChiffreColonne +=1
                elif (ligne-7) == colonne:
                    self.damierDiag.append( Button(self.fenetre_canvas.interior, text =" ", borderwidth=1, bg="grey", height = 1, width = 1))
                    self.damierDiag[self.idamierDiag].grid(row = ligne, column = colonne, sticky=NSEW)
                    self.idamierDiag +=1
                elif ligne == 9 and colonne == 3:
                    self.damierX.append( Button(self.fenetre_canvas.interior, text =" ", borderwidth=1, height = 1, width = 1, command = self.cliquer0))
                    self.damierX[self.idamierX].grid(row = ligne, column = colonne, sticky=NSEW)
                    self.idamierX +=1
                elif ligne == 10 and colonne == 2:
                    self.damierX.append( Button(self.fenetre_canvas.interior, text =" ", borderwidth=1, height = 1, width = 1, command = self.cliquer0))
                    self.damierX[self.idamierX].grid(row = ligne, column = colonne, sticky=NSEW)
                    self.idamierX +=1
                    
        # On cache des cases pour avoir un petit damier 2x2 par defaut            
        # Damier avec les cases cachées
        for ligne_ in range(65, 2, -1):
            # Decremente les indices pour arriver sur le dernier elt
            self.iAChiffreLigne -=1
            self.iAChiffreColonne -=1
            self.idamierDiag -=1
            
            # Cache les derniers cases "chiffres" et "diag"
            self.damierAChiffreLigne[self.iAChiffreLigne].grid_forget()
            self.damierAChiffreColonne[self.iAChiffreColonne].grid_forget()
            self.damierDiag[self.idamierDiag].grid_forget()
        
        # Bouton RUN
        self.bouton_run = Button(self, text=" Generation de la matrice de connexions des routeurs ", command=self.run_action)
        self.bouton_run.grid(row = 0, column = 20, columnspan = 9, sticky=NSEW)
                
        # checkbutton "Activation des moniteurs de securite"
        self.checkbouton_moniteur_securite = Checkbutton(self, text="Activation des moniteurs \n de securite", command= self.checkbouton_moniteur_securite_action)
        self.checkbouton_moniteur_securite.grid(row =13, column = 0, rowspan = 8,columnspan = 8, sticky=NSEW)
        # bouton "Configuration des moniteurs de sécurité"
        self.bouton_moniteur_securite = Button(self, text="Configuration des moniteurs \n de securite", command=self.quit, state=DISABLED)
        self.bouton_moniteur_securite.grid(row = 21, column = 0, rowspan = 8,columnspan = 8, sticky=NSEW)
        
        # checkbutton "Interfaces toutes connectees en local"
        self.checkbouton_connexions_locales = Checkbutton(self, text="Interfaces toutes \n connectees en local", command= self.checkbouton_connexions_locales_action)
        self.checkbouton_connexions_locales.grid(row =13, column = 8, rowspan = 8, columnspan = 8, sticky=NSEW)
        # bouton "Configuration des connexions locales"
        self.bouton_connexions_locales = Button(self, text="Configuration des \n connexions locales", command=self.bouton_connexions_locales_action)
        self.bouton_connexions_locales.grid(row = 21, column = 8, rowspan = 8, columnspan = 8, sticky=NSEW)
        
        # checkbutton "Interfaces toutes connectees en paquets"
        self.checkbouton_connexions_paquets = Checkbutton(self, text="Interfaces toutes \n connectees en paquets", command= self.checkbouton_connexions_paquets_action)
        self.checkbouton_connexions_paquets.grid(row =13, column = 16, rowspan = 8,columnspan = 8, sticky=NSEW)
        # bouton "Configuration des connexions en paquets"
        self.bouton_connexions_paquets = Button(self, text="Configuration des \n connexions en paquets", command=self.bouton_connexions_paquets_action)
        self.bouton_connexions_paquets.grid(row = 21, column = 16, rowspan = 8,columnspan = 8, sticky=NSEW)
        
        # bouton "Configuration des décodeurs d'adresse"
        self.bouton_decodeurs_adresses = Button(self, text="Configuration des decodeurs \n d'adresse", command=self.bouton_decodeurs_adresse_action)
        self.bouton_decodeurs_adresses.grid(row = 21, column = 24, rowspan = 8,columnspan = 8, sticky=NSEW)
        
        # bouton "Verification"
        self.bouton_verification = Button(self, text="Verification", command=self.quit)
        self.bouton_verification.grid(row = 21, column = 32, rowspan = 8,columnspan = 8, sticky=NSEW)
        
        # bouton "Génération du VHDL"
        self.bouton_generation_vhdl = Button(self, text="Generation \n du VHDL", command= self.on_buttonGenerate_clicked)
        self.bouton_generation_vhdl.grid(row = 21, column = 40, rowspan = 8,columnspan = 8, sticky=NSEW)
    
    # Fonction associé à l'action sur le bouton DamierX[0] & DamierX[1]
    def cliquer0(self):
        if self.flag_cliquer0 == 0:
            self.damierX[0].config(text = "X")
            self.damierX[1].config(text = "X")
            self.flag_cliquer0 = 1
        elif self.flag_cliquer0 == 1:
            self.damierX[0].config(text = " ")
            self.damierX[1].config(text = " ")
            self.flag_cliquer0 = 0    
    
    # Action du bouton "RUN"
    def run_action(self):
	
        # Get variable entry in Box
        if self.entry_nbr_routeur.get()=="":
            showerror("Erreur", 'Vous devez choisir un nombre de routeurs compris entre 3 et 64' )
        else:    
            nbr_maitre_esclave_init_value = StringVar()
            nbr_maitre_esclave_init_value.set = "0"
            self.var = int(self.entry_nbr_routeur.get())
            self.nbr_click_run +=1        
        
            # Check le nombre de routeurs autorisés & genère le damier pour le nbr de routeurs mis en entrée
            if (int(self.entry_nbr_routeur.get()) < 65) and (int(self.entry_nbr_routeur.get()) > 2):
                for m_iterator in range(3,self.var+1):
                    for ligne in range(8,m_iterator+9):
                        for colonne in range (1,m_iterator+2):
                            if ligne == 8 and colonne == 1:
                                continue
                            elif ligne == 8 and colonne < 4:
                                continue
                            elif colonne == 1 and ligne < 11:
                                continue
                            elif ligne == 8 and colonne > m_iterator:
                                self.damierAChiffreLigne[self.iAChiffreLigne].grid(row = ligne, column = colonne, sticky=NSEW)
                                self.iAChiffreLigne +=1
                                if self.iAChiffreLigne == self.var:
                                    self.champ_nbr_interface_maitre = Button(self.fenetre_canvas.interior, bd = 1, text="Nombre d'interfaces maitres \n du routeur")
                                    self.champ_nbr_interface_maitre.grid(row = ligne-1, column = colonne+1, rowspan = 2, columnspan = 8, sticky= NW)
                                    self.champ_nbr_interface_esclave = Button(self.fenetre_canvas.interior, bd=1, text="Nombre d'interfaces \n esclaves du routeur")
                                    self.champ_nbr_interface_esclave.grid(row = ligne-1, column = colonne+10,rowspan = 2, columnspan = 8, sticky= NW)
                            elif colonne == 1 and ligne > (8+m_iterator-1):
                                self.damierAChiffreColonne[self.iAChiffreColonne].grid(row = ligne, column = colonne, sticky=NSEW)
                                self.iAChiffreColonne +=1
                            elif (ligne-7) == colonne and ((colonne > m_iterator) or (ligne > (8+m_iterator-1))):
                                self.damierDiag[self.idamierDiag].grid(row = ligne, column = colonne, sticky=NSEW)
                                self.idamierDiag +=1
                            elif ligne == m_iterator+8 or colonne == m_iterator+1 :
                                self.damierX.append( Button(self.fenetre_canvas.interior, text =" ", borderwidth=1, height = 1, width = 1))
                                self.damierX[self.idamierX].grid(row = ligne, column = colonne, sticky=NSEW)
                                self.idamierX +=1
                                if colonne == (self.var+1):
                                    self.damierNbrMaitre.append( Entry(self.fenetre_canvas.interior, justify=CENTER,  width = 5))
                                    self.damierNbrMaitre[self.nbr_ligne].grid(row = ligne, column = colonne+1, columnspan = 8, sticky= NSEW)
                                    self.damierNbrEsclave.append( Entry(self.fenetre_canvas.interior, justify=CENTER,  width = 5))
                                    self.damierNbrEsclave[self.nbr_ligne].grid(row = ligne, column = colonne+10, columnspan = 8, sticky= NSEW)
                                    self.damierNbrMaitre[self.nbr_ligne].insert(0,"0")
                                    self.damierNbrEsclave[self.nbr_ligne].insert(0,"0")
									
                                    if ligne == (self.var+7):
                                        self.nbr_ligne +=1
                                        self.damierNbrMaitre.append( Entry(self.fenetre_canvas.interior, justify=CENTER,  width = 5))
                                        self.damierNbrMaitre[self.nbr_ligne].grid(row = ligne+1, column = colonne+1, columnspan = 8, sticky= NSEW)
                                        self.damierNbrEsclave.append( Entry(self.fenetre_canvas.interior, justify=CENTER, width = 5))
                                        self.damierNbrEsclave[self.nbr_ligne].grid(row = ligne+1, column = colonne+10, columnspan = 8, sticky= NSEW)
                                        self.damierNbrMaitre[self.nbr_ligne].insert(0,"0")
                                        self.damierNbrEsclave[self.nbr_ligne].insert(0,"0")
                                    self.nbr_ligne +=1
                
                # Bouge les boutons du bas pour laisser la place au Damier
                self.checkbouton_moniteur_securite.grid(row =m_iterator+10, column = 0, rowspan = 8,columnspan = 8, sticky=NSEW)
                self.bouton_moniteur_securite.grid(row = m_iterator+18, column = 0, rowspan = 8,columnspan = 8, sticky=NSEW)
                self.checkbouton_connexions_locales.grid(row =m_iterator+10, column = 8, rowspan = 9,columnspan = 9, sticky=NSEW)
                self.bouton_connexions_locales.grid(row = m_iterator+18, column = 8, rowspan = 9,columnspan = 9, sticky=NSEW)
                self.checkbouton_connexions_paquets.grid(row =m_iterator+10, column = 17, rowspan = 9,columnspan = 9, sticky=NSEW)
                self.bouton_connexions_paquets.grid(row = m_iterator+18, column = 17, rowspan = 9,columnspan = 9, sticky=NSEW)
                self.bouton_decodeurs_adresses.grid(row = m_iterator+18, column = 26, rowspan = 8,columnspan = 8, sticky=NSEW)
                self.bouton_verification.grid(row = m_iterator+18, column = 34, rowspan = 8,columnspan = 8, sticky=NSEW)
                self.bouton_generation_vhdl.grid(row = m_iterator+18, column = 42, rowspan = 8,columnspan = 8, sticky=NSEW)
            else:
                showerror("Erreur", 'Vous devez choisir un nombre de routeurs compris entre 3 et 64')
       
    # Fonction de re-initialisation du damier par defaut 2x2
    def damier_init_defaut(self):
        # Get max value
        self.max = int(self.entry_nbr_routeur.get())
        
        # Cache les boutons Chiffres Diagonales Nbr Esclave Maitre du damier
        for m_i in range(self.max-1,1,-1):
            self.damierAChiffreLigne[m_i].grid_forget()
            self.damierAChiffreColonne[m_i].grid_forget()
            self.damierDiag[m_i].grid_forget()
            self.damierNbrMaitre[m_i].grid_forget()
            self.damierNbrEsclave[m_i].grid_forget()
        
        # Cache les cases de Damier
        for m_i2 in range (self.idamierX-1,1,-1 ):
            self.damierX[m_i2].grid_forget()
    
    def checkbouton_moniteur_securite_action(self):
        if self.flag_checkbouton_moniteur_securite == 0:
            self.bouton_moniteur_securite.config(state = DISABLED)
            self.flag_checkbouton_moniteur_securite = 1
        elif self.flag_checkbouton_moniteur_securite ==1:
            self.bouton_moniteur_securite.config(state = NORMAL)
            self.flag_checkbouton_moniteur_securite = 0
    
    def bouton_connexions_locales_action(self):
        if self.entry_nbr_routeur.get()=="":
            showerror("Erreur", 'Vous devez specifier le nombre de Routeurs' )
        else: 
            self.nbr_R = int(self.entry_nbr_routeur.get())
            self.nbr_M = [0 for i in range(self.nbr_R)]
            self.nbr_S = [0 for i in range(self.nbr_R)]
            error_found=0
            if self.entry_nbr_routeur.get()=="":
                error_found=1
            else:
                for r in range(int(self.entry_nbr_routeur.get())):
                    if self.damierNbrMaitre[r].get()=="" or self.damierNbrEsclave[r].get()=="":
                        error_found=1
            if error_found:
                showerror("Erreur", 'Vous devez specifier le nombre des Maitres et le nbr des Esclaves' )
            else:
				#récupération du nombre de maître et d'esclave à partir des cases
                for r in range(int(self.entry_nbr_routeur.get())):
                    self.nbr_M[r] = int(self.damierNbrMaitre[r].get())
                    self.nbr_S[r] = int(self.damierNbrEsclave[r].get())
                app_localConnexion = LocalConnexion(self.nbr_R,self.nbr_M,self.nbr_S)
                app_localConnexion.mainloop()
                app_localConnexion.destroy()

    def checkbouton_connexions_locales_action(self):
        if self.flag_checkbouton_connexions_locales == 0:
            self.bouton_connexions_locales.config(state = DISABLED)
            self.flag_checkbouton_connexions_locales = 1
        elif self.flag_checkbouton_connexions_locales ==1:
            self.bouton_connexions_locales.config(state = NORMAL)
            self.flag_checkbouton_connexions_locales = 0

    def bouton_decodeurs_adresse_action(self):
        if self.entry_nbr_routeur.get()=="":
            showerror("Erreur", 'Vous devez specifier le nombre de Routeurs' )
        else: 
            self.nbr_R = int(self.entry_nbr_routeur.get())
            self.nbr_M = [0 for i in range(self.nbr_R)]
            self.nbr_S = [0 for i in range(self.nbr_R)]
            error_found=0
            if self.entry_nbr_routeur.get()=="":
                error_found=1
            else:
                for r in range(int(self.entry_nbr_routeur.get())):
                    if self.damierNbrMaitre[r].get()=="" or self.damierNbrEsclave[r].get()=="":
                        error_found=1
            if error_found:
                showerror("Erreur", 'Vous devez specifier le nombre des Maitres et le nbr des Esclaves' )
            else:
                for r in range(int(self.entry_nbr_routeur.get())):
                    self.nbr_M[r] = int(self.damierNbrMaitre[r].get())
                    self.nbr_S[r] = int(self.damierNbrEsclave[r].get())
                app_Decodeur_d_adresse = Decodeur_d_adresse(self.nbr_R,self.nbr_M,self.nbr_S)
                app_Decodeur_d_adresse.mainloop()
                app_Decodeur_d_adresse.destroy()

    def bouton_connexions_paquets_action(self):
        if self.entry_nbr_routeur.get()=="":
            showerror("Erreur", 'Vous devez specifier le nombre de Routeurs' )
        else: 
            self.nbr_R = int(self.entry_nbr_routeur.get())
            self.nbr_M = [0 for i in range(self.nbr_R)]
            self.nbr_S = [0 for i in range(self.nbr_R)]
            error_found=0
            if self.entry_nbr_routeur.get()=="":
                error_found=1
            else:
                for r in range(int(self.entry_nbr_routeur.get())):
                    if self.damierNbrMaitre[r].get()=="" or self.damierNbrEsclave[r].get()=="":
                        error_found=1
            if error_found:
                showerror("Erreur", 'Vous devez specifier le nombre des Maitres et le nbr des Esclaves' )
            else:
                for r in range(int(self.entry_nbr_routeur.get())):
                    self.nbr_M[r] = int(self.damierNbrMaitre[r].get())
                    self.nbr_S[r] = int(self.damierNbrEsclave[r].get())
                app_PaquetConnexion = PaquetConnexion(self.nbr_R,self.nbr_M,self.nbr_S)
                app_PaquetConnexion.mainloop()
                app_PaquetConnexion.destroy()

    def checkbouton_connexions_paquets_action(self):
        if self.flag_checkbouton_connexions_paquets == 0:
            self.bouton_connexions_paquets.config(state = DISABLED)
            self.flag_checkbouton_connexions_paquets = 1
        elif self.flag_checkbouton_connexions_paquets ==1:
            self.bouton_connexions_paquets.config(state = NORMAL)
            self.flag_checkbouton_connexions_paquets = 0

    # Action on bouton Generation code VHDL
    def on_buttonGenerate_clicked(self):
        print("Generate the NOC files")
        self.generate_vhdl_file()


    def generate_configurable_part1(self):
        outputdir = "./Noc0__"
        if not os.path.exists(outputdir):
            os.makedirs(outputdir)
        self.nbr_R = int(self.entry_nbr_routeur.get())
        #self.nbr_M = [0 for i in range(self.nbr_R)]
        #self.nbr_S = [0 for i in range(self.nbr_R)]
        self.nbr_M =0
        self.nbr_S =0
		
		# Calcul de la somme totale d'interface maître et d'interface esclave dans le réseau
        for r in range(int(self.entry_nbr_routeur.get())):
            self.nbr_M = int(self.damierNbrMaitre[r].get()) + self.nbr_M
            self.nbr_S = int(self.damierNbrEsclave[r].get()) + self.nbr_S
			
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

        fw= open(outputdir + "/noc_config_configurable_part1.vhd", 'w')
        
        fw.write("%s" %ch)
        fw.write('constant TOTAL_MASTER_NB          : integer := %d ;\n' %self.nbr_M)
        fw.write('constant TOTAL_SLAVE_NB           : integer := %d ;\n' %self.nbr_S)
        fw.write('constant TOTAL_ROUTING_PORT_NB    : integer := %d ;\n' %self.nbr_RP_Global)
        fw.write('constant TOTAL_ROUTER_NB          : integer := %d ;\n' %self.nbr_R)
        fw.close()



    def generate_fixed_part(self):
        outputdir = "./Noc0__"
        if not os.path.exists(outputdir):
            os.makedirs(outputdir)
        self.nbr_R = int(self.entry_nbr_routeur.get())
        self.nbr_M = [0 for i in range(self.nbr_R)]
        self.nbr_S = [0 for i in range(self.nbr_R)]

        for r in range(int(self.entry_nbr_routeur.get())):
            self.nbr_M[r] = int(self.damierNbrMaitre[r].get())
            self.nbr_S[r] = int(self.damierNbrEsclave[r].get())

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
        get_bin = lambda x, n: format(x, 'b').zfill(n)
        for r in range(self.nbr_R):
            fw.write('constant ROUTER%d : regROUTERADD:= "%r"; \n' %(r,get_bin(r, 6)))
        fw.close()

        
    def generate_configurable_part2_1(self):
        outputdir = "./Noc0__"
        if not os.path.exists(outputdir):
            os.makedirs(outputdir)
        self.nbr_R = int(self.entry_nbr_routeur.get())
        self.nbr_M = [0 for i in range(self.nbr_R)]
        self.nbr_S = [0 for i in range(self.nbr_R)]

        for r in range(int(self.entry_nbr_routeur.get())):
            self.nbr_M[r] = int(self.damierNbrMaitre[r].get())
            self.nbr_S[r] = int(self.damierNbrEsclave[r].get())
        ch='''
----------------------------------------------------------------
				 ----- CONFIGURABLE PART  -----
----------------------------------------------------------------

------ 1) MASTER, SLAVE and ROUTING PORT NUMBERS by ROUTER ------
--for each router, declare the number of master interface port(s), slave interface port(s) and routing port(s)
constant R0_MASTER_SLAVE_ROUTPORT_NB : record_master_routport_slave_nb_by_router :=(4,5,2);
constant R1_MASTER_SLAVE_ROUTPORT_NB : record_master_routport_slave_nb_by_router :=(0,2,4);
constant R2_MASTER_SLAVE_ROUTPORT_NB : record_master_routport_slave_nb_by_router :=(4,1,1);
constant R3_MASTER_SLAVE_ROUTPORT_NB : record_master_routport_slave_nb_by_router :=(3,0,3);
constant R4_MASTER_SLAVE_ROUTPORT_NB : record_master_routport_slave_nb_by_router :=(4,4,3);
constant R5_MASTER_SLAVE_ROUTPORT_NB : record_master_routport_slave_nb_by_router :=(1,1,1);

-- => AGGREGATING ARRAY <= --
--aggregate all the "Ri_MASTER_SLAVE_ROUTPORT_NB" in this array
constant ALL_ROUTER_MASTER_SLAVE_ROUTPORT_NB : array_all_record_master_routport_slave_nb_by_router:=(
	R0_MASTER_SLAVE_ROUTPORT_NB,
	R1_MASTER_SLAVE_ROUTPORT_NB,
	R2_MASTER_SLAVE_ROUTPORT_NB,
	R3_MASTER_SLAVE_ROUTPORT_NB,
	R4_MASTER_SLAVE_ROUTPORT_NB,
	R5_MASTER_SLAVE_ROUTPORT_NB
);
     
'''    
        fw= open(outputdir + "/noc_config_configurable_part2_1.vhd", 'w')
        fw.write("%s" %ch)
        fw.close()


        
    def generate_configurable_part2_2(self):
        outputdir = "./Noc0__"
        self.nbr_R = int(self.entry_nbr_routeur.get())
        self.nbr_M = [0 for i in range(self.nbr_R)]
        self.nbr_S = [0 for i in range(self.nbr_R)]

        for r in range(int(self.entry_nbr_routeur.get())):
            self.nbr_M[r] = int(self.damierNbrMaitre[r].get())
            self.nbr_S[r] = int(self.damierNbrEsclave[r].get())
        ch='''
------ 2) MASTER and SLAVE RANKS ------
--a vector composed of all the masters and a vector composed of all the slaves are used to assignate
--the master and slave interface signals to each router. These ranks are used to indicate at which location
--are situated the first master interface and the slave interface of each router in the vectors containing all master
--signals and all slave signals.
--These 2 variables must have a value for each router:
-- a) The first value is always '0'
-- b) If the current router does not have any MASTER/SLAVE the value must be '0' (MASTER for MASTER_RANK and SLAVE for SLAVE_RANK)
-- c) The value for the next router is equal to the current value plus the number of MASTER/SLAVE in the current router (cumulated sum of all the precedent MASTER/SLAVE)
constant MASTER_RANK : master_rank_in_vector := (0,0,4,8,11,15);
constant SLAVE_RANK  : slave_rank_in_vector  := (0,5,7,0,8,12);

        '''
        fw= open(outputdir + "/noc_config_configurable_part2_2.vhd", 'w')
        fw.write("%s" %ch)
        fw.close()


        
    def generate_configurable_part2_3(self):
        outputdir = "./Noc0__"
        if not os.path.exists(outputdir):
            os.makedirs(outputdir)
        self.nbr_R = int(self.entry_nbr_routeur.get())
        self.nbr_M = [0 for i in range(self.nbr_R)]
        self.nbr_S = [0 for i in range(self.nbr_R)]

        for r in range(int(self.entry_nbr_routeur.get())):
            self.nbr_M[r] = int(self.damierNbrMaitre[r].get())
            self.nbr_S[r] = int(self.damierNbrEsclave[r].get())
        ch='''
------ 3) ROUTER CONNEXIONS (topology)------
--define a record for each connexion between routers
--wgeb two routers are connected : only one ROUTER_CONNEXION constant must be defined
--4 values to define for each connexion:
-- 1) SOURCE_ROUTER					
-- 2) SOURCE_ROUTING_PORT				
-- 3) DESTINATION_ROUTER				
-- 4) DESTINATION_ROUTING_PORT		
constant ROUTER_CONNEXION_0 : record_router_connexion :=(0,9,1,2);
constant ROUTER_CONNEXION_1 : record_router_connexion :=(0,10,3,3);  
constant ROUTER_CONNEXION_2 : record_router_connexion :=(1,4,3,4); 
constant ROUTER_CONNEXION_3 : record_router_connexion :=(1,5,4,10);
constant ROUTER_CONNEXION_4 : record_router_connexion :=(2,5,1,3);
constant ROUTER_CONNEXION_5 : record_router_connexion :=(3,5,4,8); 
constant ROUTER_CONNEXION_6 : record_router_connexion :=(4,9,5,1);

-- => AGGREGATING ARRAY <= --
constant ALL_ROUTER_CONNEXIONS : array_all_router_connexion:=(
	ROUTER_CONNEXION_0,
	ROUTER_CONNEXION_1,
	ROUTER_CONNEXION_2,
	ROUTER_CONNEXION_3,
	ROUTER_CONNEXION_4,
	ROUTER_CONNEXION_5,
	ROUTER_CONNEXION_6
);
  
        '''
        fw= open(outputdir + "/noc_config_configurable_part2_3.vhd", 'w')
        fw.write("%s" %ch)
        fw.close()
        
    def generate_configurable_part2_4(self):
        outputdir = "./Noc0__"
        self.nbr_R = int(self.entry_nbr_routeur.get())
        self.nbr_M = [0 for i in range(self.nbr_R)]
        self.nbr_S = [0 for i in range(self.nbr_R)]

        for r in range(int(self.entry_nbr_routeur.get())):
            self.nbr_M[r] = int(self.damierNbrMaitre[r].get())
            self.nbr_S[r] = int(self.damierNbrEsclave[r].get())
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
constant R0_PACKET_INTERFACE_PORT_ADD : packet_interface_portadd_vector := (1,1,1,1,2,2,2,2,2,3,3,0,0,0,0,0); 
constant R1_PACKET_INTERFACE_PORT_ADD : packet_interface_portadd_vector := (2,2,3,3,3,3,0,0,0,0,0,0,0,0,0,0);
constant R2_PACKET_INTERFACE_PORT_ADD : packet_interface_portadd_vector := (1,1,1,1,2,3,0,0,0,0,0,0,0,0,0,0); 
constant R3_PACKET_INTERFACE_PORT_ADD : packet_interface_portadd_vector := (1,1,1,3,3,3,0,0,0,0,0,0,0,0,0,0); 
constant R4_PACKET_INTERFACE_PORT_ADD : packet_interface_portadd_vector := (1,1,1,1,2,2,2,2,3,3,3,0,0,0,0,0);
constant R5_PACKET_INTERFACE_PORT_ADD : packet_interface_portadd_vector := (1,2,3,0,0,0,0,0,0,0,0,0,0,0,0,0); 

-- => AGGREGATING ARRAY <= --
constant ALL_ROUTER_PACKET_INTERFACE_PORT_ADD : array_all_router_packet_interface_portadd:=(
	R0_PACKET_INTERFACE_PORT_ADD,
	R1_PACKET_INTERFACE_PORT_ADD,
	R2_PACKET_INTERFACE_PORT_ADD,
	R3_PACKET_INTERFACE_PORT_ADD,
	R4_PACKET_INTERFACE_PORT_ADD,
	R5_PACKET_INTERFACE_PORT_ADD
);
	
        '''
        fw= open(outputdir + "/noc_config_configurable_part2_4.vhd", 'w')
        fw.write("%s" %ch)
        fw.close()
        
		
		
    def generate_configurable_part2_5(self):
        outputdir = "./Noc0__"
        self.nbr_R = int(self.entry_nbr_routeur.get())
        self.nbr_M = [0 for i in range(self.nbr_R)]
        self.nbr_S = [0 for i in range(self.nbr_R)]

        for r in range(int(self.entry_nbr_routeur.get())):
            self.nbr_M[r] = int(self.damierNbrMaitre[r].get())
            self.nbr_S[r] = int(self.damierNbrEsclave[r].get())
        ch='''
------ 5) ADDRESS DECODER TABLE SIZES  ------
--define the size of each address decoding table of each master of each router (in the number of rules that it contain)
constant ROUTER0_MASTER0_ADD_DECOD_TABLE_SIZE 	: integer := 9;
constant ROUTER0_MASTER1_ADD_DECOD_TABLE_SIZE 	: integer := 8;
constant ROUTER0_MASTER2_ADD_DECOD_TABLE_SIZE 	: integer := 8;
constant ROUTER0_MASTER3_ADD_DECOD_TABLE_SIZE 	: integer := 8;
																				
constant ROUTER2_MASTER0_ADD_DECOD_TABLE_SIZE 	: integer := 8;
constant ROUTER2_MASTER1_ADD_DECOD_TABLE_SIZE 	: integer := 8;
constant ROUTER2_MASTER2_ADD_DECOD_TABLE_SIZE 	: integer := 8;
constant ROUTER2_MASTER3_ADD_DECOD_TABLE_SIZE 	: integer := 8;
																				
constant ROUTER3_MASTER0_ADD_DECOD_TABLE_SIZE 	: integer := 8;
constant ROUTER3_MASTER1_ADD_DECOD_TABLE_SIZE 	: integer := 8;
constant ROUTER3_MASTER2_ADD_DECOD_TABLE_SIZE 	: integer := 8;
																				
constant ROUTER4_MASTER0_ADD_DECOD_TABLE_SIZE 	: integer := 8;
constant ROUTER4_MASTER1_ADD_DECOD_TABLE_SIZE 	: integer := 8;
constant ROUTER4_MASTER2_ADD_DECOD_TABLE_SIZE 	: integer := 8;
constant ROUTER4_MASTER3_ADD_DECOD_TABLE_SIZE 	: integer := 8;
																				
constant ROUTER5_MASTER0_ADD_DECOD_TABLE_SIZE 	: integer := 9;

--define the total number of address decoding rules (for all the masters)
constant TOTAL_ADDRESS_DECOD_SIZE 				: integer := 130;

	
        '''
        fw= open(outputdir + "/noc_config_configurable_part2_4.vhd", 'w')
        fw.write("%s" %ch)
        fw.close()
		

		
    def generate_configurable_part2_6(self):
        outputdir = "./Noc0__"
        self.nbr_R = int(self.entry_nbr_routeur.get())
        self.nbr_M = [0 for i in range(self.nbr_R)]
        self.nbr_S = [0 for i in range(self.nbr_R)]

        for r in range(int(self.entry_nbr_routeur.get())):
            self.nbr_M[r] = int(self.damierNbrMaitre[r].get())
            self.nbr_S[r] = int(self.damierNbrEsclave[r].get())
        ch='''
------ 6) SLAVE ADDRESS MAPPING (32-bits) ------
--This address mapping is used inside the address decoding tables.
--for each master of each router, define the address mapping of slave interfaces that can be reached by the master 
--for each slave -> define a BASE_ADD and a HIGH_ADD
constant 	ROUTER0_MASTER0_address_mapping_for_ROUTER0_SLAVE4_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"00000000";
constant 	ROUTER0_MASTER0_address_mapping_for_ROUTER0_SLAVE4_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"00FFFFFF";
constant 	ROUTER0_MASTER0_address_mapping_for_ROUTER0_SLAVE5_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"01000000";
constant 	ROUTER0_MASTER0_address_mapping_for_ROUTER0_SLAVE5_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"01FFFFFF";
constant 	ROUTER0_MASTER0_address_mapping_for_ROUTER0_SLAVE6_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"02000000";
constant 	ROUTER0_MASTER0_address_mapping_for_ROUTER0_SLAVE6_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"02FFFFFF";
constant 	ROUTER0_MASTER0_address_mapping_for_ROUTER0_SLAVE7_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"03000000";
constant 	ROUTER0_MASTER0_address_mapping_for_ROUTER0_SLAVE7_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"03FFFFFF";
constant 	ROUTER0_MASTER0_address_mapping_for_ROUTER0_SLAVE8_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"04000000";
constant 	ROUTER0_MASTER0_address_mapping_for_ROUTER0_SLAVE8_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"04FFFFFF";
constant 	ROUTER0_MASTER0_address_mapping_for_ROUTER1_SLAVE0_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"10000000";
constant 	ROUTER0_MASTER0_address_mapping_for_ROUTER1_SLAVE0_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"10FFFFFF";
constant 	ROUTER0_MASTER0_address_mapping_for_ROUTER1_SLAVE1_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"11000000";
constant 	ROUTER0_MASTER0_address_mapping_for_ROUTER1_SLAVE1_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"11FFFFFF";
constant 	ROUTER0_MASTER0_address_mapping_for_ROUTER2_SLAVE4_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"20000000";
constant	ROUTER0_MASTER0_address_mapping_for_ROUTER2_SLAVE4_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"20FFFFFF";
constant 	ROUTER0_MASTER0_address_mapping_for_ROUTER5_SLAVE1_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"50000000";
constant	ROUTER0_MASTER0_address_mapping_for_ROUTER5_SLAVE1_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"50FFFFFF";

constant 	ROUTER0_MASTER1_address_mapping_for_ROUTER4_SLAVE4_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"40000000";
constant 	ROUTER0_MASTER1_address_mapping_for_ROUTER4_SLAVE4_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"40FFFFFF";
constant 	ROUTER0_MASTER1_address_mapping_for_ROUTER0_SLAVE5_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"01000000";
constant 	ROUTER0_MASTER1_address_mapping_for_ROUTER0_SLAVE5_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"01FFFFFF";
constant 	ROUTER0_MASTER1_address_mapping_for_ROUTER0_SLAVE6_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"02000000";
constant 	ROUTER0_MASTER1_address_mapping_for_ROUTER0_SLAVE6_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"02FFFFFF";
constant 	ROUTER0_MASTER1_address_mapping_for_ROUTER0_SLAVE7_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"03000000";
constant 	ROUTER0_MASTER1_address_mapping_for_ROUTER0_SLAVE7_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"03FFFFFF";
constant 	ROUTER0_MASTER1_address_mapping_for_ROUTER0_SLAVE8_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"04000000";
constant 	ROUTER0_MASTER1_address_mapping_for_ROUTER0_SLAVE8_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"04FFFFFF";
constant 	ROUTER0_MASTER1_address_mapping_for_ROUTER1_SLAVE0_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"10000000";
constant 	ROUTER0_MASTER1_address_mapping_for_ROUTER1_SLAVE0_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"10FFFFFF";
constant 	ROUTER0_MASTER1_address_mapping_for_ROUTER1_SLAVE1_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"11000000";
constant 	ROUTER0_MASTER1_address_mapping_for_ROUTER1_SLAVE1_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"11FFFFFF";
constant 	ROUTER0_MASTER1_address_mapping_for_ROUTER2_SLAVE4_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"20000000";
constant	ROUTER0_MASTER1_address_mapping_for_ROUTER2_SLAVE4_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"20FFFFFF";

constant 	ROUTER0_MASTER2_address_mapping_for_ROUTER4_SLAVE4_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"40000000";
constant 	ROUTER0_MASTER2_address_mapping_for_ROUTER4_SLAVE4_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"40FFFFFF";
constant 	ROUTER0_MASTER2_address_mapping_for_ROUTER0_SLAVE5_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"01000000";
constant 	ROUTER0_MASTER2_address_mapping_for_ROUTER0_SLAVE5_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"01FFFFFF";
constant 	ROUTER0_MASTER2_address_mapping_for_ROUTER0_SLAVE6_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"02000000";
constant 	ROUTER0_MASTER2_address_mapping_for_ROUTER0_SLAVE6_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"02FFFFFF";
constant 	ROUTER0_MASTER2_address_mapping_for_ROUTER0_SLAVE7_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"03000000";
constant 	ROUTER0_MASTER2_address_mapping_for_ROUTER0_SLAVE7_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"03FFFFFF";
constant 	ROUTER0_MASTER2_address_mapping_for_ROUTER0_SLAVE8_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"04000000";
constant 	ROUTER0_MASTER2_address_mapping_for_ROUTER0_SLAVE8_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"04FFFFFF";
constant 	ROUTER0_MASTER2_address_mapping_for_ROUTER1_SLAVE0_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"10000000";
constant 	ROUTER0_MASTER2_address_mapping_for_ROUTER1_SLAVE0_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"10FFFFFF";
constant 	ROUTER0_MASTER2_address_mapping_for_ROUTER1_SLAVE1_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"11000000";
constant 	ROUTER0_MASTER2_address_mapping_for_ROUTER1_SLAVE1_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"11FFFFFF";
constant 	ROUTER0_MASTER2_address_mapping_for_ROUTER2_SLAVE4_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"20000000";
constant	ROUTER0_MASTER2_address_mapping_for_ROUTER2_SLAVE4_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"20FFFFFF";

constant 	ROUTER0_MASTER3_address_mapping_for_ROUTER4_SLAVE6_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"42000000";
constant 	ROUTER0_MASTER3_address_mapping_for_ROUTER4_SLAVE6_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"42FFFFFF";
constant 	ROUTER0_MASTER3_address_mapping_for_ROUTER0_SLAVE5_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"01000000";
constant 	ROUTER0_MASTER3_address_mapping_for_ROUTER0_SLAVE5_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"01FFFFFF";
constant 	ROUTER0_MASTER3_address_mapping_for_ROUTER0_SLAVE6_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"02000000";
constant 	ROUTER0_MASTER3_address_mapping_for_ROUTER0_SLAVE6_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"02FFFFFF";
constant 	ROUTER0_MASTER3_address_mapping_for_ROUTER0_SLAVE7_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"03000000";
constant 	ROUTER0_MASTER3_address_mapping_for_ROUTER0_SLAVE7_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"03FFFFFF";
constant 	ROUTER0_MASTER3_address_mapping_for_ROUTER0_SLAVE8_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"04000000";
constant 	ROUTER0_MASTER3_address_mapping_for_ROUTER0_SLAVE8_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"04FFFFFF";
constant 	ROUTER0_MASTER3_address_mapping_for_ROUTER1_SLAVE0_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"10000000";
constant 	ROUTER0_MASTER3_address_mapping_for_ROUTER1_SLAVE0_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"10FFFFFF";
constant 	ROUTER0_MASTER3_address_mapping_for_ROUTER1_SLAVE1_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"11000000";
constant 	ROUTER0_MASTER3_address_mapping_for_ROUTER1_SLAVE1_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"11FFFFFF";
constant 	ROUTER0_MASTER3_address_mapping_for_ROUTER2_SLAVE4_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"20000000";
constant	ROUTER0_MASTER3_address_mapping_for_ROUTER2_SLAVE4_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"20FFFFFF";

constant 	ROUTER2_MASTER0_address_mapping_for_ROUTER4_SLAVE4_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"000AAA00";
constant 	ROUTER2_MASTER0_address_mapping_for_ROUTER4_SLAVE4_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"00FFFFFF";
constant 	ROUTER2_MASTER0_address_mapping_for_ROUTER4_SLAVE5_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"01000000";
constant 	ROUTER2_MASTER0_address_mapping_for_ROUTER4_SLAVE5_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"01FFFFFF";
constant 	ROUTER2_MASTER0_address_mapping_for_ROUTER4_SLAVE6_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"02000000";
constant 	ROUTER2_MASTER0_address_mapping_for_ROUTER4_SLAVE6_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"02FFFFFF";
constant 	ROUTER2_MASTER0_address_mapping_for_ROUTER4_SLAVE7_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"03000000";
constant 	ROUTER2_MASTER0_address_mapping_for_ROUTER4_SLAVE7_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"03FFFFFF";
constant 	ROUTER2_MASTER0_address_mapping_for_ROUTER0_SLAVE8_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"04000000";
constant 	ROUTER2_MASTER0_address_mapping_for_ROUTER0_SLAVE8_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"04FFFFFF";
constant 	ROUTER2_MASTER0_address_mapping_for_ROUTER1_SLAVE0_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"10000000";
constant 	ROUTER2_MASTER0_address_mapping_for_ROUTER1_SLAVE0_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"10FFFFFF";
constant 	ROUTER2_MASTER0_address_mapping_for_ROUTER1_SLAVE1_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"11000000";
constant 	ROUTER2_MASTER0_address_mapping_for_ROUTER1_SLAVE1_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"11FFFFFF";
constant 	ROUTER2_MASTER0_address_mapping_for_ROUTER2_SLAVE4_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"20000000";
constant	ROUTER2_MASTER0_address_mapping_for_ROUTER2_SLAVE4_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"20FFFFFF";

constant 	ROUTER2_MASTER1_address_mapping_for_ROUTER0_SLAVE4_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"00000000";
constant 	ROUTER2_MASTER1_address_mapping_for_ROUTER0_SLAVE4_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"00FFFFFF";
constant 	ROUTER2_MASTER1_address_mapping_for_ROUTER0_SLAVE5_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"01000000";
constant 	ROUTER2_MASTER1_address_mapping_for_ROUTER0_SLAVE5_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"01FFFFFF";
constant 	ROUTER2_MASTER1_address_mapping_for_ROUTER0_SLAVE6_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"02000000";
constant 	ROUTER2_MASTER1_address_mapping_for_ROUTER0_SLAVE6_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"02FFFFFF";
constant 	ROUTER2_MASTER1_address_mapping_for_ROUTER0_SLAVE7_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"03000000";
constant 	ROUTER2_MASTER1_address_mapping_for_ROUTER0_SLAVE7_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"03FFFFFF";
constant 	ROUTER2_MASTER1_address_mapping_for_ROUTER0_SLAVE8_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"04000000";
constant 	ROUTER2_MASTER1_address_mapping_for_ROUTER0_SLAVE8_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"04FFFFFF";
constant 	ROUTER2_MASTER1_address_mapping_for_ROUTER1_SLAVE0_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"10000000";
constant 	ROUTER2_MASTER1_address_mapping_for_ROUTER1_SLAVE0_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"10FFFFFF";
constant 	ROUTER2_MASTER1_address_mapping_for_ROUTER1_SLAVE1_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"11000000";
constant 	ROUTER2_MASTER1_address_mapping_for_ROUTER1_SLAVE1_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"11FFFFFF";
constant 	ROUTER2_MASTER1_address_mapping_for_ROUTER2_SLAVE4_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"20000000";
constant	ROUTER2_MASTER1_address_mapping_for_ROUTER2_SLAVE4_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"20FFFFFF";

constant 	ROUTER2_MASTER2_address_mapping_for_ROUTER0_SLAVE4_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"00000000";
constant 	ROUTER2_MASTER2_address_mapping_for_ROUTER0_SLAVE4_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"00FFFFFF";
constant 	ROUTER2_MASTER2_address_mapping_for_ROUTER0_SLAVE5_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"01000000";
constant 	ROUTER2_MASTER2_address_mapping_for_ROUTER0_SLAVE5_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"01FFFFFF";
constant 	ROUTER2_MASTER2_address_mapping_for_ROUTER0_SLAVE6_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"02000000";
constant 	ROUTER2_MASTER2_address_mapping_for_ROUTER0_SLAVE6_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"02FFFFFF";
constant 	ROUTER2_MASTER2_address_mapping_for_ROUTER0_SLAVE7_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"03000000";
constant 	ROUTER2_MASTER2_address_mapping_for_ROUTER0_SLAVE7_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"03FFFFFF";
constant 	ROUTER2_MASTER2_address_mapping_for_ROUTER0_SLAVE8_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"04000000";
constant 	ROUTER2_MASTER2_address_mapping_for_ROUTER0_SLAVE8_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"04FFFFFF";
constant 	ROUTER2_MASTER2_address_mapping_for_ROUTER1_SLAVE0_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"10000000";
constant 	ROUTER2_MASTER2_address_mapping_for_ROUTER1_SLAVE0_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"10FFFFFF";
constant 	ROUTER2_MASTER2_address_mapping_for_ROUTER1_SLAVE1_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"11000000";
constant 	ROUTER2_MASTER2_address_mapping_for_ROUTER1_SLAVE1_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"11FFFFFF";
constant 	ROUTER2_MASTER2_address_mapping_for_ROUTER2_SLAVE4_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"20000000";
constant	ROUTER2_MASTER2_address_mapping_for_ROUTER2_SLAVE4_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"20FFFFFF";

constant 	ROUTER2_MASTER3_address_mapping_for_ROUTER0_SLAVE4_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"00000000";
constant 	ROUTER2_MASTER3_address_mapping_for_ROUTER0_SLAVE4_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"00FFFFFF";
constant 	ROUTER2_MASTER3_address_mapping_for_ROUTER0_SLAVE5_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"01000000";
constant 	ROUTER2_MASTER3_address_mapping_for_ROUTER0_SLAVE5_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"01FFFFFF";
constant 	ROUTER2_MASTER3_address_mapping_for_ROUTER0_SLAVE6_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"02000000";
constant 	ROUTER2_MASTER3_address_mapping_for_ROUTER0_SLAVE6_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"02FFFFFF";
constant 	ROUTER2_MASTER3_address_mapping_for_ROUTER0_SLAVE7_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"03000000";
constant 	ROUTER2_MASTER3_address_mapping_for_ROUTER0_SLAVE7_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"03FFFFFF";
constant 	ROUTER2_MASTER3_address_mapping_for_ROUTER0_SLAVE8_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"04000000";
constant 	ROUTER2_MASTER3_address_mapping_for_ROUTER0_SLAVE8_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"04FFFFFF";
constant 	ROUTER2_MASTER3_address_mapping_for_ROUTER1_SLAVE0_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"10000000";
constant 	ROUTER2_MASTER3_address_mapping_for_ROUTER1_SLAVE0_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"10FFFFFF";
constant 	ROUTER2_MASTER3_address_mapping_for_ROUTER1_SLAVE1_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"11000000";
constant 	ROUTER2_MASTER3_address_mapping_for_ROUTER1_SLAVE1_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"11FFFFFF";
constant 	ROUTER2_MASTER3_address_mapping_for_ROUTER2_SLAVE4_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"20000000";
constant	ROUTER2_MASTER3_address_mapping_for_ROUTER2_SLAVE4_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"20FFFFFF";


constant 	ROUTER3_MASTER0_address_mapping_for_ROUTER0_SLAVE4_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"00000000";
constant 	ROUTER3_MASTER0_address_mapping_for_ROUTER0_SLAVE4_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"00FFFFFF";
constant 	ROUTER3_MASTER0_address_mapping_for_ROUTER0_SLAVE5_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"01000000";
constant 	ROUTER3_MASTER0_address_mapping_for_ROUTER0_SLAVE5_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"01FFFFFF";
constant 	ROUTER3_MASTER0_address_mapping_for_ROUTER0_SLAVE6_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"02000000";
constant 	ROUTER3_MASTER0_address_mapping_for_ROUTER0_SLAVE6_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"02FFFFFF";
constant 	ROUTER3_MASTER0_address_mapping_for_ROUTER0_SLAVE7_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"03000000";
constant 	ROUTER3_MASTER0_address_mapping_for_ROUTER0_SLAVE7_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"03FFFFFF";
constant 	ROUTER3_MASTER0_address_mapping_for_ROUTER0_SLAVE8_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"04000000";
constant 	ROUTER3_MASTER0_address_mapping_for_ROUTER0_SLAVE8_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"04FFFFFF";
constant 	ROUTER3_MASTER0_address_mapping_for_ROUTER1_SLAVE0_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"10000000";
constant 	ROUTER3_MASTER0_address_mapping_for_ROUTER1_SLAVE0_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"10FFFFFF";
constant 	ROUTER3_MASTER0_address_mapping_for_ROUTER1_SLAVE1_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"11000000";
constant 	ROUTER3_MASTER0_address_mapping_for_ROUTER1_SLAVE1_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"11FFFFFF";
constant 	ROUTER3_MASTER0_address_mapping_for_ROUTER2_SLAVE4_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"20000000";
constant	ROUTER3_MASTER0_address_mapping_for_ROUTER2_SLAVE4_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"20FFFFFF";

constant 	ROUTER3_MASTER1_address_mapping_for_ROUTER0_SLAVE4_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"00000000";
constant 	ROUTER3_MASTER1_address_mapping_for_ROUTER0_SLAVE4_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"00FFFFFF";
constant 	ROUTER3_MASTER1_address_mapping_for_ROUTER0_SLAVE5_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"01000000";
constant 	ROUTER3_MASTER1_address_mapping_for_ROUTER0_SLAVE5_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"01FFFFFF";
constant 	ROUTER3_MASTER1_address_mapping_for_ROUTER0_SLAVE6_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"02000000";
constant 	ROUTER3_MASTER1_address_mapping_for_ROUTER0_SLAVE6_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"02FFFFFF";
constant 	ROUTER3_MASTER1_address_mapping_for_ROUTER0_SLAVE7_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"03000000";
constant 	ROUTER3_MASTER1_address_mapping_for_ROUTER0_SLAVE7_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"03FFFFFF";
constant 	ROUTER3_MASTER1_address_mapping_for_ROUTER0_SLAVE8_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"04000000";
constant 	ROUTER3_MASTER1_address_mapping_for_ROUTER0_SLAVE8_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"04FFFFFF";
constant 	ROUTER3_MASTER1_address_mapping_for_ROUTER1_SLAVE0_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"10000000";
constant 	ROUTER3_MASTER1_address_mapping_for_ROUTER1_SLAVE0_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"10FFFFFF";
constant 	ROUTER3_MASTER1_address_mapping_for_ROUTER1_SLAVE1_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"11000000";
constant 	ROUTER3_MASTER1_address_mapping_for_ROUTER1_SLAVE1_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"11FFFFFF";
constant 	ROUTER3_MASTER1_address_mapping_for_ROUTER2_SLAVE4_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"20000000";
constant	ROUTER3_MASTER1_address_mapping_for_ROUTER2_SLAVE4_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"20FFFFFF";

constant 	ROUTER3_MASTER2_address_mapping_for_ROUTER0_SLAVE4_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"00000000";
constant 	ROUTER3_MASTER2_address_mapping_for_ROUTER0_SLAVE4_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"00FFFFFF";
constant 	ROUTER3_MASTER2_address_mapping_for_ROUTER0_SLAVE5_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"01000000";
constant 	ROUTER3_MASTER2_address_mapping_for_ROUTER0_SLAVE5_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"01FFFFFF";
constant 	ROUTER3_MASTER2_address_mapping_for_ROUTER0_SLAVE6_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"02000000";
constant 	ROUTER3_MASTER2_address_mapping_for_ROUTER0_SLAVE6_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"02FFFFFF";
constant 	ROUTER3_MASTER2_address_mapping_for_ROUTER0_SLAVE7_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"03000000";
constant 	ROUTER3_MASTER2_address_mapping_for_ROUTER0_SLAVE7_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"03FFFFFF";
constant 	ROUTER3_MASTER2_address_mapping_for_ROUTER0_SLAVE8_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"04000000";
constant 	ROUTER3_MASTER2_address_mapping_for_ROUTER0_SLAVE8_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"04FFFFFF";
constant 	ROUTER3_MASTER2_address_mapping_for_ROUTER1_SLAVE0_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"10000000";
constant 	ROUTER3_MASTER2_address_mapping_for_ROUTER1_SLAVE0_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"10FFFFFF";
constant 	ROUTER3_MASTER2_address_mapping_for_ROUTER1_SLAVE1_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"11000000";
constant 	ROUTER3_MASTER2_address_mapping_for_ROUTER1_SLAVE1_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"11FFFFFF";
constant 	ROUTER3_MASTER2_address_mapping_for_ROUTER2_SLAVE4_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"20000000";
constant	ROUTER3_MASTER2_address_mapping_for_ROUTER2_SLAVE4_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"20FFFFFF";


constant 	ROUTER4_MASTER0_address_mapping_for_ROUTER0_SLAVE4_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"00000000";
constant 	ROUTER4_MASTER0_address_mapping_for_ROUTER0_SLAVE4_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"00FFFFFF";
constant 	ROUTER4_MASTER0_address_mapping_for_ROUTER0_SLAVE5_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"01000000";
constant 	ROUTER4_MASTER0_address_mapping_for_ROUTER0_SLAVE5_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"01FFFFFF";
constant 	ROUTER4_MASTER0_address_mapping_for_ROUTER0_SLAVE6_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"02000000";
constant 	ROUTER4_MASTER0_address_mapping_for_ROUTER0_SLAVE6_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"02FFFFFF";
constant 	ROUTER4_MASTER0_address_mapping_for_ROUTER0_SLAVE7_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"03000000";
constant 	ROUTER4_MASTER0_address_mapping_for_ROUTER0_SLAVE7_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"03FFFFFF";
constant 	ROUTER4_MASTER0_address_mapping_for_ROUTER0_SLAVE8_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"04000000";
constant 	ROUTER4_MASTER0_address_mapping_for_ROUTER0_SLAVE8_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"04FFFFFF";
constant 	ROUTER4_MASTER0_address_mapping_for_ROUTER1_SLAVE0_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"10000000";
constant 	ROUTER4_MASTER0_address_mapping_for_ROUTER1_SLAVE0_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"10FFFFFF";
constant 	ROUTER4_MASTER0_address_mapping_for_ROUTER1_SLAVE1_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"11000000";
constant 	ROUTER4_MASTER0_address_mapping_for_ROUTER1_SLAVE1_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"11FFFFFF";
constant 	ROUTER4_MASTER0_address_mapping_for_ROUTER2_SLAVE4_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"20000000";
constant	ROUTER4_MASTER0_address_mapping_for_ROUTER2_SLAVE4_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"20FFFFFF";

constant 	ROUTER4_MASTER1_address_mapping_for_ROUTER0_SLAVE4_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"00000000";
constant 	ROUTER4_MASTER1_address_mapping_for_ROUTER0_SLAVE4_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"00FFFFFF";
constant 	ROUTER4_MASTER1_address_mapping_for_ROUTER0_SLAVE5_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"01000000";
constant 	ROUTER4_MASTER1_address_mapping_for_ROUTER0_SLAVE5_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"01FFFFFF";
constant 	ROUTER4_MASTER1_address_mapping_for_ROUTER0_SLAVE6_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"02000000";
constant 	ROUTER4_MASTER1_address_mapping_for_ROUTER0_SLAVE6_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"02FFFFFF";
constant 	ROUTER4_MASTER1_address_mapping_for_ROUTER0_SLAVE7_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"03000000";
constant 	ROUTER4_MASTER1_address_mapping_for_ROUTER0_SLAVE7_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"03FFFFFF";
constant 	ROUTER4_MASTER1_address_mapping_for_ROUTER0_SLAVE8_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"04000000";
constant 	ROUTER4_MASTER1_address_mapping_for_ROUTER0_SLAVE8_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"04FFFFFF";
constant 	ROUTER4_MASTER1_address_mapping_for_ROUTER1_SLAVE0_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"10000000";
constant 	ROUTER4_MASTER1_address_mapping_for_ROUTER1_SLAVE0_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"10FFFFFF";
constant 	ROUTER4_MASTER1_address_mapping_for_ROUTER1_SLAVE1_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"11000000";
constant 	ROUTER4_MASTER1_address_mapping_for_ROUTER1_SLAVE1_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"11FFFFFF";
constant 	ROUTER4_MASTER1_address_mapping_for_ROUTER2_SLAVE4_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"20000000";
constant	ROUTER4_MASTER1_address_mapping_for_ROUTER2_SLAVE4_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"20FFFFFF";

constant 	ROUTER4_MASTER2_address_mapping_for_ROUTER0_SLAVE4_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"00000000";
constant 	ROUTER4_MASTER2_address_mapping_for_ROUTER0_SLAVE4_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"00FFFFFF";
constant 	ROUTER4_MASTER2_address_mapping_for_ROUTER0_SLAVE5_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"01000000";
constant 	ROUTER4_MASTER2_address_mapping_for_ROUTER0_SLAVE5_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"01FFFFFF";
constant 	ROUTER4_MASTER2_address_mapping_for_ROUTER0_SLAVE6_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"02000000";
constant 	ROUTER4_MASTER2_address_mapping_for_ROUTER0_SLAVE6_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"02FFFFFF";
constant 	ROUTER4_MASTER2_address_mapping_for_ROUTER0_SLAVE7_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"03000000";
constant 	ROUTER4_MASTER2_address_mapping_for_ROUTER0_SLAVE7_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"03FFFFFF";
constant 	ROUTER4_MASTER2_address_mapping_for_ROUTER0_SLAVE8_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"04000000";
constant 	ROUTER4_MASTER2_address_mapping_for_ROUTER0_SLAVE8_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"04FFFFFF";
constant 	ROUTER4_MASTER2_address_mapping_for_ROUTER1_SLAVE0_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"10000000";
constant 	ROUTER4_MASTER2_address_mapping_for_ROUTER1_SLAVE0_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"10FFFFFF";
constant 	ROUTER4_MASTER2_address_mapping_for_ROUTER1_SLAVE1_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"11000000";
constant 	ROUTER4_MASTER2_address_mapping_for_ROUTER1_SLAVE1_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"11FFFFFF";
constant 	ROUTER4_MASTER2_address_mapping_for_ROUTER2_SLAVE4_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"20000000";
constant	ROUTER4_MASTER2_address_mapping_for_ROUTER2_SLAVE4_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"20FFFFFF";

constant 	ROUTER4_MASTER3_address_mapping_for_ROUTER0_SLAVE4_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"00000000";
constant 	ROUTER4_MASTER3_address_mapping_for_ROUTER0_SLAVE4_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"00FFFFFF";
constant 	ROUTER4_MASTER3_address_mapping_for_ROUTER0_SLAVE5_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"01000000";
constant 	ROUTER4_MASTER3_address_mapping_for_ROUTER0_SLAVE5_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"01FFFFFF";
constant 	ROUTER4_MASTER3_address_mapping_for_ROUTER0_SLAVE6_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"02000000";
constant 	ROUTER4_MASTER3_address_mapping_for_ROUTER0_SLAVE6_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"02FFFFFF";
constant 	ROUTER4_MASTER3_address_mapping_for_ROUTER0_SLAVE7_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"03000000";
constant 	ROUTER4_MASTER3_address_mapping_for_ROUTER0_SLAVE7_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"03FFFFFF";
constant 	ROUTER4_MASTER3_address_mapping_for_ROUTER0_SLAVE8_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"04000000";
constant 	ROUTER4_MASTER3_address_mapping_for_ROUTER0_SLAVE8_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"04FFFFFF";
constant 	ROUTER4_MASTER3_address_mapping_for_ROUTER1_SLAVE0_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"10000000";
constant 	ROUTER4_MASTER3_address_mapping_for_ROUTER1_SLAVE0_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"10FFFFFF";
constant 	ROUTER4_MASTER3_address_mapping_for_ROUTER1_SLAVE1_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"11000000";
constant 	ROUTER4_MASTER3_address_mapping_for_ROUTER1_SLAVE1_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"11FFFFFF";
constant 	ROUTER4_MASTER3_address_mapping_for_ROUTER2_SLAVE4_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"20000000";
constant	ROUTER4_MASTER3_address_mapping_for_ROUTER2_SLAVE4_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"20FFFFFF";


constant 	ROUTER5_MASTER0_address_mapping_for_ROUTER1_SLAVE0_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"10000000";
constant 	ROUTER5_MASTER0_address_mapping_for_ROUTER1_SLAVE0_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"10FFFFFF";
constant 	ROUTER5_MASTER0_address_mapping_for_ROUTER1_SLAVE1_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"11000000";
constant 	ROUTER5_MASTER0_address_mapping_for_ROUTER1_SLAVE1_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"11FFFFFF";
constant 	ROUTER5_MASTER0_address_mapping_for_ROUTER2_SLAVE4_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"20000000";
constant 	ROUTER5_MASTER0_address_mapping_for_ROUTER2_SLAVE4_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"20FFFFFF";
constant 	ROUTER5_MASTER0_address_mapping_for_ROUTER4_SLAVE4_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"40000000";
constant 	ROUTER5_MASTER0_address_mapping_for_ROUTER4_SLAVE4_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"40FFFFFF";
constant 	ROUTER5_MASTER0_address_mapping_for_ROUTER4_SLAVE5_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"41000000";
constant 	ROUTER5_MASTER0_address_mapping_for_ROUTER4_SLAVE5_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"41FFFFFF";
constant 	ROUTER5_MASTER0_address_mapping_for_ROUTER4_SLAVE6_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"42000000";
constant 	ROUTER5_MASTER0_address_mapping_for_ROUTER4_SLAVE6_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"42FFFFFF";
constant 	ROUTER5_MASTER0_address_mapping_for_ROUTER4_SLAVE7_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"43000000";
constant 	ROUTER5_MASTER0_address_mapping_for_ROUTER4_SLAVE7_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"43FFFFFF";
constant 	ROUTER5_MASTER0_address_mapping_for_ROUTER5_SLAVE1_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"50000000";
constant	ROUTER5_MASTER0_address_mapping_for_ROUTER5_SLAVE1_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"50FFFFFF";
constant 	ROUTER5_MASTER0_address_mapping_for_ROUTER0_SLAVE4_BASE_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"00000000";
constant	ROUTER5_MASTER0_address_mapping_for_ROUTER0_SLAVE4_HIGH_ADD 	: std_logic_vector(ADD_SIZE-1 downto 0):= X"00FFFFFF";


        
        '''
        fw= open(outputdir + "/noc_config_configurable_part2_6.vhd", 'w')
        fw.write("%s" %ch)
        fw.close()
        
    def generate_configurable_part2_7(self):
        outputdir = "./Noc0__"
        if not os.path.exists(outputdir):
            os.makedirs(outputdir)
        self.nbr_R = int(self.entry_nbr_routeur.get())
        self.nbr_M = [0 for i in range(self.nbr_R)]
        self.nbr_S = [0 for i in range(self.nbr_R)]

        for r in range(int(self.entry_nbr_routeur.get())):
            self.nbr_M[r] = int(self.damierNbrMaitre[r].get())
            self.nbr_S[r] = int(self.damierNbrEsclave[r].get())
        ch='''
---- 7) ROUTING TABLE CONTENTS ------
--define the address port that must take a packet to reach the DESTINATION ROUTER FROM the current ROUTER
--for each router a port address must be defined to reach all the other routers of the network
constant from_ROUTER0_to_ROUTER1_destination_port : regPORTADD:= ROUTINGPORT9;
constant from_ROUTER0_to_ROUTER2_destination_port : regPORTADD:= ROUTINGPORT9;
constant from_ROUTER0_to_ROUTER3_destination_port : regPORTADD:= ROUTINGPORT10;
constant from_ROUTER0_to_ROUTER4_destination_port : regPORTADD:= ROUTINGPORT9;
constant from_ROUTER0_to_ROUTER5_destination_port : regPORTADD:= ROUTINGPORT10;

constant from_ROUTER1_to_ROUTER0_destination_port : regPORTADD:= ROUTINGPORT2;
constant from_ROUTER1_to_ROUTER2_destination_port : regPORTADD:= ROUTINGPORT3;
constant from_ROUTER1_to_ROUTER3_destination_port : regPORTADD:= ROUTINGPORT4;
constant from_ROUTER1_to_ROUTER4_destination_port : regPORTADD:= ROUTINGPORT5;
constant from_ROUTER1_to_ROUTER5_destination_port : regPORTADD:= ROUTINGPORT5;

constant from_ROUTER2_to_ROUTER0_destination_port : regPORTADD:= ROUTINGPORT5;
constant from_ROUTER2_to_ROUTER1_destination_port : regPORTADD:= ROUTINGPORT5;
constant from_ROUTER2_to_ROUTER3_destination_port : regPORTADD:= ROUTINGPORT5;
constant from_ROUTER2_to_ROUTER4_destination_port : regPORTADD:= ROUTINGPORT5;
constant from_ROUTER2_to_ROUTER5_destination_port : regPORTADD:= ROUTINGPORT5;

constant from_ROUTER3_to_ROUTER0_destination_port : regPORTADD:= ROUTINGPORT3;
constant from_ROUTER3_to_ROUTER1_destination_port : regPORTADD:= ROUTINGPORT4;
constant from_ROUTER3_to_ROUTER2_destination_port : regPORTADD:= ROUTINGPORT4;
constant from_ROUTER3_to_ROUTER4_destination_port : regPORTADD:= ROUTINGPORT5;
constant from_ROUTER3_to_ROUTER5_destination_port : regPORTADD:= ROUTINGPORT5;

constant from_ROUTER4_to_ROUTER0_destination_port : regPORTADD:= ROUTINGPORT8;
constant from_ROUTER4_to_ROUTER1_destination_port : regPORTADD:= ROUTINGPORT10;
constant from_ROUTER4_to_ROUTER2_destination_port : regPORTADD:= ROUTINGPORT10;
constant from_ROUTER4_to_ROUTER3_destination_port : regPORTADD:= ROUTINGPORT8;
constant from_ROUTER4_to_ROUTER5_destination_port : regPORTADD:= ROUTINGPORT9;

constant from_ROUTER5_to_ROUTER0_destination_port : regPORTADD:= ROUTINGPORT2;
constant from_ROUTER5_to_ROUTER1_destination_port : regPORTADD:= ROUTINGPORT2;
constant from_ROUTER5_to_ROUTER2_destination_port : regPORTADD:= ROUTINGPORT2;
constant from_ROUTER5_to_ROUTER3_destination_port : regPORTADD:= ROUTINGPORT2;
constant from_ROUTER5_to_ROUTER4_destination_port : regPORTADD:= ROUTINGPORT2;

        '''
        fw= open(outputdir + "/noc_config_configurable_part2_7.vhd", 'w')
        fw.write("%s" %ch)
        fw.close()
        
    def generate_configurable_part2_8(self):
        outputdir = "./Noc0__"
        if not os.path.exists(outputdir):
            os.makedirs(outputdir)
        self.nbr_R = int(self.entry_nbr_routeur.get())
        self.nbr_M = [0 for i in range(self.nbr_R)]
        self.nbr_S = [0 for i in range(self.nbr_R)]

        for r in range(int(self.entry_nbr_routeur.get())):
            self.nbr_M[r] = int(self.damierNbrMaitre[r].get())
            self.nbr_S[r] = int(self.damierNbrEsclave[r].get())
        ch='''
------ 8) ADDRESS DECODER TYPES ------
--define the size of each address decoding table of each master of each router (in the number of rules that it contain)
type router0_master0_record_address_decod_table is array (0 to ROUTER0_MASTER0_ADD_DECOD_TABLE_SIZE-1) of record_master_interface_address_decode_routing_table;
type router0_master1_record_address_decod_table is array (0 to ROUTER0_MASTER1_ADD_DECOD_TABLE_SIZE-1) of record_master_interface_address_decode_routing_table;
type router0_master2_record_address_decod_table is array (0 to ROUTER0_MASTER2_ADD_DECOD_TABLE_SIZE-1) of record_master_interface_address_decode_routing_table;
type router0_master3_record_address_decod_table is array (0 to ROUTER0_MASTER3_ADD_DECOD_TABLE_SIZE-1) of record_master_interface_address_decode_routing_table;
                                                                                                   
type router2_master0_record_address_decod_table is array (0 to ROUTER2_MASTER0_ADD_DECOD_TABLE_SIZE-1) of record_master_interface_address_decode_routing_table;
type router2_master1_record_address_decod_table is array (0 to ROUTER2_MASTER1_ADD_DECOD_TABLE_SIZE-1) of record_master_interface_address_decode_routing_table;
type router2_master2_record_address_decod_table is array (0 to ROUTER2_MASTER2_ADD_DECOD_TABLE_SIZE-1) of record_master_interface_address_decode_routing_table;
type router2_master3_record_address_decod_table is array (0 to ROUTER2_MASTER3_ADD_DECOD_TABLE_SIZE-1) of record_master_interface_address_decode_routing_table;
                                                                                                   
type router3_master0_record_address_decod_table is array (0 to ROUTER3_MASTER0_ADD_DECOD_TABLE_SIZE-1) of record_master_interface_address_decode_routing_table;
type router3_master1_record_address_decod_table is array (0 to ROUTER3_MASTER1_ADD_DECOD_TABLE_SIZE-1) of record_master_interface_address_decode_routing_table;
type router3_master2_record_address_decod_table is array (0 to ROUTER3_MASTER2_ADD_DECOD_TABLE_SIZE-1) of record_master_interface_address_decode_routing_table;
                                                                                                   
type router4_master0_record_address_decod_table is array (0 to ROUTER4_MASTER0_ADD_DECOD_TABLE_SIZE-1) of record_master_interface_address_decode_routing_table;
type router4_master1_record_address_decod_table is array (0 to ROUTER4_MASTER1_ADD_DECOD_TABLE_SIZE-1) of record_master_interface_address_decode_routing_table;
type router4_master2_record_address_decod_table is array (0 to ROUTER4_MASTER2_ADD_DECOD_TABLE_SIZE-1) of record_master_interface_address_decode_routing_table;
type router4_master3_record_address_decod_table is array (0 to ROUTER4_MASTER3_ADD_DECOD_TABLE_SIZE-1) of record_master_interface_address_decode_routing_table;
                                                                                                    
type router5_master0_record_address_decod_table is array (0 to ROUTER5_MASTER0_ADD_DECOD_TABLE_SIZE-1) of record_master_interface_address_decode_routing_table;

type unconstrained_array_record_address_decod_table is array (natural range <>) of record_master_interface_address_decode_routing_table;


        '''
        fw= open(outputdir + "/noc_config_configurable_part2_8.vhd", 'w')
        fw.write("%s" %ch)
        fw.close()
        
		
		
    def generate_configurable_part2_9(self):
        outputdir = "./Noc0__"
        if not os.path.exists(outputdir):
            os.makedirs(outputdir)
        self.nbr_R = int(self.entry_nbr_routeur.get())
        self.nbr_M = [0 for i in range(self.nbr_R)]
        self.nbr_S = [0 for i in range(self.nbr_R)]

        for r in range(int(self.entry_nbr_routeur.get())):
            self.nbr_M[r] = int(self.damierNbrMaitre[r].get())
            self.nbr_S[r] = int(self.damierNbrEsclave[r].get())
        ch='''
------ 9) ADDRESS DECODER TABLES ------

-- constant ROUTERi_MASTERj_ADDRESS_DECODER_TABLE : router0_master0_record_address_decod_table:=(
-- |    destination slave   |   destination slave 	    |   		   Routing table 				  | slave destination |   
-- |	   base address	    | 	   high address         |	 	    local port noc address		  	  |      address      |
constant ROUTER0_MASTER0_ADDRESS_DECODER_TABLE : router0_master0_record_address_decod_table:=(
	(ROUTER0_MASTER0_address_mapping_for_ROUTER0_SLAVE4_BASE_ADD, ROUTER0_MASTER0_address_mapping_for_ROUTER0_SLAVE4_HIGH_ADD, SLAVE4, ROUTER0 & SLAVE4),	
	(ROUTER0_MASTER0_address_mapping_for_ROUTER0_SLAVE5_BASE_ADD, ROUTER0_MASTER0_address_mapping_for_ROUTER0_SLAVE5_HIGH_ADD, SLAVE5, ROUTER0 & SLAVE5),	
	(ROUTER0_MASTER0_address_mapping_for_ROUTER0_SLAVE6_BASE_ADD, ROUTER0_MASTER0_address_mapping_for_ROUTER0_SLAVE6_HIGH_ADD, SLAVE6, ROUTER0 & SLAVE6),	
	(ROUTER0_MASTER0_address_mapping_for_ROUTER0_SLAVE7_BASE_ADD, ROUTER0_MASTER0_address_mapping_for_ROUTER0_SLAVE7_HIGH_ADD, SLAVE7, ROUTER0 & SLAVE7),	
	(ROUTER0_MASTER0_address_mapping_for_ROUTER0_SLAVE8_BASE_ADD, ROUTER0_MASTER0_address_mapping_for_ROUTER0_SLAVE8_HIGH_ADD, SLAVE8, ROUTER0 & SLAVE8),	
	(ROUTER0_MASTER0_address_mapping_for_ROUTER1_SLAVE0_BASE_ADD, ROUTER0_MASTER0_address_mapping_for_ROUTER1_SLAVE0_HIGH_ADD, from_ROUTER0_to_ROUTER1_destination_port, ROUTER1 & SLAVE0),	
	(ROUTER0_MASTER0_address_mapping_for_ROUTER1_SLAVE1_BASE_ADD, ROUTER0_MASTER0_address_mapping_for_ROUTER1_SLAVE1_HIGH_ADD, from_ROUTER0_to_ROUTER1_destination_port, ROUTER1 & SLAVE1),
	(ROUTER0_MASTER0_address_mapping_for_ROUTER2_SLAVE4_BASE_ADD, ROUTER0_MASTER0_address_mapping_for_ROUTER2_SLAVE4_HIGH_ADD, from_ROUTER0_to_ROUTER2_destination_port, ROUTER2 & SLAVE4),
	(ROUTER0_MASTER0_address_mapping_for_ROUTER5_SLAVE1_BASE_ADD, ROUTER0_MASTER0_address_mapping_for_ROUTER5_SLAVE1_HIGH_ADD, from_ROUTER0_to_ROUTER5_destination_port, ROUTER5 & SLAVE1)
	);
	
constant ROUTER0_MASTER1_ADDRESS_DECODER_TABLE : router0_master1_record_address_decod_table:=(
	(ROUTER0_MASTER1_address_mapping_for_ROUTER4_SLAVE4_BASE_ADD, ROUTER0_MASTER1_address_mapping_for_ROUTER4_SLAVE4_HIGH_ADD, from_ROUTER0_to_ROUTER4_destination_port, ROUTER4 & SLAVE4),	
	(ROUTER0_MASTER1_address_mapping_for_ROUTER0_SLAVE5_BASE_ADD, ROUTER0_MASTER1_address_mapping_for_ROUTER0_SLAVE5_HIGH_ADD, SLAVE5, ROUTER0 & SLAVE5),	
	(ROUTER0_MASTER1_address_mapping_for_ROUTER0_SLAVE6_BASE_ADD, ROUTER0_MASTER1_address_mapping_for_ROUTER0_SLAVE6_HIGH_ADD, SLAVE6, ROUTER0 & SLAVE6),	
	(ROUTER0_MASTER1_address_mapping_for_ROUTER0_SLAVE7_BASE_ADD, ROUTER0_MASTER1_address_mapping_for_ROUTER0_SLAVE7_HIGH_ADD, SLAVE7, ROUTER0 & SLAVE7),	
	(ROUTER0_MASTER1_address_mapping_for_ROUTER0_SLAVE8_BASE_ADD, ROUTER0_MASTER1_address_mapping_for_ROUTER0_SLAVE8_HIGH_ADD, SLAVE8, ROUTER0 & SLAVE8),	
	(ROUTER0_MASTER1_address_mapping_for_ROUTER1_SLAVE0_BASE_ADD, ROUTER0_MASTER1_address_mapping_for_ROUTER1_SLAVE0_HIGH_ADD, from_ROUTER0_to_ROUTER1_destination_port, ROUTER1 & SLAVE0),	
	(ROUTER0_MASTER1_address_mapping_for_ROUTER1_SLAVE1_BASE_ADD, ROUTER0_MASTER1_address_mapping_for_ROUTER1_SLAVE1_HIGH_ADD, from_ROUTER0_to_ROUTER1_destination_port, ROUTER1 & SLAVE1),
	(ROUTER0_MASTER1_address_mapping_for_ROUTER2_SLAVE4_BASE_ADD, ROUTER0_MASTER1_address_mapping_for_ROUTER2_SLAVE4_HIGH_ADD, from_ROUTER0_to_ROUTER2_destination_port, ROUTER2 & SLAVE4)
	);

constant ROUTER0_MASTER2_ADDRESS_DECODER_TABLE : router0_master2_record_address_decod_table:=(
	(ROUTER0_MASTER2_address_mapping_for_ROUTER4_SLAVE4_BASE_ADD, ROUTER0_MASTER2_address_mapping_for_ROUTER4_SLAVE4_HIGH_ADD, from_ROUTER0_to_ROUTER4_destination_port, ROUTER4 & SLAVE4),	
	(ROUTER0_MASTER2_address_mapping_for_ROUTER0_SLAVE5_BASE_ADD, ROUTER0_MASTER2_address_mapping_for_ROUTER0_SLAVE5_HIGH_ADD, SLAVE5, ROUTER0 & SLAVE5),	
	(ROUTER0_MASTER2_address_mapping_for_ROUTER0_SLAVE6_BASE_ADD, ROUTER0_MASTER2_address_mapping_for_ROUTER0_SLAVE6_HIGH_ADD, SLAVE6, ROUTER0 & SLAVE6),	
	(ROUTER0_MASTER2_address_mapping_for_ROUTER0_SLAVE7_BASE_ADD, ROUTER0_MASTER2_address_mapping_for_ROUTER0_SLAVE7_HIGH_ADD, SLAVE7, ROUTER0 & SLAVE7),	
	(ROUTER0_MASTER2_address_mapping_for_ROUTER0_SLAVE8_BASE_ADD, ROUTER0_MASTER2_address_mapping_for_ROUTER0_SLAVE8_HIGH_ADD, SLAVE8, ROUTER0 & SLAVE8),	
	(ROUTER0_MASTER2_address_mapping_for_ROUTER1_SLAVE0_BASE_ADD, ROUTER0_MASTER2_address_mapping_for_ROUTER1_SLAVE0_HIGH_ADD, from_ROUTER0_to_ROUTER1_destination_port, ROUTER1 & SLAVE0),	
	(ROUTER0_MASTER2_address_mapping_for_ROUTER1_SLAVE1_BASE_ADD, ROUTER0_MASTER2_address_mapping_for_ROUTER1_SLAVE1_HIGH_ADD, from_ROUTER0_to_ROUTER1_destination_port, ROUTER1 & SLAVE1),
	(ROUTER0_MASTER2_address_mapping_for_ROUTER2_SLAVE4_BASE_ADD, ROUTER0_MASTER2_address_mapping_for_ROUTER2_SLAVE4_HIGH_ADD, from_ROUTER0_to_ROUTER2_destination_port, ROUTER2 & SLAVE4)
	);
	
constant ROUTER0_MASTER3_ADDRESS_DECODER_TABLE : router0_master3_record_address_decod_table:=(
	(ROUTER0_MASTER3_address_mapping_for_ROUTER4_SLAVE6_BASE_ADD, ROUTER0_MASTER3_address_mapping_for_ROUTER4_SLAVE6_HIGH_ADD, from_ROUTER0_to_ROUTER4_destination_port, ROUTER4 & SLAVE4),	
	(ROUTER0_MASTER3_address_mapping_for_ROUTER0_SLAVE5_BASE_ADD, ROUTER0_MASTER3_address_mapping_for_ROUTER0_SLAVE5_HIGH_ADD, SLAVE5, ROUTER0 & SLAVE5),	
	(ROUTER0_MASTER3_address_mapping_for_ROUTER0_SLAVE6_BASE_ADD, ROUTER0_MASTER3_address_mapping_for_ROUTER0_SLAVE6_HIGH_ADD, SLAVE6, ROUTER0 & SLAVE6),	
	(ROUTER0_MASTER3_address_mapping_for_ROUTER0_SLAVE7_BASE_ADD, ROUTER0_MASTER3_address_mapping_for_ROUTER0_SLAVE7_HIGH_ADD, SLAVE7, ROUTER0 & SLAVE7),	
	(ROUTER0_MASTER3_address_mapping_for_ROUTER0_SLAVE8_BASE_ADD, ROUTER0_MASTER3_address_mapping_for_ROUTER0_SLAVE8_HIGH_ADD, SLAVE8, ROUTER0 & SLAVE8),	
	(ROUTER0_MASTER3_address_mapping_for_ROUTER1_SLAVE0_BASE_ADD, ROUTER0_MASTER3_address_mapping_for_ROUTER1_SLAVE0_HIGH_ADD, from_ROUTER0_to_ROUTER1_destination_port, ROUTER1 & SLAVE0),	
	(ROUTER0_MASTER3_address_mapping_for_ROUTER1_SLAVE1_BASE_ADD, ROUTER0_MASTER3_address_mapping_for_ROUTER1_SLAVE1_HIGH_ADD, from_ROUTER0_to_ROUTER1_destination_port, ROUTER1 & SLAVE1),
	(ROUTER0_MASTER3_address_mapping_for_ROUTER2_SLAVE4_BASE_ADD, ROUTER0_MASTER3_address_mapping_for_ROUTER2_SLAVE4_HIGH_ADD, from_ROUTER0_to_ROUTER2_destination_port, ROUTER2 & SLAVE4)
	);

constant ROUTER2_MASTER0_ADDRESS_DECODER_TABLE : router2_master0_record_address_decod_table:=(
	(ROUTER2_MASTER0_address_mapping_for_ROUTER4_SLAVE4_BASE_ADD, ROUTER2_MASTER0_address_mapping_for_ROUTER4_SLAVE4_HIGH_ADD, from_ROUTER2_to_ROUTER4_destination_port, ROUTER4 & SLAVE4),	
	(ROUTER2_MASTER0_address_mapping_for_ROUTER4_SLAVE5_BASE_ADD, ROUTER2_MASTER0_address_mapping_for_ROUTER4_SLAVE5_HIGH_ADD, from_ROUTER2_to_ROUTER4_destination_port, ROUTER4 & SLAVE5),	
	(ROUTER2_MASTER0_address_mapping_for_ROUTER4_SLAVE6_BASE_ADD, ROUTER2_MASTER0_address_mapping_for_ROUTER4_SLAVE6_HIGH_ADD, from_ROUTER2_to_ROUTER4_destination_port, ROUTER4 & SLAVE6),	
	(ROUTER2_MASTER0_address_mapping_for_ROUTER4_SLAVE7_BASE_ADD, ROUTER2_MASTER0_address_mapping_for_ROUTER4_SLAVE7_HIGH_ADD, from_ROUTER2_to_ROUTER4_destination_port, ROUTER4 & SLAVE7),	
	(ROUTER2_MASTER0_address_mapping_for_ROUTER0_SLAVE8_BASE_ADD, ROUTER2_MASTER0_address_mapping_for_ROUTER0_SLAVE8_HIGH_ADD, from_ROUTER2_to_ROUTER0_destination_port, ROUTER0 & SLAVE8),	
	(ROUTER2_MASTER0_address_mapping_for_ROUTER1_SLAVE0_BASE_ADD, ROUTER2_MASTER0_address_mapping_for_ROUTER1_SLAVE0_HIGH_ADD, from_ROUTER2_to_ROUTER1_destination_port, ROUTER1 & SLAVE0),	
	(ROUTER2_MASTER0_address_mapping_for_ROUTER1_SLAVE1_BASE_ADD, ROUTER2_MASTER0_address_mapping_for_ROUTER1_SLAVE1_HIGH_ADD, from_ROUTER2_to_ROUTER1_destination_port, ROUTER1 & SLAVE1),
	(ROUTER2_MASTER0_address_mapping_for_ROUTER2_SLAVE4_BASE_ADD, ROUTER2_MASTER0_address_mapping_for_ROUTER2_SLAVE4_HIGH_ADD, SLAVE4, ROUTER2 & SLAVE4)
	);
	
constant ROUTER2_MASTER1_ADDRESS_DECODER_TABLE : router2_master1_record_address_decod_table:=(
	(ROUTER2_MASTER1_address_mapping_for_ROUTER0_SLAVE4_BASE_ADD, ROUTER2_MASTER1_address_mapping_for_ROUTER0_SLAVE4_HIGH_ADD, from_ROUTER2_to_ROUTER0_destination_port, ROUTER0 & SLAVE4),	
	(ROUTER2_MASTER1_address_mapping_for_ROUTER0_SLAVE5_BASE_ADD, ROUTER2_MASTER1_address_mapping_for_ROUTER0_SLAVE5_HIGH_ADD, from_ROUTER2_to_ROUTER0_destination_port, ROUTER0 & SLAVE5),	
	(ROUTER2_MASTER1_address_mapping_for_ROUTER0_SLAVE6_BASE_ADD, ROUTER2_MASTER1_address_mapping_for_ROUTER0_SLAVE6_HIGH_ADD, from_ROUTER2_to_ROUTER0_destination_port, ROUTER0 & SLAVE6),	
	(ROUTER2_MASTER1_address_mapping_for_ROUTER0_SLAVE7_BASE_ADD, ROUTER2_MASTER1_address_mapping_for_ROUTER0_SLAVE7_HIGH_ADD, from_ROUTER2_to_ROUTER0_destination_port, ROUTER0 & SLAVE7),	
	(ROUTER2_MASTER1_address_mapping_for_ROUTER0_SLAVE8_BASE_ADD, ROUTER2_MASTER1_address_mapping_for_ROUTER0_SLAVE8_HIGH_ADD, from_ROUTER2_to_ROUTER0_destination_port, ROUTER0 & SLAVE8),	
	(ROUTER2_MASTER1_address_mapping_for_ROUTER1_SLAVE0_BASE_ADD, ROUTER2_MASTER1_address_mapping_for_ROUTER1_SLAVE0_HIGH_ADD, from_ROUTER2_to_ROUTER1_destination_port, ROUTER1 & SLAVE0),	
	(ROUTER2_MASTER1_address_mapping_for_ROUTER1_SLAVE1_BASE_ADD, ROUTER2_MASTER1_address_mapping_for_ROUTER1_SLAVE1_HIGH_ADD, from_ROUTER2_to_ROUTER1_destination_port, ROUTER1 & SLAVE1),
	(ROUTER2_MASTER1_address_mapping_for_ROUTER2_SLAVE4_BASE_ADD, ROUTER2_MASTER1_address_mapping_for_ROUTER2_SLAVE4_HIGH_ADD, SLAVE4, ROUTER2 & SLAVE4)
	);

constant ROUTER2_MASTER2_ADDRESS_DECODER_TABLE : router2_master2_record_address_decod_table:=(
	(ROUTER2_MASTER2_address_mapping_for_ROUTER0_SLAVE4_BASE_ADD, ROUTER2_MASTER2_address_mapping_for_ROUTER0_SLAVE4_HIGH_ADD, from_ROUTER2_to_ROUTER0_destination_port, ROUTER0 & SLAVE4),	
	(ROUTER2_MASTER2_address_mapping_for_ROUTER0_SLAVE5_BASE_ADD, ROUTER2_MASTER2_address_mapping_for_ROUTER0_SLAVE5_HIGH_ADD, from_ROUTER2_to_ROUTER0_destination_port, ROUTER0 & SLAVE5),	
	(ROUTER2_MASTER2_address_mapping_for_ROUTER0_SLAVE6_BASE_ADD, ROUTER2_MASTER2_address_mapping_for_ROUTER0_SLAVE6_HIGH_ADD, from_ROUTER2_to_ROUTER0_destination_port, ROUTER0 & SLAVE6),	
	(ROUTER2_MASTER2_address_mapping_for_ROUTER0_SLAVE7_BASE_ADD, ROUTER2_MASTER2_address_mapping_for_ROUTER0_SLAVE7_HIGH_ADD, from_ROUTER2_to_ROUTER0_destination_port, ROUTER0 & SLAVE7),	
	(ROUTER2_MASTER2_address_mapping_for_ROUTER0_SLAVE8_BASE_ADD, ROUTER2_MASTER2_address_mapping_for_ROUTER0_SLAVE8_HIGH_ADD, from_ROUTER2_to_ROUTER0_destination_port, ROUTER0 & SLAVE8),	
	(ROUTER2_MASTER2_address_mapping_for_ROUTER1_SLAVE0_BASE_ADD, ROUTER2_MASTER2_address_mapping_for_ROUTER1_SLAVE0_HIGH_ADD, from_ROUTER2_to_ROUTER1_destination_port, ROUTER1 & SLAVE0),	
	(ROUTER2_MASTER2_address_mapping_for_ROUTER1_SLAVE1_BASE_ADD, ROUTER2_MASTER2_address_mapping_for_ROUTER1_SLAVE1_HIGH_ADD, from_ROUTER2_to_ROUTER1_destination_port, ROUTER1 & SLAVE1),
	(ROUTER2_MASTER2_address_mapping_for_ROUTER2_SLAVE4_BASE_ADD, ROUTER2_MASTER2_address_mapping_for_ROUTER2_SLAVE4_HIGH_ADD, SLAVE4, ROUTER2 & SLAVE4)
	);
	
constant ROUTER2_MASTER3_ADDRESS_DECODER_TABLE : router2_master3_record_address_decod_table:=(
	(ROUTER2_MASTER3_address_mapping_for_ROUTER0_SLAVE4_BASE_ADD, ROUTER2_MASTER3_address_mapping_for_ROUTER0_SLAVE4_HIGH_ADD, from_ROUTER2_to_ROUTER0_destination_port, ROUTER0 & SLAVE4),	
	(ROUTER2_MASTER3_address_mapping_for_ROUTER0_SLAVE5_BASE_ADD, ROUTER2_MASTER3_address_mapping_for_ROUTER0_SLAVE5_HIGH_ADD, from_ROUTER2_to_ROUTER0_destination_port, ROUTER0 & SLAVE5),	
	(ROUTER2_MASTER3_address_mapping_for_ROUTER0_SLAVE6_BASE_ADD, ROUTER2_MASTER3_address_mapping_for_ROUTER0_SLAVE6_HIGH_ADD, from_ROUTER2_to_ROUTER0_destination_port, ROUTER0 & SLAVE6),	
	(ROUTER2_MASTER3_address_mapping_for_ROUTER0_SLAVE7_BASE_ADD, ROUTER2_MASTER3_address_mapping_for_ROUTER0_SLAVE7_HIGH_ADD, from_ROUTER2_to_ROUTER0_destination_port, ROUTER0 & SLAVE7),	
	(ROUTER2_MASTER3_address_mapping_for_ROUTER0_SLAVE8_BASE_ADD, ROUTER2_MASTER3_address_mapping_for_ROUTER0_SLAVE8_HIGH_ADD, from_ROUTER2_to_ROUTER0_destination_port, ROUTER0 & SLAVE8),	
	(ROUTER2_MASTER3_address_mapping_for_ROUTER1_SLAVE0_BASE_ADD, ROUTER2_MASTER3_address_mapping_for_ROUTER1_SLAVE0_HIGH_ADD, from_ROUTER2_to_ROUTER1_destination_port, ROUTER1 & SLAVE0),	
	(ROUTER2_MASTER3_address_mapping_for_ROUTER1_SLAVE1_BASE_ADD, ROUTER2_MASTER3_address_mapping_for_ROUTER1_SLAVE1_HIGH_ADD, from_ROUTER2_to_ROUTER1_destination_port, ROUTER1 & SLAVE1),
	(ROUTER2_MASTER3_address_mapping_for_ROUTER2_SLAVE4_BASE_ADD, ROUTER2_MASTER3_address_mapping_for_ROUTER2_SLAVE4_HIGH_ADD, SLAVE4, ROUTER2 & SLAVE4)
	);
	
constant ROUTER3_MASTER0_ADDRESS_DECODER_TABLE : router3_master0_record_address_decod_table:=(
	(ROUTER3_MASTER0_address_mapping_for_ROUTER0_SLAVE4_BASE_ADD, ROUTER3_MASTER0_address_mapping_for_ROUTER0_SLAVE4_HIGH_ADD, from_ROUTER3_to_ROUTER0_destination_port, ROUTER0 & SLAVE4),	
	(ROUTER3_MASTER0_address_mapping_for_ROUTER0_SLAVE5_BASE_ADD, ROUTER3_MASTER0_address_mapping_for_ROUTER0_SLAVE5_HIGH_ADD, from_ROUTER3_to_ROUTER0_destination_port, ROUTER0 & SLAVE5),	
	(ROUTER3_MASTER0_address_mapping_for_ROUTER0_SLAVE6_BASE_ADD, ROUTER3_MASTER0_address_mapping_for_ROUTER0_SLAVE6_HIGH_ADD, from_ROUTER3_to_ROUTER0_destination_port, ROUTER0 & SLAVE6),	
	(ROUTER3_MASTER0_address_mapping_for_ROUTER0_SLAVE7_BASE_ADD, ROUTER3_MASTER0_address_mapping_for_ROUTER0_SLAVE7_HIGH_ADD, from_ROUTER3_to_ROUTER0_destination_port, ROUTER0 & SLAVE7),	
	(ROUTER3_MASTER0_address_mapping_for_ROUTER0_SLAVE8_BASE_ADD, ROUTER3_MASTER0_address_mapping_for_ROUTER0_SLAVE8_HIGH_ADD, from_ROUTER3_to_ROUTER0_destination_port, ROUTER0 & SLAVE8),	
	(ROUTER3_MASTER0_address_mapping_for_ROUTER1_SLAVE0_BASE_ADD, ROUTER3_MASTER0_address_mapping_for_ROUTER1_SLAVE0_HIGH_ADD, from_ROUTER3_to_ROUTER1_destination_port, ROUTER1 & SLAVE0),	
	(ROUTER3_MASTER0_address_mapping_for_ROUTER1_SLAVE1_BASE_ADD, ROUTER3_MASTER0_address_mapping_for_ROUTER1_SLAVE1_HIGH_ADD, from_ROUTER3_to_ROUTER1_destination_port, ROUTER1 & SLAVE1),
	(ROUTER3_MASTER0_address_mapping_for_ROUTER2_SLAVE4_BASE_ADD, ROUTER3_MASTER0_address_mapping_for_ROUTER2_SLAVE4_HIGH_ADD, from_ROUTER3_to_ROUTER2_destination_port, ROUTER2 & SLAVE4)
	);
	
constant ROUTER3_MASTER1_ADDRESS_DECODER_TABLE : router3_master1_record_address_decod_table:=(
	(ROUTER3_MASTER1_address_mapping_for_ROUTER0_SLAVE4_BASE_ADD, ROUTER3_MASTER1_address_mapping_for_ROUTER0_SLAVE4_HIGH_ADD, from_ROUTER3_to_ROUTER0_destination_port, ROUTER0 & SLAVE4),	
	(ROUTER3_MASTER1_address_mapping_for_ROUTER0_SLAVE5_BASE_ADD, ROUTER3_MASTER1_address_mapping_for_ROUTER0_SLAVE5_HIGH_ADD, from_ROUTER3_to_ROUTER0_destination_port, ROUTER0 & SLAVE5),	
	(ROUTER3_MASTER1_address_mapping_for_ROUTER0_SLAVE6_BASE_ADD, ROUTER3_MASTER1_address_mapping_for_ROUTER0_SLAVE6_HIGH_ADD, from_ROUTER3_to_ROUTER0_destination_port, ROUTER0 & SLAVE6),	
	(ROUTER3_MASTER1_address_mapping_for_ROUTER0_SLAVE7_BASE_ADD, ROUTER3_MASTER1_address_mapping_for_ROUTER0_SLAVE7_HIGH_ADD, from_ROUTER3_to_ROUTER0_destination_port, ROUTER0 & SLAVE7),	
	(ROUTER3_MASTER1_address_mapping_for_ROUTER0_SLAVE8_BASE_ADD, ROUTER3_MASTER1_address_mapping_for_ROUTER0_SLAVE8_HIGH_ADD, from_ROUTER3_to_ROUTER0_destination_port, ROUTER0 & SLAVE8),	
	(ROUTER3_MASTER1_address_mapping_for_ROUTER1_SLAVE0_BASE_ADD, ROUTER3_MASTER1_address_mapping_for_ROUTER1_SLAVE0_HIGH_ADD, from_ROUTER3_to_ROUTER1_destination_port, ROUTER1 & SLAVE0),	
	(ROUTER3_MASTER1_address_mapping_for_ROUTER1_SLAVE1_BASE_ADD, ROUTER3_MASTER1_address_mapping_for_ROUTER1_SLAVE1_HIGH_ADD, from_ROUTER3_to_ROUTER1_destination_port, ROUTER1 & SLAVE1),
	(ROUTER3_MASTER1_address_mapping_for_ROUTER2_SLAVE4_BASE_ADD, ROUTER3_MASTER1_address_mapping_for_ROUTER2_SLAVE4_HIGH_ADD, from_ROUTER3_to_ROUTER2_destination_port, ROUTER2 & SLAVE4)
	);

constant ROUTER3_MASTER2_ADDRESS_DECODER_TABLE : router3_master2_record_address_decod_table:=(
	(ROUTER3_MASTER2_address_mapping_for_ROUTER0_SLAVE4_BASE_ADD, ROUTER3_MASTER2_address_mapping_for_ROUTER0_SLAVE4_HIGH_ADD, from_ROUTER3_to_ROUTER0_destination_port, ROUTER0 & SLAVE4),	
	(ROUTER3_MASTER2_address_mapping_for_ROUTER0_SLAVE5_BASE_ADD, ROUTER3_MASTER2_address_mapping_for_ROUTER0_SLAVE5_HIGH_ADD, from_ROUTER3_to_ROUTER0_destination_port, ROUTER0 & SLAVE5),	
	(ROUTER3_MASTER2_address_mapping_for_ROUTER0_SLAVE6_BASE_ADD, ROUTER3_MASTER2_address_mapping_for_ROUTER0_SLAVE6_HIGH_ADD, from_ROUTER3_to_ROUTER0_destination_port, ROUTER0 & SLAVE6),	
	(ROUTER3_MASTER2_address_mapping_for_ROUTER0_SLAVE7_BASE_ADD, ROUTER3_MASTER2_address_mapping_for_ROUTER0_SLAVE7_HIGH_ADD, from_ROUTER3_to_ROUTER0_destination_port, ROUTER0 & SLAVE7),	
	(ROUTER3_MASTER2_address_mapping_for_ROUTER0_SLAVE8_BASE_ADD, ROUTER3_MASTER2_address_mapping_for_ROUTER0_SLAVE8_HIGH_ADD, from_ROUTER3_to_ROUTER0_destination_port, ROUTER0 & SLAVE8),	
	(ROUTER3_MASTER2_address_mapping_for_ROUTER1_SLAVE0_BASE_ADD, ROUTER3_MASTER2_address_mapping_for_ROUTER1_SLAVE0_HIGH_ADD, from_ROUTER3_to_ROUTER1_destination_port, ROUTER1 & SLAVE0),	
	(ROUTER3_MASTER2_address_mapping_for_ROUTER1_SLAVE1_BASE_ADD, ROUTER3_MASTER2_address_mapping_for_ROUTER1_SLAVE1_HIGH_ADD, from_ROUTER3_to_ROUTER1_destination_port, ROUTER1 & SLAVE1),
	(ROUTER3_MASTER2_address_mapping_for_ROUTER2_SLAVE4_BASE_ADD, ROUTER3_MASTER2_address_mapping_for_ROUTER2_SLAVE4_HIGH_ADD, from_ROUTER3_to_ROUTER2_destination_port, ROUTER2 & SLAVE4)
	);
	
	
constant ROUTER4_MASTER0_ADDRESS_DECODER_TABLE : router4_master0_record_address_decod_table:=(
	(ROUTER4_MASTER0_address_mapping_for_ROUTER0_SLAVE4_BASE_ADD, ROUTER4_MASTER0_address_mapping_for_ROUTER0_SLAVE4_HIGH_ADD, from_ROUTER4_to_ROUTER0_destination_port, ROUTER0 & SLAVE4),	
	(ROUTER4_MASTER0_address_mapping_for_ROUTER0_SLAVE5_BASE_ADD, ROUTER4_MASTER0_address_mapping_for_ROUTER0_SLAVE5_HIGH_ADD, from_ROUTER4_to_ROUTER0_destination_port, ROUTER0 & SLAVE5),	
	(ROUTER4_MASTER0_address_mapping_for_ROUTER0_SLAVE6_BASE_ADD, ROUTER4_MASTER0_address_mapping_for_ROUTER0_SLAVE6_HIGH_ADD, from_ROUTER4_to_ROUTER0_destination_port, ROUTER0 & SLAVE6),	
	(ROUTER4_MASTER0_address_mapping_for_ROUTER0_SLAVE7_BASE_ADD, ROUTER4_MASTER0_address_mapping_for_ROUTER0_SLAVE7_HIGH_ADD, from_ROUTER4_to_ROUTER0_destination_port, ROUTER0 & SLAVE7),	
	(ROUTER4_MASTER0_address_mapping_for_ROUTER0_SLAVE8_BASE_ADD, ROUTER4_MASTER0_address_mapping_for_ROUTER0_SLAVE8_HIGH_ADD, from_ROUTER4_to_ROUTER0_destination_port, ROUTER0 & SLAVE8),	
	(ROUTER4_MASTER0_address_mapping_for_ROUTER1_SLAVE0_BASE_ADD, ROUTER4_MASTER0_address_mapping_for_ROUTER1_SLAVE0_HIGH_ADD, from_ROUTER4_to_ROUTER1_destination_port, ROUTER1 & SLAVE0),	
	(ROUTER4_MASTER0_address_mapping_for_ROUTER1_SLAVE1_BASE_ADD, ROUTER4_MASTER0_address_mapping_for_ROUTER1_SLAVE1_HIGH_ADD, from_ROUTER4_to_ROUTER1_destination_port, ROUTER1 & SLAVE1),
	(ROUTER4_MASTER0_address_mapping_for_ROUTER2_SLAVE4_BASE_ADD, ROUTER4_MASTER0_address_mapping_for_ROUTER2_SLAVE4_HIGH_ADD, from_ROUTER4_to_ROUTER2_destination_port, ROUTER2 & SLAVE4)
	);
	
constant ROUTER4_MASTER1_ADDRESS_DECODER_TABLE : router4_master1_record_address_decod_table:=(
	(ROUTER4_MASTER1_address_mapping_for_ROUTER0_SLAVE4_BASE_ADD, ROUTER4_MASTER1_address_mapping_for_ROUTER0_SLAVE4_HIGH_ADD, from_ROUTER4_to_ROUTER0_destination_port, ROUTER0 & SLAVE4),	
	(ROUTER4_MASTER1_address_mapping_for_ROUTER0_SLAVE5_BASE_ADD, ROUTER4_MASTER1_address_mapping_for_ROUTER0_SLAVE5_HIGH_ADD, from_ROUTER4_to_ROUTER0_destination_port, ROUTER0 & SLAVE5),	
	(ROUTER4_MASTER1_address_mapping_for_ROUTER0_SLAVE6_BASE_ADD, ROUTER4_MASTER1_address_mapping_for_ROUTER0_SLAVE6_HIGH_ADD, from_ROUTER4_to_ROUTER0_destination_port, ROUTER0 & SLAVE6),	
	(ROUTER4_MASTER1_address_mapping_for_ROUTER0_SLAVE7_BASE_ADD, ROUTER4_MASTER1_address_mapping_for_ROUTER0_SLAVE7_HIGH_ADD, from_ROUTER4_to_ROUTER0_destination_port, ROUTER0 & SLAVE7),	
	(ROUTER4_MASTER1_address_mapping_for_ROUTER0_SLAVE8_BASE_ADD, ROUTER4_MASTER1_address_mapping_for_ROUTER0_SLAVE8_HIGH_ADD, from_ROUTER4_to_ROUTER0_destination_port, ROUTER0 & SLAVE8),	
	(ROUTER4_MASTER1_address_mapping_for_ROUTER1_SLAVE0_BASE_ADD, ROUTER4_MASTER1_address_mapping_for_ROUTER1_SLAVE0_HIGH_ADD, from_ROUTER4_to_ROUTER1_destination_port, ROUTER1 & SLAVE0),	
	(ROUTER4_MASTER1_address_mapping_for_ROUTER1_SLAVE1_BASE_ADD, ROUTER4_MASTER1_address_mapping_for_ROUTER1_SLAVE1_HIGH_ADD, from_ROUTER4_to_ROUTER1_destination_port, ROUTER1 & SLAVE1),
	(ROUTER4_MASTER1_address_mapping_for_ROUTER2_SLAVE4_BASE_ADD, ROUTER4_MASTER1_address_mapping_for_ROUTER2_SLAVE4_HIGH_ADD, from_ROUTER4_to_ROUTER2_destination_port, ROUTER2 & SLAVE4)
	);

constant ROUTER4_MASTER2_ADDRESS_DECODER_TABLE : router4_master2_record_address_decod_table:=(
	(ROUTER4_MASTER2_address_mapping_for_ROUTER0_SLAVE4_BASE_ADD, ROUTER4_MASTER2_address_mapping_for_ROUTER0_SLAVE4_HIGH_ADD, from_ROUTER4_to_ROUTER0_destination_port, ROUTER0 & SLAVE4),	
	(ROUTER4_MASTER2_address_mapping_for_ROUTER0_SLAVE5_BASE_ADD, ROUTER4_MASTER2_address_mapping_for_ROUTER0_SLAVE5_HIGH_ADD, from_ROUTER4_to_ROUTER0_destination_port, ROUTER0 & SLAVE5),	
	(ROUTER4_MASTER2_address_mapping_for_ROUTER0_SLAVE6_BASE_ADD, ROUTER4_MASTER2_address_mapping_for_ROUTER0_SLAVE6_HIGH_ADD, from_ROUTER4_to_ROUTER0_destination_port, ROUTER0 & SLAVE6),	
	(ROUTER4_MASTER2_address_mapping_for_ROUTER0_SLAVE7_BASE_ADD, ROUTER4_MASTER2_address_mapping_for_ROUTER0_SLAVE7_HIGH_ADD, from_ROUTER4_to_ROUTER0_destination_port, ROUTER0 & SLAVE7),	
	(ROUTER4_MASTER2_address_mapping_for_ROUTER0_SLAVE8_BASE_ADD, ROUTER4_MASTER2_address_mapping_for_ROUTER0_SLAVE8_HIGH_ADD, from_ROUTER4_to_ROUTER0_destination_port, ROUTER0 & SLAVE8),	
	(ROUTER4_MASTER2_address_mapping_for_ROUTER1_SLAVE0_BASE_ADD, ROUTER4_MASTER2_address_mapping_for_ROUTER1_SLAVE0_HIGH_ADD, from_ROUTER4_to_ROUTER1_destination_port, ROUTER1 & SLAVE0),	
	(ROUTER4_MASTER2_address_mapping_for_ROUTER1_SLAVE1_BASE_ADD, ROUTER4_MASTER2_address_mapping_for_ROUTER1_SLAVE1_HIGH_ADD, from_ROUTER4_to_ROUTER1_destination_port, ROUTER1 & SLAVE1),
	(ROUTER4_MASTER2_address_mapping_for_ROUTER2_SLAVE4_BASE_ADD, ROUTER4_MASTER2_address_mapping_for_ROUTER2_SLAVE4_HIGH_ADD, from_ROUTER4_to_ROUTER2_destination_port, ROUTER2 & SLAVE4)
	);
	
constant ROUTER4_MASTER3_ADDRESS_DECODER_TABLE : router4_master3_record_address_decod_table:=(
	(ROUTER4_MASTER3_address_mapping_for_ROUTER0_SLAVE4_BASE_ADD, ROUTER4_MASTER3_address_mapping_for_ROUTER0_SLAVE4_HIGH_ADD, from_ROUTER4_to_ROUTER0_destination_port, ROUTER0 & SLAVE4),	
	(ROUTER4_MASTER3_address_mapping_for_ROUTER0_SLAVE5_BASE_ADD, ROUTER4_MASTER3_address_mapping_for_ROUTER0_SLAVE5_HIGH_ADD, from_ROUTER4_to_ROUTER0_destination_port, ROUTER0 & SLAVE5),	
	(ROUTER4_MASTER3_address_mapping_for_ROUTER0_SLAVE6_BASE_ADD, ROUTER4_MASTER3_address_mapping_for_ROUTER0_SLAVE6_HIGH_ADD, from_ROUTER4_to_ROUTER0_destination_port, ROUTER0 & SLAVE6),	
	(ROUTER4_MASTER3_address_mapping_for_ROUTER0_SLAVE7_BASE_ADD, ROUTER4_MASTER3_address_mapping_for_ROUTER0_SLAVE7_HIGH_ADD, from_ROUTER4_to_ROUTER0_destination_port, ROUTER0 & SLAVE7),	
	(ROUTER4_MASTER3_address_mapping_for_ROUTER0_SLAVE8_BASE_ADD, ROUTER4_MASTER3_address_mapping_for_ROUTER0_SLAVE8_HIGH_ADD, from_ROUTER4_to_ROUTER0_destination_port, ROUTER0 & SLAVE8),	
	(ROUTER4_MASTER3_address_mapping_for_ROUTER1_SLAVE0_BASE_ADD, ROUTER4_MASTER3_address_mapping_for_ROUTER1_SLAVE0_HIGH_ADD, from_ROUTER4_to_ROUTER1_destination_port, ROUTER1 & SLAVE0),	
	(ROUTER4_MASTER3_address_mapping_for_ROUTER1_SLAVE1_BASE_ADD, ROUTER4_MASTER3_address_mapping_for_ROUTER1_SLAVE1_HIGH_ADD, from_ROUTER4_to_ROUTER1_destination_port, ROUTER1 & SLAVE1),
	(ROUTER4_MASTER3_address_mapping_for_ROUTER2_SLAVE4_BASE_ADD, ROUTER4_MASTER3_address_mapping_for_ROUTER2_SLAVE4_HIGH_ADD, from_ROUTER4_to_ROUTER2_destination_port, ROUTER2 & SLAVE4)
	);
	
constant ROUTER5_MASTER0_ADDRESS_DECODER_TABLE : router5_master0_record_address_decod_table:=(
	(ROUTER5_MASTER0_address_mapping_for_ROUTER1_SLAVE0_BASE_ADD, ROUTER5_MASTER0_address_mapping_for_ROUTER1_SLAVE0_HIGH_ADD, from_ROUTER5_to_ROUTER1_destination_port, ROUTER1 & SLAVE0),	
	(ROUTER5_MASTER0_address_mapping_for_ROUTER1_SLAVE1_BASE_ADD, ROUTER5_MASTER0_address_mapping_for_ROUTER1_SLAVE1_HIGH_ADD, from_ROUTER5_to_ROUTER1_destination_port, ROUTER1 & SLAVE1),	
	(ROUTER5_MASTER0_address_mapping_for_ROUTER2_SLAVE4_BASE_ADD, ROUTER5_MASTER0_address_mapping_for_ROUTER2_SLAVE4_HIGH_ADD, from_ROUTER5_to_ROUTER2_destination_port, ROUTER2 & SLAVE4),	
	(ROUTER5_MASTER0_address_mapping_for_ROUTER4_SLAVE4_BASE_ADD, ROUTER5_MASTER0_address_mapping_for_ROUTER4_SLAVE4_HIGH_ADD, from_ROUTER5_to_ROUTER4_destination_port, ROUTER4 & SLAVE4),	
	(ROUTER5_MASTER0_address_mapping_for_ROUTER4_SLAVE5_BASE_ADD, ROUTER5_MASTER0_address_mapping_for_ROUTER4_SLAVE5_HIGH_ADD, from_ROUTER5_to_ROUTER4_destination_port, ROUTER4 & SLAVE5),	
	(ROUTER5_MASTER0_address_mapping_for_ROUTER4_SLAVE6_BASE_ADD, ROUTER5_MASTER0_address_mapping_for_ROUTER4_SLAVE6_HIGH_ADD, from_ROUTER5_to_ROUTER4_destination_port, ROUTER4 & SLAVE6),
	(ROUTER5_MASTER0_address_mapping_for_ROUTER4_SLAVE7_BASE_ADD, ROUTER5_MASTER0_address_mapping_for_ROUTER4_SLAVE7_HIGH_ADD, from_ROUTER5_to_ROUTER4_destination_port, ROUTER4 & SLAVE7),
	(ROUTER5_MASTER0_address_mapping_for_ROUTER5_SLAVE1_BASE_ADD, ROUTER5_MASTER0_address_mapping_for_ROUTER5_SLAVE1_HIGH_ADD, SLAVE4, ROUTER5 & SLAVE4),
	(ROUTER5_MASTER0_address_mapping_for_ROUTER0_SLAVE4_BASE_ADD, ROUTER5_MASTER0_address_mapping_for_ROUTER0_SLAVE4_HIGH_ADD, from_ROUTER5_to_ROUTER0_destination_port, ROUTER0 & SLAVE4)
	);
	
	
-- => AGGREGATING ARRAY <= --
--aggregates all master address decoder rules : starting from ROUTER0 - MASTER0 - RULES0 => first increment RULE number, then increment MASTER number, and finally increment ROUTER number
--concantenate all the rules with a "&"
constant ALL_MASTER_ADDRESS_DECODER_TABLES : unconstrained_array_record_address_decod_table:=(
	ROUTER0_MASTER0_ADDRESS_DECODER_TABLE(0) &
	ROUTER0_MASTER0_ADDRESS_DECODER_TABLE(1) &
	ROUTER0_MASTER0_ADDRESS_DECODER_TABLE(2) &
	ROUTER0_MASTER0_ADDRESS_DECODER_TABLE(3) &
	ROUTER0_MASTER0_ADDRESS_DECODER_TABLE(4) &
	ROUTER0_MASTER0_ADDRESS_DECODER_TABLE(5) &
	ROUTER0_MASTER0_ADDRESS_DECODER_TABLE(6) &
	ROUTER0_MASTER0_ADDRESS_DECODER_TABLE(7) &
	ROUTER0_MASTER0_ADDRESS_DECODER_TABLE(8) &
	ROUTER0_MASTER1_ADDRESS_DECODER_TABLE(0) &
	ROUTER0_MASTER1_ADDRESS_DECODER_TABLE(1) &
	ROUTER0_MASTER1_ADDRESS_DECODER_TABLE(2) &
	ROUTER0_MASTER1_ADDRESS_DECODER_TABLE(3) &
	ROUTER0_MASTER1_ADDRESS_DECODER_TABLE(4) &
	ROUTER0_MASTER1_ADDRESS_DECODER_TABLE(5) &
	ROUTER0_MASTER1_ADDRESS_DECODER_TABLE(6) &
	ROUTER0_MASTER1_ADDRESS_DECODER_TABLE(7) &
	ROUTER0_MASTER2_ADDRESS_DECODER_TABLE(0) &
	ROUTER0_MASTER2_ADDRESS_DECODER_TABLE(1) &
	ROUTER0_MASTER2_ADDRESS_DECODER_TABLE(2) &
	ROUTER0_MASTER2_ADDRESS_DECODER_TABLE(3) &
	ROUTER0_MASTER2_ADDRESS_DECODER_TABLE(4) &
	ROUTER0_MASTER2_ADDRESS_DECODER_TABLE(5) &
	ROUTER0_MASTER2_ADDRESS_DECODER_TABLE(6) &
	ROUTER0_MASTER2_ADDRESS_DECODER_TABLE(7) &
	ROUTER0_MASTER3_ADDRESS_DECODER_TABLE(0) &
	ROUTER0_MASTER3_ADDRESS_DECODER_TABLE(1) &
	ROUTER0_MASTER3_ADDRESS_DECODER_TABLE(2) &
	ROUTER0_MASTER3_ADDRESS_DECODER_TABLE(3) &
	ROUTER0_MASTER3_ADDRESS_DECODER_TABLE(4) &
	ROUTER0_MASTER3_ADDRESS_DECODER_TABLE(5) &
	ROUTER0_MASTER3_ADDRESS_DECODER_TABLE(6) &
	ROUTER0_MASTER3_ADDRESS_DECODER_TABLE(7) &
	ROUTER2_MASTER0_ADDRESS_DECODER_TABLE(0) &
	ROUTER2_MASTER0_ADDRESS_DECODER_TABLE(1) &
	ROUTER2_MASTER0_ADDRESS_DECODER_TABLE(2) &
	ROUTER2_MASTER0_ADDRESS_DECODER_TABLE(3) &
	ROUTER2_MASTER0_ADDRESS_DECODER_TABLE(4) &
	ROUTER2_MASTER0_ADDRESS_DECODER_TABLE(5) &
	ROUTER2_MASTER0_ADDRESS_DECODER_TABLE(6) &
	ROUTER2_MASTER0_ADDRESS_DECODER_TABLE(7) &
	ROUTER2_MASTER1_ADDRESS_DECODER_TABLE(0) &
	ROUTER2_MASTER1_ADDRESS_DECODER_TABLE(1) &
	ROUTER2_MASTER1_ADDRESS_DECODER_TABLE(2) &
	ROUTER2_MASTER1_ADDRESS_DECODER_TABLE(3) &
	ROUTER2_MASTER1_ADDRESS_DECODER_TABLE(4) &
	ROUTER2_MASTER1_ADDRESS_DECODER_TABLE(5) &
	ROUTER2_MASTER1_ADDRESS_DECODER_TABLE(6) &
	ROUTER2_MASTER1_ADDRESS_DECODER_TABLE(7) &
	ROUTER2_MASTER2_ADDRESS_DECODER_TABLE(0) &
	ROUTER2_MASTER2_ADDRESS_DECODER_TABLE(1) &
	ROUTER2_MASTER2_ADDRESS_DECODER_TABLE(2) &
	ROUTER2_MASTER2_ADDRESS_DECODER_TABLE(3) &
	ROUTER2_MASTER2_ADDRESS_DECODER_TABLE(4) &
	ROUTER2_MASTER2_ADDRESS_DECODER_TABLE(5) &
	ROUTER2_MASTER2_ADDRESS_DECODER_TABLE(6) &
	ROUTER2_MASTER2_ADDRESS_DECODER_TABLE(7) &
	ROUTER2_MASTER3_ADDRESS_DECODER_TABLE(0) &
	ROUTER2_MASTER3_ADDRESS_DECODER_TABLE(1) &
	ROUTER2_MASTER3_ADDRESS_DECODER_TABLE(2) &
	ROUTER2_MASTER3_ADDRESS_DECODER_TABLE(3) &
	ROUTER2_MASTER3_ADDRESS_DECODER_TABLE(4) &
	ROUTER2_MASTER3_ADDRESS_DECODER_TABLE(5) &
	ROUTER2_MASTER3_ADDRESS_DECODER_TABLE(6) &
	ROUTER2_MASTER3_ADDRESS_DECODER_TABLE(7) &
	ROUTER3_MASTER0_ADDRESS_DECODER_TABLE(0) &
	ROUTER3_MASTER0_ADDRESS_DECODER_TABLE(1) &
	ROUTER3_MASTER0_ADDRESS_DECODER_TABLE(2) &
	ROUTER3_MASTER0_ADDRESS_DECODER_TABLE(3) &
	ROUTER3_MASTER0_ADDRESS_DECODER_TABLE(4) &
	ROUTER3_MASTER0_ADDRESS_DECODER_TABLE(5) &
	ROUTER3_MASTER0_ADDRESS_DECODER_TABLE(6) &
	ROUTER3_MASTER0_ADDRESS_DECODER_TABLE(7) &
	ROUTER3_MASTER1_ADDRESS_DECODER_TABLE(0) &
	ROUTER3_MASTER1_ADDRESS_DECODER_TABLE(1) &
	ROUTER3_MASTER1_ADDRESS_DECODER_TABLE(2) &
	ROUTER3_MASTER1_ADDRESS_DECODER_TABLE(3) &
	ROUTER3_MASTER1_ADDRESS_DECODER_TABLE(4) &
	ROUTER3_MASTER1_ADDRESS_DECODER_TABLE(5) &
	ROUTER3_MASTER1_ADDRESS_DECODER_TABLE(6) &
	ROUTER3_MASTER1_ADDRESS_DECODER_TABLE(7) &
	ROUTER3_MASTER2_ADDRESS_DECODER_TABLE(0) &
	ROUTER3_MASTER2_ADDRESS_DECODER_TABLE(1) &
	ROUTER3_MASTER2_ADDRESS_DECODER_TABLE(2) &
	ROUTER3_MASTER2_ADDRESS_DECODER_TABLE(3) &
	ROUTER3_MASTER2_ADDRESS_DECODER_TABLE(4) &
	ROUTER3_MASTER2_ADDRESS_DECODER_TABLE(5) &
	ROUTER3_MASTER2_ADDRESS_DECODER_TABLE(6) &
	ROUTER3_MASTER2_ADDRESS_DECODER_TABLE(7) &
	ROUTER4_MASTER0_ADDRESS_DECODER_TABLE(0) &
	ROUTER4_MASTER0_ADDRESS_DECODER_TABLE(1) &
	ROUTER4_MASTER0_ADDRESS_DECODER_TABLE(2) &
	ROUTER4_MASTER0_ADDRESS_DECODER_TABLE(3) &
	ROUTER4_MASTER0_ADDRESS_DECODER_TABLE(4) &
	ROUTER4_MASTER0_ADDRESS_DECODER_TABLE(5) &
	ROUTER4_MASTER0_ADDRESS_DECODER_TABLE(6) &
	ROUTER4_MASTER0_ADDRESS_DECODER_TABLE(7) &
	ROUTER4_MASTER1_ADDRESS_DECODER_TABLE(0) &
	ROUTER4_MASTER1_ADDRESS_DECODER_TABLE(1) &
	ROUTER4_MASTER1_ADDRESS_DECODER_TABLE(2) &
	ROUTER4_MASTER1_ADDRESS_DECODER_TABLE(3) &
	ROUTER4_MASTER1_ADDRESS_DECODER_TABLE(4) &
	ROUTER4_MASTER1_ADDRESS_DECODER_TABLE(5) &
	ROUTER4_MASTER1_ADDRESS_DECODER_TABLE(6) &
	ROUTER4_MASTER1_ADDRESS_DECODER_TABLE(7) &
	ROUTER4_MASTER2_ADDRESS_DECODER_TABLE(0) &
	ROUTER4_MASTER2_ADDRESS_DECODER_TABLE(1) &
	ROUTER4_MASTER2_ADDRESS_DECODER_TABLE(2) &
	ROUTER4_MASTER2_ADDRESS_DECODER_TABLE(3) &
	ROUTER4_MASTER2_ADDRESS_DECODER_TABLE(4) &
	ROUTER4_MASTER2_ADDRESS_DECODER_TABLE(5) &
	ROUTER4_MASTER2_ADDRESS_DECODER_TABLE(6) &
	ROUTER4_MASTER2_ADDRESS_DECODER_TABLE(7) &
	ROUTER4_MASTER3_ADDRESS_DECODER_TABLE(0) &
	ROUTER4_MASTER3_ADDRESS_DECODER_TABLE(1) &
	ROUTER4_MASTER3_ADDRESS_DECODER_TABLE(2) &
	ROUTER4_MASTER3_ADDRESS_DECODER_TABLE(3) &
	ROUTER4_MASTER3_ADDRESS_DECODER_TABLE(4) &
	ROUTER4_MASTER3_ADDRESS_DECODER_TABLE(5) &
	ROUTER4_MASTER3_ADDRESS_DECODER_TABLE(6) &
	ROUTER4_MASTER3_ADDRESS_DECODER_TABLE(7) &
	ROUTER5_MASTER0_ADDRESS_DECODER_TABLE(0) &
	ROUTER5_MASTER0_ADDRESS_DECODER_TABLE(1) &
	ROUTER5_MASTER0_ADDRESS_DECODER_TABLE(2) &
	ROUTER5_MASTER0_ADDRESS_DECODER_TABLE(3) &
	ROUTER5_MASTER0_ADDRESS_DECODER_TABLE(4) &
	ROUTER5_MASTER0_ADDRESS_DECODER_TABLE(5) &
	ROUTER5_MASTER0_ADDRESS_DECODER_TABLE(6) &
	ROUTER5_MASTER0_ADDRESS_DECODER_TABLE(7) &
	ROUTER5_MASTER0_ADDRESS_DECODER_TABLE(8)
	); 
        '''
        fw= open(outputdir + "/noc_config_configurable_part2_9.vhd", 'w')
        fw.write("%s" %ch)
        fw.close()
		
		
        
    def generate_configurable_part2_10(self):
        outputdir = "./Noc0__"
        if not os.path.exists(outputdir):
            os.makedirs(outputdir)
        self.nbr_R = int(self.entry_nbr_routeur.get())
        self.nbr_M = [0 for i in range(self.nbr_R)]
        self.nbr_S = [0 for i in range(self.nbr_R)]

        for r in range(int(self.entry_nbr_routeur.get())):
            self.nbr_M[r] = int(self.damierNbrMaitre[r].get())
            self.nbr_S[r] = int(self.damierNbrEsclave[r].get())
        ch='''
------ 10) ADDRESS DECODER PARAMETER MATRIX ------
--one line for each router (from 0 to y)
--one column for each master of each router (from 0 to 14)
--the goal is to define one couple of value "(MASTER_TABLE_RANK_NB, MASTER_DECOD_TABLE_SIZE)" for each master of each router
--MASTER_TABLE_RANK_NB = rank of the address decoding rule in the total number of rules (it is equal to the cumulated number of rules in the previous master address decoders)
--MASTER_DECOD_TABLE_SIZE = number of address decoding rule in the current master address decoder table
constant ADD_DECODER_PARAMETER_MX :  matrix_add_decoder_parameter :=(
((0,9), 	(9,8), 		(17,8), 	(25,8), 	(0,0), 		(0,0), 		(0,0), 		(0,0), 	(0,0), (0,0), (0,0), (0,0), (0,0), (0,0), (0,0)), 	-- ROUTER 0
((0,0), 	(0,0), 		(0,0), 		(0,0), 		(0,0), 		(0,0), 		(0,0), 		(0,0), 	(0,0), (0,0), (0,0), (0,0), (0,0), (0,0), (0,0)),	-- ROUTER 1
((33,8), 	(41,8),		(49,8), 	(57,8), 	(0,0), 		(0,0), 		(0,0), 		(0,0), 	(0,0), (0,0), (0,0), (0,0), (0,0), (0,0), (0,0)),	-- ROUTER 2
((65,8), 	(73,8),	 	(81,8), 	(0,0), 		(0,0), 		(0,0), 		(0,0), 		(0,0), 	(0,0), (0,0), (0,0), (0,0), (0,0), (0,0), (0,0)),	-- ROUTER 3
((89,8), 	(97,8),	 	(105,8), 	(113,8), 	(0,0), 		(0,0), 		(0,0), 		(0,0), 	(0,0), (0,0), (0,0), (0,0), (0,0), (0,0), (0,0)),	-- ROUTER 4
((121,9), 	(0,0), 		(0,0), 		(0,0), 		(0,0), 		(0,0), 		(0,0), 		(0,0), 	(0,0), (0,0), (0,0), (0,0), (0,0), (0,0), (0,0))    -- ROUTER 5
);
--MASTER	MASTER		MASTER		MASTER		MASTER		MASTER		MASTER		MASTER	MASTER...
--0			1			2			3			4			5			6			7		8		9	   10	  11    12     13      14   

        '''
        fw= open(outputdir + "/noc_config_configurable_part2_10.vhd", 'w')
        fw.write("%s" %ch)
        fw.close()
		
		
    def generate_configurable_part2_11(self):
        outputdir = "./Noc0__"
        if not os.path.exists(outputdir):
            os.makedirs(outputdir)
        self.nbr_R = int(self.entry_nbr_routeur.get())
        self.nbr_M = [0 for i in range(self.nbr_R)]
        self.nbr_S = [0 for i in range(self.nbr_R)]

        for r in range(int(self.entry_nbr_routeur.get())):
            self.nbr_M[r] = int(self.damierNbrMaitre[r].get())
            self.nbr_S[r] = int(self.damierNbrEsclave[r].get())
        ch='''
------ 11) ROUTING TABLE  -------
--define for each router a routing table that gives the destination port to take
--to reach all the other routers of the network.
-- 1rst value) router destination address in regROUTERADD format.
-- 2nd value) local router port address
constant ROUTER0_ROUTING_TABLE : routing_table_array:=(
	(ROUTER1, from_ROUTER0_to_ROUTER1_destination_port),
	(ROUTER2, from_ROUTER0_to_ROUTER2_destination_port),
	(ROUTER3, from_ROUTER0_to_ROUTER3_destination_port),
	(ROUTER4, from_ROUTER0_to_ROUTER4_destination_port),
	(ROUTER5, from_ROUTER0_to_ROUTER5_destination_port));
		
constant ROUTER1_ROUTING_TABLE : routing_table_array:=( 
	(ROUTER0, from_ROUTER1_to_ROUTER0_destination_port),
	(ROUTER2, from_ROUTER1_to_ROUTER2_destination_port),
	(ROUTER3, from_ROUTER1_to_ROUTER3_destination_port),
	(ROUTER4, from_ROUTER1_to_ROUTER4_destination_port),
	(ROUTER5, from_ROUTER1_to_ROUTER5_destination_port));
		
constant ROUTER2_ROUTING_TABLE : routing_table_array:=(
	(ROUTER0, from_ROUTER2_to_ROUTER0_destination_port),
	(ROUTER1, from_ROUTER2_to_ROUTER1_destination_port),
	(ROUTER3, from_ROUTER2_to_ROUTER3_destination_port),
	(ROUTER4, from_ROUTER2_to_ROUTER4_destination_port),
	(ROUTER5, from_ROUTER2_to_ROUTER5_destination_port));
	
constant ROUTER3_ROUTING_TABLE : routing_table_array:=(
	(ROUTER0, from_ROUTER3_to_ROUTER0_destination_port),
	(ROUTER1, from_ROUTER3_to_ROUTER1_destination_port),
	(ROUTER2, from_ROUTER3_to_ROUTER2_destination_port),
	(ROUTER4, from_ROUTER3_to_ROUTER4_destination_port),
	(ROUTER5, from_ROUTER3_to_ROUTER5_destination_port));
		
constant ROUTER4_ROUTING_TABLE : routing_table_array:=( 
	(ROUTER0, from_ROUTER4_to_ROUTER0_destination_port),
	(ROUTER1, from_ROUTER4_to_ROUTER1_destination_port),
	(ROUTER2, from_ROUTER4_to_ROUTER2_destination_port),
	(ROUTER3, from_ROUTER4_to_ROUTER3_destination_port),
	(ROUTER5, from_ROUTER4_to_ROUTER5_destination_port));
		
constant ROUTER5_ROUTING_TABLE : routing_table_array:=( 
	(ROUTER0, from_ROUTER5_to_ROUTER0_destination_port),
	(ROUTER1, from_ROUTER5_to_ROUTER1_destination_port),
	(ROUTER2, from_ROUTER5_to_ROUTER2_destination_port),
	(ROUTER3, from_ROUTER5_to_ROUTER3_destination_port),
	(ROUTER4, from_ROUTER5_to_ROUTER4_destination_port));
	
-- => AGGREGATING ARRAY <= --
constant ALL_ROUTING_TABLES : array_all_routing_tables:=(
	ROUTER0_ROUTING_TABLE,
	ROUTER1_ROUTING_TABLE,
	ROUTER2_ROUTING_TABLE,
	ROUTER3_ROUTING_TABLE,
	ROUTER4_ROUTING_TABLE,
	ROUTER5_ROUTING_TABLE
);
        '''
        fw= open(outputdir + "/noc_config_configurable_part2_11.vhd", 'w')
        fw.write("%s" %ch)
        fw.close()
	
	
	
    def generate_configurable_part2_12_1(self):
        outputdir = "./Noc0__"
        self.nbr_R = int(self.entry_nbr_routeur.get())
        self.nbr_M = [0 for i in range(self.nbr_R)]
        self.nbr_S = [0 for i in range(self.nbr_R)]

        for r in range(int(self.entry_nbr_routeur.get())):
            self.nbr_M[r] = int(self.damierNbrMaitre[r].get())
            self.nbr_S[r] = int(self.damierNbrEsclave[r].get())
        ch='''
        
        '''
        fw= open(outputdir + "/noc_config_configurable_part2_12_1.vhd", 'w')
        fw.write("------ 9) LOCAL CONNEXIONS MATRIX ------ \n")
        for r in range(self.nbr_R):
            fw.write('constant ROUTER%d_LOCAL_MX    : local_connexion_matrix :=(           \n ' %r)
            fw.write('\n')
            fw.write(' (0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0), -- slave 0 Mij (0:14),Single_master,LOCAL_MASTER_RANK \n')
            fw.write(" (0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0), -- slave 1                                            \n")                                         
            fw.write(" (0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0), -- slave 2                                            \n")
            fw.write(" (0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0), -- slave 3                                            \n")
            fw.write(" (0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0), -- slave 4                                            \n")
            fw.write(" (0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0), -- slave 5                                            \n")
            fw.write(" (0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0), -- slave 6                                            \n")
            fw.write(" (0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0), -- slave 7                                            \n")
            fw.write(" (0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0), -- slave 8                                            \n")
            fw.write(" (0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0), -- slave 9                                            \n")
            fw.write(" (0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0), -- slave 10                                           \n")
            fw.write(" (0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0), -- slave 11                                           \n")
            fw.write(" (0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0), -- slave 12                                           \n")
            fw.write(" (0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0), -- slave 13                                           \n")
            fw.write(" (0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0), -- slave 14                                           \n")
            fw.write(" (0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0), -- single_slave                                       \n")
            fw.write(" (0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0));-- slave rank                                         \n")
            fw.write("--m m m m m m m m m m m m m m m s m                                                          \n")
            fw.write("--a a a a a a a a a a a a a a a i r                                                          \n")
            fw.write("--s s s s s s s s s s s s s s s n a                                                          \n")
            fw.write("--t t t t t t t t t t t t t t t g n                                                          \n")
            fw.write("--e e e e e e e e e e e e e e e l k                                                          \n")
            fw.write("--r r r r r r r r r r r r r r r e                                                            \n")
            fw.write("--0 1 2 3 4 5 6 7 8 9 1 1 1 1 1 m                                                            \n")                                           
            fw.write("--                    0 1 2 3 4                                                              \n")
            fw.write('\n')
            fw.write('\n')
            fw.write('\n')
        fw.close()


    def generate_configurable_part2_12_2(self):
        outputdir = "./Noc0__"
        if not os.path.exists(outputdir):
            os.makedirs(outputdir)
        self.nbr_R = int(self.entry_nbr_routeur.get())
        self.nbr_M = [0 for i in range(self.nbr_R)]
        self.nbr_S = [0 for i in range(self.nbr_R)]

        for r in range(int(self.entry_nbr_routeur.get())):
            self.nbr_M[r] = int(self.damierNbrMaitre[r].get())
            self.nbr_S[r] = int(self.damierNbrEsclave[r].get())
        ch='''

-- => AGGREGATING ARRAY <= --
constant ALL_ROUTER_LOCAL_MATRIX : array_all_local_connexion_matrix:=(
	ROUTER0_LOCAL_MX,
	ROUTER1_LOCAL_MX,
	ROUTER2_LOCAL_MX,
	ROUTER3_LOCAL_MX,
	ROUTER4_LOCAL_MX,
	ROUTER5_LOCAL_MX
);
    '''
        fw= open(outputdir + "/noc_config_configurable_part2_12_2.vhd", 'w')
        fw.write("%s" %ch)
        fw.close()
	
	
    def generate_end_of_file_with_function(self):
        outputdir = "./Noc0__"
        if not os.path.exists(outputdir):
            os.makedirs(outputdir)
        self.nbr_R = int(self.entry_nbr_routeur.get())
        self.nbr_M = [0 for i in range(self.nbr_R)]
        self.nbr_S = [0 for i in range(self.nbr_R)]

        for r in range(int(self.entry_nbr_routeur.get())):
            self.nbr_M[r] = int(self.damierNbrMaitre[r].get())
            self.nbr_S[r] = int(self.damierNbrEsclave[r].get())
        ch='''

end noc_address_pack;

package body noc_address_pack is

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

end noc_address_pack;
        
        '''
        fw= open(outputdir + "/noc_config_end_of_file_with_function.vhd", 'w')
        fw.write("%s" %ch)
        fw.close()


    def generate_vhdl_file(self):
        error_found=0
        #Vérifier que le dossier existe, il est créé si nécessaire
        outputdir = "./Noc0__"
        if not os.path.exists(outputdir):
            os.makedirs(outputdir)
        generated_files=["/noc_config_configurable_part1.vhd","/noc_config_fixed_part.vhd","/noc_config_configurable_part2_1.vhd","/noc_config_configurable_part2_2.vhd","/noc_config_configurable_part2_3.vhd","/noc_config_configurable_part2_4.vhd","/noc_config_configurable_part2_5.vhd","/noc_config_configurable_part2_6.vhd","/noc_config_configurable_part2_7.vhd","/noc_config_configurable_part2_8.vhd","/noc_config_configurable_part2_9.vhd","/noc_config_configurable_part2_10.vhd","/noc_config_configurable_part2_11.vhd","/noc_config_configurable_part2_12_1.vhd","/noc_config_configurable_part2_12_2.vhd","/noc_config_end_of_file_with_function.vhd"]
        self.generate_configurable_part1()
        self.generate_fixed_part()
        self.generate_configurable_part2_1()
        self.generate_configurable_part2_2()
        self.generate_configurable_part2_3()
        self.generate_configurable_part2_4()
        #self.generate_configurable_part2_5()
        self.generate_configurable_part2_6()
        self.generate_configurable_part2_7()
        self.generate_configurable_part2_8()
        self.generate_configurable_part2_9()
        self.generate_configurable_part2_10()
        self.generate_configurable_part2_11()
        self.generate_configurable_part2_12_1()
        self.generate_configurable_part2_12_2()
        self.generate_end_of_file_with_function()
        for i in range(len(generated_files)):
            if not os.path.exists(outputdir+generated_files[i]):
                error_found=1
        if error_found:
            showerror("Erreur", 'Enregistrer avant vos modifications dans (configuration des connexions locales), (configurations des decodeurs d\'adresses) ou (configurations des connexions en paquets)' )
        else:
            # génère le fichier de sortie
            with open(outputdir + "/noc_config.vhd",'w') as new_file:
                with open(outputdir + "/noc_config_configurable_part1.vhd") as old_file:
                    for line in old_file:   
                        new_file.write(line)
                with open(outputdir + "/noc_config_fixed_part.vhd") as old_file:
                    for line in old_file:   
                        new_file.write(line)
                with open(outputdir + "/noc_config_configurable_part2_1.vhd") as old_file:
                    for line in old_file:   
                        new_file.write(line)
                with open(outputdir + "/noc_config_configurable_part2_2.vhd") as old_file:
                    for line in old_file:   
                        new_file.write(line)
                with open(outputdir + "/noc_config_configurable_part2_3.vhd") as old_file:
                    for line in old_file:   
                        new_file.write(line)
                with open(outputdir + "/noc_config_configurable_part2_4.vhd") as old_file:
                    for line in old_file:   
                        new_file.write(line)
                with open(outputdir + "/noc_config_configurable_part2_5.vhd") as old_file:
                    for line in old_file:   
                        new_file.write(line)
                with open(outputdir + "/noc_config_configurable_part2_6.vhd") as old_file:
                    for line in old_file:   
                        new_file.write(line)
                with open(outputdir + "/noc_config_configurable_part2_7.vhd") as old_file:
                    for line in old_file:   
                        new_file.write(line)
                with open(outputdir + "/noc_config_configurable_part2_8.vhd") as old_file:
                    for line in old_file:   
                        new_file.write(line)
                with open(outputdir + "/noc_config_configurable_part2_9.vhd") as old_file:
                    for line in old_file:   
                        new_file.write(line)
                with open(outputdir + "/noc_config_configurable_part2_10.vhd") as old_file:
                    for line in old_file:
                        new_file.write(line)
                with open(outputdir + "/noc_config_configurable_part2_11.vhd") as old_file:
                    for line in old_file:   
                        new_file.write(line)
                with open(outputdir + "/noc_config_configurable_part2_12_1.vhd") as old_file:
                    for line in old_file:   
                        new_file.write(line)
                with open(outputdir + "/noc_config_configurable_part2_12_2.vhd") as old_file:
                    for line in old_file:   
                        new_file.write(line)
                with open(outputdir + "/noc_config_end_of_file_with_function.vhd") as old_file:
                    for line in old_file:   
                        new_file.write(line)
				
            os.remove(outputdir + "/noc_config_configurable_part1.vhd")
            os.remove(outputdir + "/noc_config_fixed_part.vhd")
            os.remove(outputdir + "/noc_config_configurable_part2_1.vhd")
            os.remove(outputdir + "/noc_config_configurable_part2_2.vhd")
            os.remove(outputdir + "/noc_config_configurable_part2_3.vhd")
            os.remove(outputdir + "/noc_config_configurable_part2_4.vhd")
            os.remove(outputdir + "/noc_config_configurable_part2_5.vhd")
            os.remove(outputdir + "/noc_config_configurable_part2_6.vhd")
            os.remove(outputdir + "/noc_config_configurable_part2_7.vhd")
            os.remove(outputdir + "/noc_config_configurable_part2_8.vhd")
            os.remove(outputdir + "/noc_config_configurable_part2_9.vhd")
            os.remove(outputdir + "/noc_config_configurable_part2_10.vhd")
            os.remove(outputdir + "/noc_config_configurable_part2_11.vhd")
            os.remove(outputdir + "/noc_config_configurable_part2_12_1.vhd")
            os.remove(outputdir + "/noc_config_configurable_part2_12_2.vhd")
            os.remove(outputdir + "/noc_config_end_of_file_with_function.vhd")

# copier les sources VHDL
filelist = [ 
    "noc_address_pack.vhd"
    ]
#classe for copying VHDL files    
class copyothersfiles():
    def __init__(self, NocName ):
        #Vérifier que le dossier existe, il est créé si nécessaire
        outputdir = "./"+NocName
        if not os.path.exists(outputdir):
            os.makedirs(outputdir)
    
        #Copie les fichiers
        for f in filelist:
            shutil.copy2('./base/'+ f, outputdir + '/' + f)

#classe pour gérer les connexions locales
class LocalConnexion(Tk):
    def __init__(self, nbr_r_p,nbr_m_p,nbr_s_p ):
        root = Tk.__init__(self)
        var = []
        row_cont=0
        self.title("Configuration des connexions locales")
        self.geometry("600x370")
        self.frame = VerticalScrolledFrame(self)
        self.frame.grid(row=0, column=0,sticky=N)
        self.nbr_R = nbr_r_p
        self.nbr_M = nbr_m_p
        self.nbr_S = nbr_s_p
        self.is_selected_flag=0
        Connexion_local =[[[ 0 for i in range(self.nbr_R) ] for j in range(len(self.nbr_M))] for j in range(len(self.nbr_S)) ]
        label_0    = []
        Routeurs   = []
        Maitres    = []
        Esclaves   = []
        self.Connexions = []
        label_0   .append(Label(self.frame.interior, text="", width=6))
        Routeurs  .append(Label(self.frame.interior, text="Routeur  "))
        Maitres   .append(Label(self.frame.interior, text="Maitre   "))
        Esclaves  .append(Label(self.frame.interior, text="Esclave  "))
        self.Connexions.append(Label(self.frame.interior, text="Connexion"))
#       print ('Avant de commencer les loop')
#       print ('self.nbr_R = %d ' % self.nbr_R)
#       print ('self.nbr_M[0] = %d ' % self.nbr_M[0])
        for r in range(self.nbr_R):
            for m in range(self.nbr_M[r]):
                for s in range(self.nbr_M[r],self.nbr_M[r]+self.nbr_S[r]):
                    Routeurs  .append(Button(self.frame.interior, text=str(r), state=DISABLED, width=7))
                    Maitres   .append(Button(self.frame.interior, text=str(m+1), state=DISABLED, width=7))
                    Esclaves  .append(Button(self.frame.interior, text=str(s+1), state=DISABLED, width=7))
                    self.Connexions.append(Checkbutton(self.frame.interior, variable=var))
                    row_cont=row_cont +1
                    Connexion_local[r][m][s-self.nbr_M[r]]= var
        
        label_0[0]      .grid(row=0, column=1)
        for i in range(len(Esclaves)):
            Routeurs[i]  .grid(row=i, column=2)
            Maitres[i]   .grid(row=i, column=3)
            Esclaves[i]  .grid(row=i, column=4)
            self.Connexions[i].grid(row=i, column=5)
        Button(self, text="Tout Connecter/Deconnecter", width=22, command=self.on_buttonToutConnecter_clicked).grid(row=18, column=3)
        Button(self, text="Save", width=22, command=self.on_buttonsave_clicked).grid(row=19, column=3)


    def on_buttonToutConnecter_clicked(self):
        print("Tout connecter")
        if self.is_selected_flag==0:
            for i in range(1,len(self.Connexions)):
                self.Connexions[i].select()
            self.is_selected_flag=1
        else:
            for i in range(1,len(self.Connexions)):
                self.Connexions[i].deselect()
            self.is_selected_flag=0

 
    def on_buttonsave_clicked(self):
        print("Configuration des connexions locales")    
        self.quit()



#classe pour gérer les connexions en paquets
class PaquetConnexion(Tk):
    def __init__(self,nbr_r_p,nbr_m_p,nbr_s_p):
        root = Tk.__init__(self)
        self.var = []
        row_cont=0
        self.title("Configuration des connexions en paquets")
        self.geometry("520x370")
        self.frame = VerticalScrolledFrame(self)
        self.frame.grid(row=0, column=0,sticky=N)
        self.nbr_R = nbr_r_p
        self.nbr_M = nbr_m_p
        self.nbr_S = nbr_s_p
        self.is_selected_flag=0
        Connexion_local =[[[ 0 for i in range(self.nbr_R) ] for j in range(len(self.nbr_M))] for j in range(len(self.nbr_S)) ]
        label_0    = []
        Routeurs   = []
        Maitres    = []
        #Esclaves   = []
        self.Connexions = []
        label_0   .append(Label(self.frame.interior, text="", width=6))
        Routeurs  .append(Label(self.frame.interior, text="Routeur  "))
        Maitres   .append(Label(self.frame.interior, text="  IP "))
        #Esclaves  .append(Label(self.frame.interior, text="Esclave  "))
        self.Connexions.append(Label(self.frame.interior, text="Connexion"))

        for r in range(self.nbr_R):
            for m in range(self.nbr_M[r]):
                Routeurs  .append(Button(self.frame.interior, text=str(r), state=DISABLED, width=7))
                Maitres   .append(Button(self.frame.interior, text=str(m+1)+"(Maitre)", state=DISABLED, width=7))
                self.Connexions.append(Checkbutton(self.frame.interior, variable=self.var))
                row_cont=row_cont +1
                #Connexion_local[r][m][s-self.nbr_M[r]]= var

            for s in range(self.nbr_M[r],self.nbr_M[r]+self.nbr_S[r]):
                Routeurs  .append(Button(self.frame.interior, text=str(r), state=DISABLED, width=7))
                Maitres   .append(Button(self.frame.interior, text=str(s+1)+"(Esclave)", state=DISABLED, width=7))
                #Esclaves  .append(Button(self.frame.interior, text=str(s+1), state=DISABLED, width=7))
                self.Connexions.append(Checkbutton(self.frame.interior, variable=self.var))
                row_cont=row_cont +1
                #Connexion_local[r][m][s-self.nbr_M[r]]= self.var[r+s]
        
        label_0[0]      .grid(row=0, column=1)
        for i in range(len(Maitres)):
            Routeurs[i]  .grid(row=i, column=2)
            Maitres[i]   .grid(row=i, column=3)
            #Esclaves[i]  .grid(row=i, column=4)
            self.Connexions[i].grid(row=i, column=4)
        Button(self, text="Tout Connecter/Deconnecter", width=22, command=self.on_buttonToutConnecter_clicked).grid(row=18, column=3)
        Button(self, text="Save", width=22, command=self.on_buttonsave_clicked).grid(row=19, column=3)


    def on_buttonToutConnecter_clicked(self):
        print("Tout connecter")
        if self.is_selected_flag==0:
            for i in range(1,len(self.Connexions)):
                self.Connexions[i].select()
            self.is_selected_flag=1
        else:
            for i in range(1,len(self.Connexions)):
                self.Connexions[i].deselect()
            self.is_selected_flag=0

    def on_buttonsave_clicked(self):
        print("Configuration des connexions en paquets")    
        #for i in range(1,len(self.Connexions)):
            #print("self.var_checkbutton[%d]= %r" % (i,self.var[i-1].get()))  
        self.quit()
 


#classe pour gérer le décodeur d'adresses
class Decodeur_d_adresse(Tk):
    def __init__(self, nbr_r_p,nbr_m_p,nbr_s_p):
        root = Tk.__init__(self)
        var = []
        row_cont=0
        self.title("Configuration des decodeurs d'adresses")
        self.geometry("580x310")
        self.frame = VerticalScrolledFrame(self)
        self.frame.grid(row=0, column=0,sticky=N)
        #print('nbr_R_Global in Decodeur dadresse = %d' % args)
        self.nbr_R = nbr_r_p
        self.nbr_M = nbr_m_p
        self.nbr_S = nbr_s_p
        label_0    = []
        Routeurs   = []
        Esclaves    = []
        self.Adresse_basse   = []
        self.Adresse_haute = []
        label_0.append(Label(self.frame.interior, text="", width=6))
        Routeurs.append(Label(self.frame.interior, text="Routeur"))
        Esclaves.append(Label(self.frame.interior, text="Esclave"))
        self.Adresse_basse.append(Label(self.frame.interior, text="Adresse basse (Hex)  "))
        self.Adresse_haute.append(Label(self.frame.interior, text="Adresse haute (Hex)"))
        for r in range(self.nbr_R):
            for s in range(self.nbr_M[r],self.nbr_M[r]+self.nbr_S[r]):
                Routeurs  .append(Button(self.frame.interior, text=str(r), state=DISABLED, width=10))
                Esclaves   .append(Button(self.frame.interior, text=str(s+1), state=DISABLED, width=10))
                self.Adresse_basse  .append(Entry(self.frame.interior))
                self.Adresse_haute.append(Entry(self.frame.interior))
				# self.Adresse_basse.insert("00000000")
				# self.Adresse_haute.insert("00000000")
                row_cont=row_cont +1
        
        label_0[0]      .grid(row=0, column=1)
        for i in range(len(Esclaves)):
            Routeurs[i]  .grid(row=i, column=2)
            Esclaves[i]   .grid(row=i, column=3)
            self.Adresse_basse[i]  .grid(row=i, column=4)
            self.Adresse_haute[i].grid(row=i, column=5)
        Button(self, text="Save", width=12, command=self.on_buttonsave_clicked).grid(row=10, column=3)

    def on_buttonsave_clicked(self):
        error_flag=0
        print("Configuration du  decodeur d'adresses enregistree")    
        for i in range(1,len(self.Adresse_basse)):
            if not(re.match("^[A-Fa-f0-9_-]*$", self.Adresse_haute[i].get())) or len(self.Adresse_haute[i].get())!=8 or not(re.match("^[A-Fa-f0-9_-]*$", self.Adresse_basse[i].get())) or len(self.Adresse_basse[i].get())!=8:
                showerror("Erreur", '[%s] n\'est pas une adresse Hexadecimale valide \n Info: Une adresse valide contient 8 caracteres [A-Fa-f0-9]' %self.Adresse_haute[i].get())
                error_flag=1
        if error_flag==0:
            outputdir = "./Noc0__"
            if not os.path.exists(outputdir):
                os.makedirs(outputdir)
            fw= open(outputdir + "/noc_config_configurable_part2_5.vhd", 'w')
            fw.write("------ 5) CROSSBAR 32-bits SLAVE ADDRESSES ------ \n")
            fw.write('\n')
            for r in range(self.nbr_R):
                fw.write('-- ROUTER %d --\n' %r)
                for s in range(self.nbr_M[r],self.nbr_M[r]+self.nbr_S[r]):
                    fw.write('-- Slave %d --\n' %s)
                    fw.write('constant  ROUTER%d_SLAVE%d_BASE_ADD     : std_logic_vector(ADD_SIZE-1 downto 0):= X"%s";\n' %(r,s,self.Adresse_basse[r+1].get()))
                    fw.write('constant  ROUTER%d_SLAVE%d_HIGH_ADD     : std_logic_vector(ADD_SIZE-1 downto 0):= X"%s";\n' %(r,s,self.Adresse_haute[r+1].get()))
                    fw.write('\n')
            fw.close()
            self.quit()
       


# Main        
if __name__ == "__main__":
    
    fenetre = Tk()
    fenetre.title("Outil de generation de configurations NoC (Version 0.2)")
    interface = Interface(fenetre)
    print('nbr_R_Global in Main = %d' % Interface.nbr_R_Global)
	
    #definit une taille minimale pour la fenêtre (en dessous de laquelle on ne peut descendre)
    fenetre.update()
    fenetre.minsize(fenetre.winfo_width(), fenetre.winfo_height())

    interface.mainloop()
