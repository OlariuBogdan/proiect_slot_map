# -*- coding: utf-8 -*-
import pygame
import sys
import setari as s
from rola import Rola 
from interfata import Interfata

class Joc:
    def __init__(self):
        pygame.init()
        self.ecran = pygame.display.set_mode((s.LATIME, s.INALTIME), pygame.SCALED | pygame.FULLSCREEN)
        pygame.display.set_caption('Slot Machine - Teme MAP')
        self.ceas = pygame.time.Clock()
        
        try:
            self.fundal = pygame.image.load(s.CALE_FUNDAL).convert()
            self.fundal = pygame.transform.scale(self.fundal, (s.LATIME, s.INALTIME))
        except (AttributeError, FileNotFoundError):
            print("Notă: Nu s-a încărcat niciun fundal (CALE_FUNDAL nu e definită în setari.py). Se folosește fundal negru.")
            self.fundal = None
        
        # Starea jocului
        self.poate_roti = True
        
        # Datele jucătorului
        self.balanta = 1000.00
        self.miza_pe_linie = 1.00 
        self.numar_linii_plata = len(s.LINII_PLATA)
        self.miza_totala = self.miza_pe_linie * self.numar_linii_plata
        self.ultimul_castig_din_spin = 0.00

        # Componente
        self.lista_role = []
        self.interfata = Interfata()
        self.genereaza_role()
        
        # Variabilă pentru a stoca delta_time
        self.delta_time = 0.0

    def genereaza_role(self):
        """ 
        Creează cele 5 obiecte Rola și le poziționează pe ecran.
        """
        latime_totala_grila = s.DIMENSIUNE_CELULA * 5
        x_start = (s.LATIME - latime_totala_grila) / 2
        
        for i in range(5):
            pozitie_x_celula = x_start + i * s.DIMENSIUNE_CELULA
            self.lista_role.append(Rola(i, pozitie_x_celula))

    def run(self):
        """ Bucla principală a jocului. """
        # Timpul de start (pentru calculul delta_time)
        timp_anterior = pygame.time.get_ticks()

        while True:
            # --- MODIFICARE: Calcul delta_time corect ---
            # delta_time este timpul (în secunde) scurs de la ultimul frame
            timp_curent = pygame.time.get_ticks()
            self.delta_time = (timp_curent - timp_anterior) / 1000.0 # Împărțim la 1000.0 pt secunde
            timp_anterior = timp_curent
            # ----------------------------------------------
            
            self.gestioneaza_evenimente()
            self.update()
            self.desenare()
            self.ceas.tick(s.FPS) 

    def gestioneaza_evenimente(self):
        """ Gestionează input-ul (tastatură, închidere fereastră). """
        for eveniment in pygame.event.get():
            if eveniment.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if eveniment.type == pygame.KEYDOWN:
                if eveniment.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                
                if eveniment.key == pygame.K_SPACE and self.poate_roti:
                    self.spin()

    def spin(self):
        """ Inițiază o nouă rotire. """
        self.miza_totala = self.miza_pe_linie * self.numar_linii_plata
        
        if self.balanta < self.miza_totala:
            print("Fonduri insuficiente!")
            return 
            
        self.poate_roti = False
        self.balanta -= self.miza_totala
        self.ultimul_castig_din_spin = 0 
        
        for i, rola in enumerate(self.lista_role):
            durata_ms = 1000 + (i * 300)
            rola.start_spin(durata_ms)
            
    def update(self):
        """ Actualizează logica jocului în fiecare frame. """
        
        # --- MODIFICARE: Trimitem delta_time la fiecare rolă ---
        for rola in self.lista_role:
            rola.update(self.delta_time)
        # ----------------------------------------------------
            
        # Verificăm dacă s-a terminat o rotire (toate rolele sunt 'IDLE')
        if not self.poate_roti and all(rola.stare == 'IDLE' for rola in self.lista_role):
            self.poate_roti = True 
            
            matrice_rezultat = self.get_matrice_rezultat()
            castig_linii = self.verificare_castiguri_linii(matrice_rezultat)
            castig_scatter = self.verificare_scatter(matrice_rezultat)
            
            castig_total = castig_linii + castig_scatter
            self.ultimul_castig_din_spin = castig_total
            
            if castig_total > 0:
                print(f"Ai câștigat: {castig_total} RON!")
                self.balanta += castig_total

    def get_matrice_rezultat(self):
        """
        Returnează o matrice 3x5 (3 rânduri, 5 coloane) cu simbolurile finale.
        """
        coloane = [rola.get_simboluri_vizibile() for rola in self.lista_role]
        matrice_randuri = [list(rand) for rand in zip(*coloane)]
        return matrice_randuri

    def verificare_castiguri_linii(self, matrice_randuri):
        """ Verifică toate liniile de plată și returnează câștigul total. """
        castig_total_spin = 0
        
        for nume_linie, linie in s.LINII_PLATA.items():
            simboluri_pe_linie = []
            
            for id_coloana, index_rand in enumerate(linie):
                simbol = matrice_randuri[index_rand][id_coloana]
                simboluri_pe_linie.append(simbol)
            
            castig_linie = self.calculeaza_castig_linie(simboluri_pe_linie)
            castig_total_spin += castig_linie
            
        return castig_total_spin

    def calculeaza_castig_linie(self, simboluri):
        """
    	Calculează câștigul pentru o singură linie de 5 simboluri.
        """
        primul_simbol = simboluri[0]
        if primul_simbol == s.SCATTER:
            return 0
        
        if primul_simbol == s.WILD:
            simbol_non_wild_gasit = False
            for simbol_non_wild in simboluri[1:]:
                if simbol_non_wild != s.WILD and simbol_non_wild != s.SCATTER:
                    primul_simbol = simbol_non_wild
                    simbol_non_wild_gasit = True
                    break
            if not simbol_non_wild_gasit:
                return s.TABEL_PLATA[s.SAPTE][5] * self.miza_pe_linie

        numar_consecutive = 0
        for simbol in simboluri:
            if simbol == primul_simbol or simbol == s.WILD:
                numar_consecutive += 1
            else:
                break
        
        if numar_consecutive >= 3:
            if primul_simbol in s.TABEL_PLATA:
                plata = s.TABEL_PLATA[primul_simbol][numar_consecutive]
                return plata * self.miza_pe_linie
        
        return 0

    def verificare_scatter(self, matrice_randuri):
        """ Verifică câștigurile SCATTER oriunde pe ecran. """
        numar_scatter = 0
        for rand in matrice_randuri:
            for simbol in rand:
                if simbol == s.SCATTER:
                    numar_scatter += 1
        
        if numar_scatter in s.PLATA_SCATTER:
            plata = s.PLATA_SCATTER[numar_scatter]
            return plata * self.miza_totala
        
        return 0

    def desenare(self):
        """ Desenează totul pe ecran. """
        
        if self.fundal:
            self.ecran.blit(self.fundal, (0, 0))
        else:
            self.ecran.fill((20, 20, 20))
        
        for rola in self.lista_role:
            rola.desenare(self.ecran)
            
        self.interfata.desenare(
            balanta=self.balanta, 
            miza_pe_linie=self.miza_pe_linie, 
            numar_linii=self.numar_linii_plata, 
            ultimul_castig=self.ultimul_castig_din_spin
        )
        
        pygame.display.flip()

# --- Punctul de Start al Programului ---
if __name__ == "__main__":
    joc = Joc()
    joc.run()