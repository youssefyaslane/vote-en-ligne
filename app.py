from flask import Flask, render_template, request
import sqlite3
from cryptography.fernet import Fernet
import socket











app = Flask(__name__)

# Chemin vers la base de données SQLite
DATABASE = r'C:\Users\user\Desktop\Project_vote\Votedatabase.db'


# # Générer une nouvelle clé Fernet
# def generate_key():
#     return Fernet.generate_key()

# key = generate_key()
# print("Clé de chiffrement Fernet: ", key.decode())

key = "p64qxpOeMlOxyLzvmX8qq8vomvXVJTvNgZQCqsZtQDM="
cipher_suite = Fernet(key)

def execute_query(query, params=()):
    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()
    cursor.execute(query, params)
    connection.commit()
    connection.close()

SERVER1_IP = '127.0.0.1'
SERVER1_PORT = 12345


SERVER2_IP = '127.0.0.1'
SERVER2_PORT = 12346

def cin_exists(cin):
    DATABASE = r'C:\Users\user\Desktop\Project_vote\Votedatabase.db'
    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM Votes WHERE cin = ?", (cin,))
    user = cursor.fetchone()
    connection.close()
    return user is not None


@app.route('/')
def index():
    return render_template('vote.html')

@app.route('/submit_vote', methods=['POST'])
def submit_vote():
    if request.method == 'POST':
        cin = request.form['cin']
        vote = request.form['vote']

        if cin_exists(cin):
            return "Le CIN existe déjà dans la base de données."
        
        # Chiffrer les données
        cin_encrypted = cipher_suite.encrypt(cin.encode())
        vote_encrypted = cipher_suite.encrypt(vote.encode())
        print(cin,vote)
        # Créer un message avec les données chiffrées
        message = f"{cin_encrypted}.{vote_encrypted}"
        
        # Envoyer le message aux deux serveurs via des sockets
        try:
            # Envoi au premier serveur
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s1:
                s1.connect((SERVER1_IP, SERVER1_PORT))
                s1.sendall(message.encode())
            
            # Envoi au deuxième serveur
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s2:
                s2.connect((SERVER2_IP, SERVER2_PORT))
                s2.sendall(message.encode())
            
            return "Vote soumis avec succès !"
        
        except Exception as e:
            print("Erreur lors de l'envoi du message :", e)
            return "Une erreur s'est produite lors de l'envoi du vote."
        
        
if __name__ == '__main__':
    app.run(debug=True)
