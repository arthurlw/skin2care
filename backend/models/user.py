import json
class User:
    def __init__(self, user_id, username, password, gender, skin_type, age, notifications, email, products, survey_id):
        self.user_id = user_id
        self.username = username
        # Consider hashing for security
        self.password = password  
        self.gender = gender
        self.skin_type = skin_type
        self.age = age
        self.notifications = notifications
        self.email = email
        self.products = products # This indicates to user's favorite product and data are stored in a list.
        self.survey_id = survey_id

    def to_dict(self):
        return {
            "userId": self.user_id,
            "username": self.username,
            "password": self.password,
            "gender": self.gender,
            "skinType": self.skin_type,
            "age": self.age,
            "notifications": self.notifications,
            "email": self.email,
            "fav_products": self.products,
            "survey_id": self.survey_id
        }
    
    
    def get_user_info(self):
        # return all of the information of one user in json format
        return json.dumps(self.to_dict())
    
    def save_fave_product(self, product):
        #Parameter type: Product
        self.products.append(product)
