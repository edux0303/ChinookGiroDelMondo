import flet as ft


class Controller:
    def __init__(self, view, model):
        # the view, with the graphical elements of the UI
        self._view = view
        # the model, which implements the logic of the program and holds the data
        self._model = model

    # ---------- PUNTO 1 ----------

    def fillDDGeneri(self):
        self._view._ddGenere.options.clear()
        for idG, nome in self._model.getGeneri():
            self._view._ddGenere.options.append(ft.dropdown.Option(key=str(idG), text=nome))
        self._view.update_page()

    def handleCreaGrafo(self, e):
        self._view._txt_result.controls.clear()

        # 1. genere
        if self._view._ddGenere.value is None:
            self._errore("Seleziona un genere!")
            return
        idGenere = int(self._view._ddGenere.value)

        # 2. soglia S
        try:
            soglia = int(self._view._txtInS.value)
        except (ValueError, TypeError):
            self._errore("S deve essere un numero intero!")
            return
        if soglia < 1:
            self._errore("S deve essere almeno 1!")
            return

        # 3. costruisco il grafo
        self._model.buildGraph(idGenere, soglia)

        if self._model.getNumNodi() == 0:
            self._errore("Nessun paese ha acquistato brani di questo genere.")
            return

        # 4. stampo
        self._view._txt_result.controls.append(ft.Text("Grafo creato correttamente!", color="green"))
        self._view._txt_result.controls.append(ft.Text(f"Numero di nodi: {self._model.getNumNodi()}"))
        self._view._txt_result.controls.append(ft.Text(f"Numero di archi: {self._model.getNumArchi()}"))

        # 5. dropdown paesi
        self.fillDDPaesi()

        self._view.update_page()

    def fillDDPaesi(self):
        self._view._ddPaese.options.clear()
        self._view._ddPaese.value = None
        for p in self._model.getNodiOrdinati():
            self._view._ddPaese.options.append(ft.dropdown.Option(key=p.nome, text=p.nome))

    def handleStampaInfo(self, e):
        self._view._txt_result.controls.clear()

        if self._model.getNumNodi() == 0:
            self._errore("Crea prima il grafo!")
            return

        res = self._view._txt_result.controls

        # a) ricavo maggiore
        paese, ricavo = self._model.getRicavoMaggiore()
        res.append(ft.Text(f"a) Paese con ricavo maggiore: {paese} ({ricavo:.2f} $)"))

        # b) più clienti
        lista, n = self._model.getPiuClienti()
        res.append(ft.Text(f"b) Paese con più clienti ({n}): {', '.join(str(p) for p in lista)}"))

        # c) più artisti
        lista, n = self._model.getPiuArtisti()
        res.append(ft.Text(f"c) Paese con più artisti diversi ({n}): {', '.join(str(p) for p in lista)}"))

        # d) grado maggiore
        lista, grado = self._model.getGradoMaggiore()
        res.append(ft.Text(f"d) Paese con grado maggiore ({grado}): {', '.join(str(p) for p in lista)}"))

        # e) top 5 archi
        res.append(ft.Text("e) I 5 archi di peso maggiore:"))
        for p1, p2, peso in self._model.getTop5Archi():
            res.append(ft.Text(f"     {p1} – {p2}: {peso}"))

        # f) componenti
        nComp, dimMax, isolati = self._model.getInfoComponenti()
        res.append(ft.Text(f"f) Componenti connesse: {nComp}"))
        res.append(ft.Text(f"     Dimensione della più grande: {dimMax}"))
        res.append(ft.Text(f"     Paesi isolati: {isolati}"))

        # g) ricavo medio per cliente
        lista, media = self._model.getRicavoMedio()
        res.append(ft.Text(f"g) Ricavo medio per cliente maggiore ({media:.2f} $): "
                           f"{', '.join(str(p) for p in lista)}"))

        # h) artista in più paesi
        lista, nPaesi = self._model.getArtistaPiuPaesi()
        res.append(ft.Text(f"h) Artista acquistato in più paesi ({nPaesi}): {', '.join(lista)}"))

        self._view.update_page()

    # ---------- PUNTO 2 ----------

    def handleTour(self, e):
        self._view._txt_result.controls.clear()

        # 1. grafo creato?
        if self._model.getNumNodi() == 0:
            self._errore("Crea prima il grafo!")
            return

        # 2. paese di partenza
        if self._view._ddPaese.value is None:
            self._errore("Seleziona un paese di partenza!")
            return
        partenza = self._model.getPaese(self._view._ddPaese.value)
        if partenza is None:
            self._errore("Paese non presente nel grafo!")
            return

        # 3. L
        try:
            L = int(self._view._txtInL.value)
        except (ValueError, TypeError):
            self._errore("L deve essere un numero intero!")
            return
        if L < 3 or L > 6:
            self._errore("L deve essere compreso tra 3 e 6!")
            return

        # 4. ricorsione
        ciclo, peso = self._model.getTour(partenza, L)

        if len(ciclo) == 0:
            self._errore(f"Nessun tour di {L} paesi a partire da {partenza}.")
            return

        # 5. stampo il ciclo con i pesi
        self._view._txt_result.controls.append(
            ft.Text(f"Tour di {L} paesi a partire da {partenza}:", color="green"))
        for i in range(len(ciclo)):
            p1 = ciclo[i]
            p2 = ciclo[(i + 1) % len(ciclo)]        # dopo l'ultimo torno al primo
            self._view._txt_result.controls.append(
                ft.Text(f"     {p1} → {p2} (peso {self._model.getPesoArco(p1, p2)})"))
        self._view._txt_result.controls.append(ft.Text(f"Peso totale: {peso}"))

        self._view.update_page()

    # ---------- UTILITY ----------

    def _errore(self, messaggio):
        self._view._txt_result.controls.append(ft.Text(messaggio, color="red"))
        self._view.update_page()