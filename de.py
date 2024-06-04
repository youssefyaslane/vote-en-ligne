import socket
from cryptography.fernet import Fernet, InvalidToken
import sqlite3

# Adresse IP et port sur lesquels le serveur "de" écoutera
SERVER_DE_IP = '127.0.0.1'
SERVER_DE_PORT = 12346

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


messages = []

def compare_messages(messages):

    if all(x == messages[0] for x in messages):
        print("Les valeurs des messages sont égales.")
        id_and_vote = messages[0].split('candidat')
        user_id = id_and_vote[0]
        vote = 'candidat' + id_and_vote[1]
        insert_vote_to_database(user_id, vote)
    else:
        print("Les valeurs des messages ne sont pas égales.")


def insert_vote_to_database(user_id, vote):
    DATABASE = r'C:\Users\user\Desktop\Project_vote\Votedatabase.db'
    try:
        connection = sqlite3.connect(DATABASE)
        cursor = connection.cursor()
        cursor.execute("INSERT INTO Votes (cin, vote) VALUES (?, ?)", (user_id, vote))
        connection.commit()
        connection.close()
        print("Vote inséré dans la base de données avec succès!")
    except sqlite3.Error as error:
        print("Erreur lors de l'insertion du vote dans la base de données:", error)



def main():
    global messages
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((SERVER_DE_IP, SERVER_DE_PORT))
        s.listen()
        print(f"Le serveur 'de' écoute sur {SERVER_DE_IP}:{SERVER_DE_PORT}")
    
        while True:
            
            conn, addr = s.accept()
            with conn:
                
                print('Connecté par', addr)
                data = conn.recv(1024)
                if not data:
                    break
                
                decrypted_data = decrypt_message(data)
                print('Message reçu sur le serveur "de":', decrypted_data)
                messages.append(decrypted_data)
                print('Messages stockés:', messages)
                if len(messages) == 2:
                    print("Comparaison des messages...")
                    compare_messages(messages)
                    print("Réinitialisation de la liste des messages...")
                    messages = []

if __name__ == "__main__":
    main()
