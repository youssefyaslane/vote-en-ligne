import socket
from cryptography.fernet import Fernet, InvalidToken

# Adresse IP et port sur lesquels le serveur "co" écoutera
SERVER_CO_IP = '127.0.0.1'
SERVER_CO_PORT = 12345


# Adresse IP et port du serveur "de"
SERVER_DE_IP = '127.0.0.1'
SERVER_DE_PORT = 12346


# Clé de chiffrement
key = "p64qxpOeMlOxyLzvmX8qq8vomvXVJTvNgZQCqsZtQDM="
cipher_suite = Fernet(key)

def decrypt_message(encrypted_message):
    # Extraire les données entre les apostrophes
    encrypted_segments = encrypted_message.decode().split("'")
    decrypted_segments = []
    # Déchiffrer chaque segment entre les apostrophes
    for segment in encrypted_segments:
        try:
            decrypted_segment = cipher_suite.decrypt(segment.encode())
            decrypted_segments.append(decrypted_segment)
        except InvalidToken:  # Utilisation directe de InvalidToken
            # Si le segment ne peut pas être déchiffré, continuer au prochain segment
            continue
    # Concaténer les segments déchiffrés pour reconstruire le message complet
    decrypted_message = b''.join(decrypted_segments)
    return decrypted_message.decode()

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((SERVER_CO_IP, SERVER_CO_PORT))
        s.listen()
        print(f"Le serveur 'co' écoute sur {SERVER_CO_IP}:{SERVER_CO_PORT}")

        while True:
            conn, addr = s.accept()
            with conn:
                print('Connecté par', addr)
                data = conn.recv(1024)
                if not data:
                    break
                decrypted_data = decrypt_message(data)
                print('Message reçu sur le serveur "co":', decrypted_data)
                # Envoi du message au serveur "de"
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s2:
                    s2.connect((SERVER_DE_IP, SERVER_DE_PORT))
                    s2.sendall(data)
                    print("Message envoyé au serveur 'de'")

if __name__ == "__main__":
    main()
