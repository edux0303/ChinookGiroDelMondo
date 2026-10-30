from database.DB_connect import DBConnect
from model.country import Country


""""
PUNTO 1
1. All’avvio, riempire un menu a tendina con tutti i generi.
2. L’utente sceglie un genere G e inserisce in un campo di testo un intero S ≥ 1. Premendo “Crea Grafo”, l’applicazione costruisce un grafo semplice, non orientato e pesato: a) i nodi sono i paesi (campo Country dei clienti) in cui è stato venduto almeno un brano del genere G. Per ogni paese si memorizzino, considerando solo i brani del genere G:
    * il ricavo totale;
    * l’insieme dei clienti che li hanno acquistati;
    * l’insieme degli artisti acquistati; b) due paesi sono collegati da un arco se hanno almeno S artisti in comune; c) il peso dell’arco è il numero di artisti in comune.
3. Stampare il numero di nodi e di archi. Riempire poi un menu a tendina con i paesi del grafo, in ordine alfabetico.
4. Premendo “Stampa Info”, stampare: a) il paese con il ricavo maggiore e il ricavo; b) il paese (o i paesi, se a pari merito) con più clienti e il numero; c) il paese (o i paesi) con più artisti diversi e il numero; d) il paese (o i paesi) con grado maggiore e il grado; e) i 5 archi di peso maggiore, in ordine decrescente di peso. A parità si ordina alfabeticamente per il primo paese e poi per il secondo; f) il numero di componenti connesse, la dimensione della più grande e il numero di paesi isolati; g) il paese (o i paesi) con il ricavo medio per cliente maggiore, cioè ricavo diviso numero di clienti, con due decimali; h) l’artista (o gli artisti) acquistato nel maggior numero di paesi del grafo, e il numero di paesi.
PUNTO 2
Si vuole organizzare un tour che parte da un paese, ne visita altri e ritorna al paese di partenza. L’utente sceglie un paese P e inserisce un intero L, con 3 ≤ L ≤ 6. Con un algoritmo ricorsivo, trovare un ciclo che:
1. parte da P e ritorna in P;
2. visita esattamente L paesi diversi (P compreso), quindi usa L archi;
3. ogni coppia di paesi consecutivi, compresa la coppia ultimo paese → P, deve essere collegata da un arco del grafo;
4. massimizza la somma dei pesi degli archi.


"""

class DAO():

    @staticmethod
    def getGeneri():
        conn = DBConnect.get_connection()
        if conn is None:
            return []

        results = []

        cursor = conn.cursor(dictionary=True)
        query = """
                SELECT g.GenreId, g.Name
                FROM Genre g
                ORDER BY g.Name
                """

        cursor.execute(query)

        for row in cursor:
            results.append((row["GenreId"], row["Name"]))

        cursor.close()
        conn.close()
        return results

    @staticmethod
    def getNodi(genere):
        conn = DBConnect.get_connection()
        if conn is None:
            return []

        results = []

        cursor = conn.cursor(dictionary=True)
        query = """
                SELECT c.Country AS paese, SUM(il.UnitPrice * il.Quantity) AS ricavo
                FROM Customer c, Invoice i, InvoiceLine il, Track t
                WHERE c.CustomerId = i.CustomerId AND i.InvoiceId = il.InvoiceId
                AND il.TrackId = t.TrackId
                AND t.GenreId = %s
                GROUP BY c.Country
                ORDER BY c.Country
                """

        cursor.execute(query, (genere,))

        for row in cursor:
            results.append(Country(row["paese"], float(row["ricavo"])))

        cursor.close()
        conn.close()
        return results

    @staticmethod
    def getCoppieClienti(genere):
        conn = DBConnect.get_connection()
        if conn is None:
            return []

        results = []

        cursor = conn.cursor(dictionary=True)
        query = """
                SELECT DISTINCT c.Country AS paese, c.CustomerId AS idC
                FROM Customer c, Invoice i, InvoiceLine il, Track t
                WHERE c.CustomerId = i.CustomerId AND i.InvoiceId = il.InvoiceId
                AND il.TrackId = t.TrackId
                AND t.GenreId = %s
                """

        cursor.execute(query, (genere,))

        for row in cursor:
            results.append((row["paese"], row["idC"]))

        cursor.close()
        conn.close()
        return results

    @staticmethod
    def getCoppieArtisti(genere):
        conn = DBConnect.get_connection()
        if conn is None:
            return []

        results = []

        cursor = conn.cursor(dictionary=True)
        query = """
                SELECT DISTINCT c.Country AS paese, al.ArtistId AS idA
                FROM Customer c, Invoice i, InvoiceLine il, Track t, Album al
                WHERE c.CustomerId = i.CustomerId AND i.InvoiceId = il.InvoiceId
                AND il.TrackId = t.TrackId AND t.AlbumId = al.AlbumId
                AND t.GenreId = %s
                """

        cursor.execute(query, (genere,))

        for row in cursor:
            results.append((row["paese"], row["idA"]))

        cursor.close()
        conn.close()
        return results

    @staticmethod
    def getArtisti():
        conn = DBConnect.get_connection()
        if conn is None:
            return {}

        results = {}

        cursor = conn.cursor(dictionary=True)
        query = """
                SELECT ar.ArtistId, ar.Name
                FROM Artist ar
                """

        cursor.execute(query)

        for row in cursor:
            results[row["ArtistId"]] = row["Name"]

        cursor.close()
        conn.close()
        return results
