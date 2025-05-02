import json
class Routine:
    def __init__(self, routine_id, username, products, date_created, ):
        self.routine_id = routine_id
        self.username = username
        self.products = products  # List of Product objects
        self.date_created = date_created


    def to_dict(self):
        return {
            "routineId": self.routine_id,
            "username": self.username,
            "products": [product.to_dict() for product in self.products],
            "dateCreated": self.date_created
        }

    def get_product_info(self):
        # return all of the information of routine in json format
        return json.dumps(self.to_dict())
