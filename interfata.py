# -*- coding: utf-8 -*-
import pygame
import setari as s 

# --- Setări pentru Interfață ---
CULOARE_TEXT = (255, 255, 255) # Alb
CULOARE_CASTIG = (255, 215, 0) # Auriu
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

    def afiseaza_text(self, text, font, culoare, pozitie_centru):
        """ O metodă ajutătoare pentru a desena text centrat. """
        suprafata_text = font.render(text, True, culoare)
        rect_text = suprafata_text.get_rect(center=pozitie_centru)
        self.ecran.blit(suprafata_text, rect_text)

    def desenare(self, balanta, miza_pe_linie, numar_linii, ultimul_castig):
        """
        Metoda principală de desenare, apelată în fiecare frame din 'principal.py'.
        """
        
        # --- Desenează o bandă neagră jos pentru text ---
        banda_jos_rect = pygame.Rect(0, s.INALTIME - 60, s.LATIME, 80)
        pygame.draw.rect(self.ecran, 'black', banda_jos_rect)
        
        miza_totala = miza_pe_linie * numar_linii
        
        text_balanta = f"Credit: {balanta:.2f} RON"
        pozitie_balanta = (200, s.INALTIME - 40)
        self.afiseaza_text(text_balanta, self.font_principal, CULOARE_TEXT, pozitie_balanta)

        text_miza = f"Miza: {miza_totala} RON ({numar_linii} linii)"
        pozitie_miza = (s.LATIME - 200, s.INALTIME - 40)
        self.afiseaza_text(text_miza, self.font_principal, CULOARE_TEXT, pozitie_miza)

        if ultimul_castig > 0:
            text_castig = f"CASTIG: {ultimul_castig:.2f} RON"
            pozitie_castig = (s.LATIME / 2, s.INALTIME - 40)
            self.afiseaza_text(text_castig, self.font_castig, CULOARE_CASTIG, pozitie_castig)