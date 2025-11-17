# -*- coding: utf-8 -*-
import pygame
import setari as s 

# --- Setări pentru Interfață ---
CULOARE_TEXT = (255, 255, 255) # Alb
CULOARE_CASTIG = (255, 215, 0) # Auriu
CULOARE_BUTON = (50, 50, 50) # Gri închis
MARIME_FONT_PRINCIPAL = 30
MARIME_FONT_CASTIG = 40

class Interfata:
    """
    Gestionează desenarea tuturor elementelor de UI (text, balanță, miză).
    """
    def __init__(self):
        self.ecran = pygame.display.get_surface()
        
        try:
            self.font_principal = pygame.font.Font('grafica/grafica/font/Slot-Regular.otf', MARIME_FONT_PRINCIPAL)
            self.font_castig = pygame.font.Font('grafica/grafica/font/Slot-Regular.otf', MARIME_FONT_CASTIG)
        except FileNotFoundError:
            print("Avertisment: Nu am găsit fontul personalizat. Folosesc fontul implicit.")
            self.font_principal = pygame.font.Font(None, MARIME_FONT_PRINCIPAL + 5)
            self.font_castig = pygame.font.Font(None, MARIME_FONT_CASTIG + 5)
            
        # --- MODIFICAT: Stocăm rect-urile butoanelor pentru click ---
        self.rect_miza_minus = None
        self.rect_miza_plus = None
        self.rect_start_stop = None # <-- NOU

    def afiseaza_text(self, text, font, culoare, pozitie_centru):
        """ 
        O metodă ajutătoare pentru a desena text centrat. 
        MODIFICAT: Acum returnează rect-ul textului desenat.
        """
        suprafata_text = font.render(text, True, culoare)
        rect_text = suprafata_text.get_rect(center=pozitie_centru)
        self.ecran.blit(suprafata_text, rect_text)
        return rect_text # <-- Linie adăugată

    # --- MODIFICAT: Am adăugat 'poate_roti' la parametrii ---
    def desenare(self, balanta, miza_pe_linie, numar_linii, ultimul_castig, poate_roti):
        """
        Metoda principală de desenare, apelată în fiecare frame din 'principal.py'.
        """
        
        # --- Desenează o bandă neagră jos pentru text ---
        banda_jos_rect = pygame.Rect(0, s.INALTIME - 60, s.LATIME, 80)
        pygame.draw.rect(self.ecran, 'black', banda_jos_rect)
        
        # ---- De desenat banda sus
        
        miza_totala = miza_pe_linie * numar_linii
        
        # --- Definim dimensiuni comune pentru butoane ---
        marime_buton_patrat = 35
        padding_buton = 10
        y_buton = s.INALTIME - 40 - (marime_buton_patrat // 2)
        
        # --- Balanța ---
        text_balanta = f"Credit: {balanta:.2f} RON"
        pozitie_balanta = (200, s.INALTIME - 40)
        rect_text_balanta = self.afiseaza_text(text_balanta, self.font_principal, CULOARE_TEXT, pozitie_balanta)

        # --- NOU: Butonul START/STOP ---
        text_buton_start = "START" if poate_roti else "STOP"
        latime_buton_start = 100
        x_start_stop = rect_text_balanta.right + padding_buton
        self.rect_start_stop = pygame.Rect(x_start_stop, y_buton, latime_buton_start, marime_buton_patrat)
        pygame.draw.rect(self.ecran, CULOARE_BUTON, self.rect_start_stop, border_radius=5)
        self.afiseaza_text(text_buton_start, self.font_principal, CULOARE_TEXT, self.rect_start_stop.center)
        # --- Sfârșit buton START/STOP ---

        # --- Miza și Butoanele (SECȚIUNE MODIFICATĂ) ---
        text_miza = f"Miza: {miza_totala:.2f} RON ({numar_linii} linii)"
        pozitie_miza = (s.LATIME - 280, s.INALTIME - 40)
        rect_text_miza = self.afiseaza_text(text_miza, self.font_principal, CULOARE_TEXT, pozitie_miza)

        # Buton Minus (-)
        x_minus = rect_text_miza.left - padding_buton - marime_buton_patrat
        self.rect_miza_minus = pygame.Rect(x_minus, y_buton, marime_buton_patrat, marime_buton_patrat)
        pygame.draw.rect(self.ecran, CULOARE_BUTON, self.rect_miza_minus, border_radius=5)
        self.afiseaza_text("-", self.font_castig, CULOARE_TEXT, self.rect_miza_minus.center)

        # Buton Plus (+)
        x_plus = rect_text_miza.right + padding_buton
        self.rect_miza_plus = pygame.Rect(x_plus, y_buton, marime_buton_patrat, marime_buton_patrat)
        pygame.draw.rect(self.ecran, CULOARE_BUTON, self.rect_miza_plus, border_radius=5)
        self.afiseaza_text("+", self.font_castig, CULOARE_TEXT, self.rect_miza_plus.center)
        # --- Sfârșit secțiune butoane miză ---

        # --- Câștig ---
        if ultimul_castig > 0:
            text_castig = f"CASTIG: {ultimul_castig:.2f} RON"
            pozitie_castig = (s.LATIME / 2, s.INALTIME - 40)
            self.afiseaza_text(text_castig, self.font_castig, CULOARE_CASTIG, pozitie_castig)