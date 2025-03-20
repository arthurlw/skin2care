class User:
    def __init__(self, user_id, username, password, gender, skin_type, age):
        self.user_id = user_id
        self.username = username
        # Consider hashing for security
        self.password = password  
        self.gender = gender
        self.skin_type = skin_type
        self.age = age

    def to_dict(self):
        return {
            "userId": self.user_id,
            "username": self.username,
            "gender": self.gender,
            "skinType": self.skin_type,
            "age": self.age
        }
