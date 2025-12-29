# -*- coding: utf-8 -*-
import pygame
import random
import setari as s

class Simbol(pygame.sprite.Sprite):
    """
    Reprezinta un singur pătrat grafic de pe ecran.
    Acum, ea doar ține minte imaginea și poziția.
    Logica de scalare și creare se mută în clasa Rola.
    """
    def __init__(self, nume_simbol, pozitie, marime, imagine_scalata):
        super().__init__()
        self.nume = nume_simbol
        self.image = imagine_scalata
        self.rect = self.image.get_rect(topleft = pozitie)

class Rola:
    
    def __init__(self, id_rola, pozitie_x):
        self.id_rola = id_rola
        self.pozitie_x = pozitie_x
        
        # Stocăm dimensiunile
        self.marime_celula = s.DIMENSIUNE_CELULA
        self.marime_simbol_grafica = s.DIMENSIUNE_CELULA - (s.MARGINE_SIMBOL * 2)
        self.padding_x = s.MARGINE_SIMBOL
        self.padding_y = s.MARGINE_SIMBOL
        
        # Benzile virtuale
        self.banda_virtuala = s.BENZI_ROLE[id_rola]
        self.lungime_banda = len(self.banda_virtuala)
        
        # Starea rolei
        self.stare = 'IDLE' # Stări: 'IDLE', 'SPINNING', 'STOPPING'
        self.index_stop_final = 0
        
        # Grup de sprite-uri
        self.grup_simboluri = pygame.sprite.Group()
        
        # Stocăm imaginile gata scalate (optimizare)
        self.imagini_preincarcate = self.preincarca_imagini()
        
        # Inițializăm rola cu 4 simboluri (unul extra sus, pentru wrapping)
        self.genereaza_simboluri_initiale()

    def preincarca_imagini(self):
        """ Încarcă și scalează toate imaginile o singură dată (optimizare). """
        imagini = {}
        dimensiune = (self.marime_simbol_grafica, self.marime_simbol_grafica)
        for nume_simbol, cale_fisier in s.MAPARE_GRAFICA.items():
            try:
                img = pygame.image.load(cale_fisier).convert_alpha()
                imagini[nume_simbol] = pygame.transform.scale(img, dimensiune)
            except FileNotFoundError:
                print(f"EROARE la preîncărcare: Nu am găsit {cale_fisier}")
                img_rosie = pygame.Surface(dimensiune)
                img_rosie.fill('red')
                imagini[nume_simbol] = img_rosie
        return imagini

    def genereaza_simboluri_initiale(self):
        """ Creează un set inițial de 4 simboluri. """
        self.grup_simboluri.empty()
        index_curent = random.randint(0, self.lungime_banda - 1)
        
        # Calculăm poziția Y a grilei (centrată)
        inaltime_totala_grila = self.marime_celula * 3
        y_start_grila = (s.INALTIME - inaltime_totala_grila) / 2
        
        # Creăm 4 simboluri: unul deasupra, și cele 3 vizibile
        for i in range(-1, 3): # i va fi -1, 0, 1, 2
            index_banda = (index_curent + i) % self.lungime_banda
            nume_simbol = self.banda_virtuala[index_banda]
            
            # Calculăm poziția X și Y a SIMBOLULUI (cu padding)
            x = self.pozitie_x + self.padding_x
            y = y_start_grila + (i * self.marime_celula) + self.padding_y
            
            simbol = Simbol(nume_simbol, (x, y), self.marime_simbol_grafica, self.imagini_preincarcate[nume_simbol])
            self.grup_simboluri.add(simbol)

    def start_spin(self, durata_ms):
        """ Pornește rotirea și alege un index final. """
        self.stare = 'SPINNING'
        self.durata_spin = durata_ms
        self.timp_start_spin = pygame.time.get_ticks()
        self.index_stop_final = random.randint(0, self.lungime_banda - 1)

    def update(self, delta_time):
        """ Actualizează starea rolei (SPINNING sau STOPPING). """
        if self.stare == 'SPINNING':
            self.anima_rotire(delta_time)
            
            # Verificăm dacă a expirat timpul
            timp_curent = pygame.time.get_ticks()
            if timp_curent - self.timp_start_spin >= self.durata_spin:
                self.stare = 'STOPPING' # Trecem la starea de oprire
                
        elif self.stare == 'STOPPING':
            self.anima_oprire()

    def anima_rotire(self, delta_time):
        """ Mișcă fluid simbolurile în jos și le "teleportează". """
        y_delta = s.VITEZA_SPIN * delta_time # Calculăm cât să mișcăm (bazat pe timp)
        
        inaltime_totala_grila = self.marime_celula * 3
        y_start_grila = (s.INALTIME - inaltime_totala_grila) / 2
        y_jos_limita = y_start_grila + inaltime_totala_grila # Limita de jos
        
        simboluri = self.grup_simboluri.sprites()
        for simbol in simboluri:
            simbol.rect.y += y_delta
            
            # Verificăm dacă simbolul a ieșit complet pe jos
            if simbol.rect.top > y_jos_limita:
                # Îl "teleportăm" sus
                # Găsim simbolul cel mai de sus pentru a ne alinia corect
                y_cel_mai_sus = min(s.rect.y for s in simboluri)
                simbol.rect.y = y_cel_mai_sus - self.marime_celula
                
                # Îi dăm un nume și o imagine nouă, aleatorie
                nume_simbol_nou = random.choice(self.banda_virtuala)
                simbol.nume = nume_simbol_nou
                simbol.image = self.imagini_preincarcate[nume_simbol_nou]

    def anima_oprire(self):
        """ Oprește fluid rola, aliniind-o la indexul final. """
        
        # Calculăm pozițiile Y țintă ale celulelor
        inaltime_totala_grila = self.marime_celula * 3
        y_start_grila = (s.INALTIME - inaltime_totala_grila) / 2
        
        y_tinta_sus = y_start_grila
        y_tinta_mijloc = y_start_grila + self.marime_celula
        y_tinta_jos = y_start_grila + self.marime_celula * 2
        
        # Re-populăm grupul cu simbolurile FINALE
        # (Acest lucru se întâmplă o singură dată la începutul stării STOPPING)
        if not hasattr(self, 'simbol_mijloc_final'):
            self.grup_simboluri.empty()
            
            # Creăm simbolul de sus
            nume_sus = self.banda_virtuala[(self.index_stop_final - 1) % self.lungime_banda]
            x_sus = self.pozitie_x + self.padding_x
            y_sus = y_tinta_sus + self.padding_y - self.marime_celula # Îl punem cu o celulă mai sus
            simbol_sus = Simbol(nume_sus, (x_sus, y_sus), self.marime_simbol_grafica, self.imagini_preincarcate[nume_sus])

            # Creăm simbolul din mijloc
            nume_mijloc = self.banda_virtuala[self.index_stop_final]
            x_mijloc = self.pozitie_x + self.padding_x
            y_mijloc = y_tinta_mijloc + self.padding_y - self.marime_celula # Îl punem cu o celulă mai sus
            self.simbol_mijloc_final = Simbol(nume_mijloc, (x_mijloc, y_mijloc), self.marime_simbol_grafica, self.imagini_preincarcate[nume_mijloc])

            # Creăm simbolul de jos
            nume_jos = self.banda_virtuala[(self.index_stop_final + 1) % self.lungime_banda]
            x_jos = self.pozitie_x + self.padding_x
            y_jos = y_tinta_jos + self.padding_y - self.marime_celula # Îl punem cu o celulă mai sus
            simbol_jos = Simbol(nume_jos, (x_jos, y_jos), self.marime_simbol_grafica, self.imagini_preincarcate[nume_jos])
            
            self.grup_simboluri.add(simbol_sus, self.simbol_mijloc_final, simbol_jos)

        # Calculăm poziția Y țintă a simbolului din mijloc
        y_tinta_finala = y_tinta_mijloc + self.padding_y
        distanta = y_tinta_finala - self.simbol_mijloc_final.rect.y
        
        # Verificăm dacă am ajuns (cu o marjă de eroare de 1 pixel)
        if abs(distanta) < 1:
            # Am ajuns! Fixăm poziția exactă (pentru orice eroare de rotunjire)
            offset_final = y_tinta_finala - self.simbol_mijloc_final.rect.y
            for simbol in self.grup_simboluri:
                simbol.rect.y += offset_final
                
            self.stare = 'IDLE' # Am terminat de oprit
            del self.simbol_mijloc_final # Ștergem atributul temporar
        else:
            # Nu am ajuns încă. Ne mișcăm cu o fracțiune din distanță (easing)
            miscare = distanta * s.VITEZA_OPRIRE
            # Ne asigurăm că ne mișcăm cu cel puțin 1 pixel, altfel s-ar putea bloca
            if miscare > 0: miscare = max(miscare, 1)
            if miscare < 0: miscare = min(miscare, -1)
                
            for simbol in self.grup_simboluri:
                simbol.rect.y += miscare

    def get_simboluri_vizibile(self):
        """ Returnează numele celor 3 simboluri vizibile de la indexul final. """
        index_sus = (self.index_stop_final - 1) % self.lungime_banda
        index_mijloc = self.index_stop_final % self.lungime_banda
        index_jos = (self.index_stop_final + 1) % self.lungime_banda
        
        return [
            self.banda_virtuala[index_sus],
            self.banda_virtuala[index_mijloc],
            self.banda_virtuala[index_jos]
        ]

    def desenare(self, ecran):
        """ Desenează cele 3 (sau 4 în timpul tranziției) simboluri pe ecran. """
        self.grup_simboluri.draw(ecran)