import bcrypt
import database

def register_user(username, password):
    if not username or not password:
        return False, "⚠️ Fields cannot be empty."
    
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    success = database.add_user(username, hashed.decode('utf-8'))
    
    if success:
        return True, "✅ User created! Please log in."
    else:
        return False, "❌ Username already exists."

def authenticate_user(username, password):
    stored_hash = database.get_user(username)
    if not stored_hash:
        return False
    
    return bcrypt.checkpw(password.encode('utf-8'), stored_hash[0].encode('utf-8'))