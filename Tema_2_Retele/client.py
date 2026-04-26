import socket
import sys

ADRESA_SERVER = "server_udp"
PORT = 9999

client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client_socket.settimeout(5.0)

este_conectat = False

def trimite_comanda(mesaj):
    """Trimite mesajul catre server si returneaza raspunsul."""
    try:
        client_socket.sendto(mesaj.encode('utf-8'), (ADRESA_SERVER, PORT))
        raspuns_brut, _ = client_socket.recvfrom(4096)
        return raspuns_brut.decode('utf-8')
    except socket.timeout:
        return "Eroare locala: Timeout. Serverul nu a raspuns in 5 secunde."
    except Exception as e:
        return f"Eroare locala: A aparut o problema la comunicare: {e}"

print("=== Client UDP Pornit ===")
print("Comenzi disponibile: CONNECT, DISCONNECT, PUBLISH <text>, DELETE <id>, LIST, EXIT")

while True:
    try:
        comanda_user = input("\nIntrodu comanda: ").strip()
        
        if not comanda_user:
            continue
            
        parti_comanda = comanda_user.split(" ", 1)
        cuvant_cheie = parti_comanda[0].upper()

        if cuvant_cheie == "EXIT":
            print("Inchidere client...")
            client_socket.close()
            sys.exit(0)

        if cuvant_cheie in ["PUBLISH", "DELETE", "LIST"]:
            if not este_conectat:
                print("Eroare locala: Trebuie sa te conectezi (CONNECT) inainte de a folosi aceasta comanda.")
                continue

        if cuvant_cheie == "PUBLISH":
            if len(parti_comanda) < 2 or parti_comanda[1].strip() == "":
                print("Eroare locala: Lipseste mesajul. Folosire: PUBLISH <text>")
                continue

        if cuvant_cheie == "DELETE":
            if len(parti_comanda) < 2 or not parti_comanda[1].strip().isdigit():
                print("Eroare locala: ID-ul trebuie sa fie un numar intreg. Folosire: DELETE <ID>")
                continue

        raspuns_server = trimite_comanda(comanda_user)
        print(f"R: {raspuns_server}")

        if cuvant_cheie == "CONNECT" and raspuns_server.startswith("OK"):
            este_conectat = True
        elif cuvant_cheie == "DISCONNECT" and raspuns_server.startswith("OK"):
            este_conectat = False

    except KeyboardInterrupt:
        print("\nInchidere fortata client...")
        client_socket.close()
        sys.exit(0)