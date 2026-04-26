import socket

ADRESA_SERVER = "0.0.0.0"
PORT = 9999

clienti_conectati = {}
mesaje_publicate = {}
id_mesaj_curent = 1

server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind((ADRESA_SERVER, PORT))

print(f"[SERVER] Serverul UDP a pornit si asculta pe {ADRESA_SERVER}:{PORT}...")

while True:
    try:
        mesaj_brut, adresa_client = server_socket.recvfrom(1024)
        mesaj_text = mesaj_brut.decode('utf-8').strip()

        parti = mesaj_text.split(" ", 1)
        comanda = parti[0].upper()
        
        print(f"[SERVER] Mesaj primit de la {adresa_client}: {mesaj_text}")

        if comanda in ["PUBLISH", "DELETE", "LIST"]:
            if adresa_client not in clienti_conectati:
                raspuns = "EROARE: Nu esti conectat. Foloseste CONNECT mai intai."
                server_socket.sendto(raspuns.encode('utf-8'), adresa_client)
                continue
        
        if comanda == "CONNECT":
            if adresa_client in clienti_conectati:
                raspuns = "EROARE: Esti deja conectat."
            else:
                clienti_conectati[adresa_client] = True
                raspuns = "OK: Te-ai conectat cu succes."
                print(f"[SERVER] Numar clienti activi: {len(clienti_conectati)}")
            server_socket.sendto(raspuns.encode('utf-8'), adresa_client)

        elif comanda == "DISCONNECT":
            if adresa_client not in clienti_conectati:
                raspuns = "EROARE: Nu esti inregistrat / Nu te-ai conectat."
            else:
                del clienti_conectati[adresa_client]
                raspuns = "OK: Te-ai deconectat."
                print(f"[SERVER] Numar clienti activi: {len(clienti_conectati)}")
            server_socket.sendto(raspuns.encode('utf-8'), adresa_client)

        elif comanda == "PUBLISH":
            if len(parti) < 2 or parti[1].strip() == "":
                raspuns = "EROARE: Mesajul nu poate fi gol."
            else:
                text_mesaj = parti[1].strip()
                mesaje_publicate[id_mesaj_curent] = {"text": text_mesaj, "autor": adresa_client}
                raspuns = f"OK: Mesaj publicat cu ID={id_mesaj_curent}"
                id_mesaj_curent += 1
            server_socket.sendto(raspuns.encode('utf-8'), adresa_client)

        elif comanda == "DELETE":
            try:
                id_sters = int(parti[1].strip())
                if id_sters not in mesaje_publicate:
                    raspuns = f"EROARE: Nu exista un mesaj cu ID={id_sters}."
                elif mesaje_publicate[id_sters]["autor"] != adresa_client:
                    raspuns = "EROARE: Nu poti sterge un mesaj pe care nu tu l-ai publicat."
                else:
                    del mesaje_publicate[id_sters]
                    raspuns = f"OK: Mesajul cu ID={id_sters} a fost sters."
            except (IndexError, ValueError):
                raspuns = "EROARE: Format invalid. Foloseste DELETE <id_numeric>."
            server_socket.sendto(raspuns.encode('utf-8'), adresa_client)

        elif comanda == "LIST":
            if not mesaje_publicate:
                raspuns = "INFO: Nu exista mesaje publicate in acest moment."
            else:
                raspuns = "--- LISTA MESAJE ---\n"
                for m_id, m_data in mesaje_publicate.items():
                    raspuns += f"[{m_id}] {m_data['text']}\n"
                raspuns += "--------------------"
            server_socket.sendto(raspuns.encode('utf-8'), adresa_client)

        else:
            raspuns = "EROARE: Comanda necunoscuta."
            server_socket.sendto(raspuns.encode('utf-8'), adresa_client)

    except Exception as e:
        print(f"[SERVER] Eroare de procesare: {e}")