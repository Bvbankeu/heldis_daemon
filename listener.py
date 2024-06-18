#!/usr/bin/python3
import socket
import threading
import requests

# Fonction pour appeler une API avec les données reçues
def identify_type(data):
    type_code = data[2:4]
    if type_code == '01':
        return 'http://localhost:8000/translate/login/'
    elif type_code == '10':
        return 'http://localhost:8000/translate/onlineGPS/'
    
def get_imei(data):
    type_code = data[2:4]
    if type_code == '01':
        return data[4:20]
    else:
        return '6549873216543214'

class GpsInstance:
    def __init__(self, instance_id):
        self.id = str(instance_id)
        self.status = '07135523080364'

    def get_imei(self, data):
        type_code = data[2:4]
        if type_code == '01':
            return data[4:20]

    def get_status(self, data):
        return data[4:20]

    def identify_type(self, data):
        type_code = data[2:4]
        if type_code == '01':
            return 'http://localhost:8000/translate/login/'
        elif type_code == '10':
            return 'http://localhost:8000/translate/onlineGPS/'
        elif type_code == '13':
            return 'http://localhost:8000/translate/status/'
        elif type_code == '11':
            return 'http://localhost:8000/translate/offlineGPS/'
        elif type_code == '17':
            return 'http://localhost:8000/translate/offlineWifi/'
        elif type_code == '69':
            return 'http://localhost:8000/translate/wifiPositioning/'
        elif type_code == '30':
            return 'http://localhost:8000/translate/updateTime/'
        elif type_code == '57':
            return 'http://localhost:8000/translate/setParams/'
        else:
            return 'http://localhost:8000/translate/reste/'   
        
    def process(self, data):
        try:
            
            if data[2:4] == '01':
                self.id = self.get_imei(data)

            # URL de l'API Django pour le décodage du message
            api_url = self.identify_type(data)

            # Paramètres de la requête GET
            params = {'hex_message': data, 'imei': self.id}

            # Envoi de la requête GET à l'API avec le message hexadécimal
            response = requests.get(api_url, params=params)
            print(api_url)
            print(params)
            # Vérification du code de statut de la réponse
            if response.status_code == 200:
                json_response = response.json()
                # Accès à la valeur associée à la clé 'login_response'
                resplogin = json_response.get('response', '')
                # Affichage de la réponse de l'API
                print("Réponse de l'API:", resplogin)
                return resplogin
            else:
                print("Erreur lors de l'envoi du message hexadécimal à l'API. Code de statut:", response.status_code)
                print(response.json())
        except Exception as e:
            print("Une erreur s'est produite lors de la communication avec l'API:", str(e))
        return '787801440D0A'
    

def process(data):
    try:
        # URL de l'API Django pour le décodage du message
        api_url = identify_type(data)

        # Paramètres de la requête GET
        params = {'hex_message': data, 'imei':get_imei(data)}

        # Envoi de la requête GET à l'API avec le message hexadécimal
        response = requests.get(api_url, params=params)

        # Vérification du code de statut de la réponse
        if response.status_code == 200:
            json_response = response.json()
            # Accès à la valeur associée à la clé 'login_response'
            resplogin = json_response.get('login_response', '')
            # Affichage de la réponse de l'API
            print("Réponse de l'API:", resplogin)
            return resplogin
        else:
            print("Erreur lors de l'envoi du message hexadécimal à l'API. Code de statut:", response.status_code)
            print(response.json)
    except Exception as e:
        print("Une erreur s'est produite lors de la communication avec l'API:", str(e))
    return '7878 01 44 0D0A'


def handle_client(client_socket, addr):
    try:
        client_socket.settimeout(310)
        gps_connected = GpsInstance('0123456789012345')
        while True:
            # receive and print client messages
            request = client_socket.recv(1024)
            #if not request:
             #   print("Aucune donnée reçue du client.")
              #  break
            if request.lower() == "close":
                client_socket.send("closed".encode("utf-8"))
                break
            print(f"Received: {request}")
            #convertir hex to string
            request_hex = request.hex()
            payload = request_hex[4:len(request_hex)-4]
            # convert and send accept response to the client
            print(payload)
            
            client_socket.sendall(bytes.fromhex(gps_connected.process(payload)))  # Envoyer la réponse au client
            #response = "accepted"
            #client_socket.send(response.encode("utf-8"))
    except socket.timeout:
        # Si aucun message n'est reçu après 310 secondes
        print("Aucune donnée reçue du client après 310 secondes.")
    except Exception as e:
        print(f"Error when hanlding client: {e}")
    finally:
        #client_socket.close()
        requests.get('http://localhost:8000/translate/offStatus/', params = {'imei': gps_connected.id})
        print(f"Connection to client ({addr[0]}:{addr[1]}) closed")



def run_server():
    server_ip = "0.0.0.0"  # server hostname or IP address
    port = 7086  # server port number
    # create a socket object
    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # bind the socket to the host and port
        server.bind((server_ip, port))
        # listen for incoming connections
        server.listen()
        print(f"Listening on {server_ip}:{port}")

        while True:
            # accept a client connection
            client_socket, addr = server.accept()
            print(f"Accepted connection from {addr[0]}:{addr[1]}")
            # start a new thread to handle the client
            thread = threading.Thread(target=handle_client, args=(client_socket, addr,))
            thread.start()
    except Exception as e:
        print(f"Error: {e}")
    finally:
        server.close()


run_server()