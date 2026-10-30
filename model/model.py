import networkx as nx
from itertools import combinations
from database.DAO import DAO


class Model:
    def __init__(self):
        self._grafo = nx.Graph()
        self._idMap = {}
        self._nomiArtisti = {}
        # punto 2
        self._cicloBest = []
        self._pesoBest = -1
        self._partenza = None
        self._L = 0

    # ==================== PUNTO 1 ====================

    def getGeneri(self):
        return DAO.getGeneri()

    def buildGraph(self, genere, soglia):
        self._grafo.clear()
        self._idMap = {}

        # nodi: paesi con almeno un brano del genere venduto
        nodi = DAO.getNodi(genere)
        self._idMap = {p.nome: p for p in nodi}
        self._grafo.add_nodes_from(nodi)

        # set dei clienti di ogni paese
        for paese, idC in DAO.getCoppieClienti(genere):
            if paese in self._idMap:
                self._idMap[paese].clienti.add(idC)

        # set degli artisti di ogni paese
        for paese, idA in DAO.getCoppieArtisti(genere):
            if paese in self._idMap:
                self._idMap[paese].artisti.add(idA)

        # archi: almeno 'soglia' artisti in comune
        for p1, p2 in combinations(nodi, 2):
            comuni = p1.artisti & p2.artisti
            if len(comuni) >= soglia:
                self._grafo.add_edge(p1, p2, weight=len(comuni))

    def getNumNodi(self):
        return self._grafo.number_of_nodes()

    def getNumArchi(self):
        return self._grafo.number_of_edges()

    def getNodiOrdinati(self):
        return sorted(self._grafo.nodes, key=lambda p: p.nome)

    def getPaese(self, nome):
        return self._idMap.get(nome)

    # a) paese con ricavo maggiore
    def getRicavoMaggiore(self):
        best = max(self._grafo.nodes, key=lambda p: p.ricavo)
        return best, best.ricavo

    # b) paesi con più clienti
    def getPiuClienti(self):
        maxClienti = max(len(p.clienti) for p in self._grafo.nodes)
        migliori = [p for p in self._grafo.nodes if len(p.clienti) == maxClienti]
        migliori.sort(key=lambda p: p.nome)
        return migliori, maxClienti

    # c) paesi con più artisti diversi
    def getPiuArtisti(self):
        maxArtisti = max(len(p.artisti) for p in self._grafo.nodes)
        migliori = [p for p in self._grafo.nodes if len(p.artisti) == maxArtisti]
        migliori.sort(key=lambda p: p.nome)
        return migliori, maxArtisti

    # d) paesi con grado maggiore
    def getGradoMaggiore(self):
        maxGrado = max(self._grafo.degree(p) for p in self._grafo.nodes)
        migliori = [p for p in self._grafo.nodes if self._grafo.degree(p) == maxGrado]
        migliori.sort(key=lambda p: p.nome)
        return migliori, maxGrado

    # e) 5 archi di peso maggiore
    def getTop5Archi(self):
        archi = []
        for u, v, dati in self._grafo.edges(data=True):
            nomi = sorted([u.nome, v.nome])
            archi.append((nomi[0], nomi[1], dati["weight"]))
        archi.sort(key=lambda x: (-x[2], x[0], x[1]))
        return archi[:5]

    # f) componenti connesse
    def getInfoComponenti(self):
        componenti = list(nx.connected_components(self._grafo))
        piuGrande = max(componenti, key=len)
        isolati = 0
        for comp in componenti:
            if len(comp) == 1:
                isolati += 1
        return len(componenti), len(piuGrande), isolati

    # g) paesi con ricavo medio per cliente maggiore
    def getRicavoMedio(self):
        medie = {}
        for p in self._grafo.nodes:
            medie[p] = round(p.ricavo / len(p.clienti), 2)
        maxMedia = max(medie.values())
        migliori = [p for p in medie if medie[p] == maxMedia]
        migliori.sort(key=lambda p: p.nome)
        return migliori, maxMedia

    # h) artisti acquistati nel maggior numero di paesi
    def getArtistaPiuPaesi(self):
        conta = {}
        for p in self._grafo.nodes:
            for a in p.artisti:
                conta[a] = conta.get(a, 0) + 1
        maxPaesi = max(conta.values())
        if len(self._nomiArtisti) == 0:
            self._nomiArtisti = DAO.getArtisti()      # {ArtistId: nome}
        migliori = [self._nomiArtisti[a] for a in conta if conta[a] == maxPaesi]
        migliori.sort()
        return migliori, maxPaesi

    # ==================== PUNTO 2 ====================

    def getTour(self, partenza, L):
        self._cicloBest = []
        self._pesoBest = -1
        self._partenza = partenza
        self._L = L
        self._ricorsione([partenza], 0)
        return self._cicloBest, self._pesoBest

    def _ricorsione(self, parziale, pesoParziale):
        ultimo = parziale[-1]

        # caso terminale: ho L paesi, devo poter tornare alla partenza
        if len(parziale) == self._L:
            if self._grafo.has_edge(ultimo, self._partenza):
                # stesso ciclo nei due versi: tengo solo quello con secondo < penultimo
                if parziale[1].nome < parziale[-1].nome:
                    peso = pesoParziale + self._grafo[ultimo][self._partenza]["weight"]
                    if peso > self._pesoBest:
                        self._pesoBest = peso
                        self._cicloBest = list(parziale)
            return

        # aggiungo un vicino non ancora visitato
        for vicino in self._grafo.neighbors(ultimo):
            if vicino in parziale:
                continue
            peso = self._grafo[ultimo][vicino]["weight"]
            parziale.append(vicino)
            self._ricorsione(parziale, pesoParziale + peso)
            parziale.pop()

    def getPesoArco(self, p1, p2):
        return self._grafo[p1][p2]["weight"]