import json
import os
import shutil
import keyring
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

SERVICE_NAME = "EgyptISPQuotaChecker"
ACCOUNT_USER = "LocalEncryptionKey" # The 'user' in credential manager for the key
APP_DATA_DIR = os.path.join(os.getenv('APPDATA'), SERVICE_NAME)
DATA_FILE = os.path.join(APP_DATA_DIR, "accounts.enc")

class AccountManager:
    def __init__(self):
        self._ensure_app_data()
        self.key = self._get_or_create_key()
        self.cipher = Fernet(self.key)
        self.accounts = self.load_accounts()

    def _ensure_app_data(self):
        if not os.path.exists(APP_DATA_DIR):
            try:
                os.makedirs(APP_DATA_DIR)
            except OSError as e:
                print(f"Error creating data directory: {e}")

        # Check for legacy file in current directory
        legacy_file = "accounts.enc"
        if os.path.exists(legacy_file) and not os.path.exists(DATA_FILE):
            try:
                shutil.move(legacy_file, DATA_FILE)
                print(f"Moved existing accounts file to {DATA_FILE}")
            except Exception as e:
                print(f"Failed to migrate accounts file: {e}")

    def _get_or_create_key(self):
        # Try to get key from Windows Credential Manager
        stored_key = keyring.get_password(SERVICE_NAME, ACCOUNT_USER)
        
        if stored_key:
            return base64.urlsafe_b64decode(stored_key)
        else:
            # Generate new key
            new_key = Fernet.generate_key()
            # Store in Credential Manager (base64 encoded string)
            keyring.set_password(SERVICE_NAME, ACCOUNT_USER, base64.urlsafe_b64encode(new_key).decode('utf-8'))
            return new_key

    def load_accounts(self):
        if not os.path.exists(DATA_FILE):
            return []
        
        try:
            with open(DATA_FILE, "rb") as f:
                encrypted_data = f.read()
            
            if not encrypted_data:
                return []

            decrypted_data = self.cipher.decrypt(encrypted_data)
            return json.loads(decrypted_data.decode('utf-8'))
        except Exception as e:
            print(f"Error loading accounts: {e}")
            return []

    def save_accounts(self):
        try:
            json_data = json.dumps(self.accounts).encode('utf-8')
            encrypted_data = self.cipher.encrypt(json_data)
            
            with open(DATA_FILE, "wb") as f:
                f.write(encrypted_data)
        except Exception as e:
            print(f"Error saving accounts: {e}")

    def add_account(self, name, number, password, service_type="Internet"):
        new_account = {
            "id": self._generate_id(),
            "name": name,
            "number": number,
            "password": password,
            "service_type": service_type
        }
        self.accounts.append(new_account)
        self.save_accounts()
        return new_account

    def delete_account(self, account_id):
        self.accounts = [acc for acc in self.accounts if acc["id"] != account_id]
        self.save_accounts()

    def update_account(self, account_id, **kwargs):
        for acc in self.accounts:
            if acc["id"] == account_id:
                for k, v in kwargs.items():
                    if k in acc:
                        acc[k] = v
                self.save_accounts()
                return True
        return False

    def get_accounts(self):
        return self.accounts

    def _generate_id(self):
        import uuid
        return str(uuid.uuid4())

if __name__ == "__main__":
    # Test
    am = AccountManager()
    print("Loaded accounts:", len(am.get_accounts()))
    # am.add_account("My Landline", "023333333", "topsecret", "Internet")
    # print("Accounts after add:", am.get_accounts())
