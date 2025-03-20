class Product:
    def __init__(self, product_id, name, description, brand, product_type):
        self.product_id = product_id
        self.name = name
        self.description = description
        self.brand = brand
        self.product_type = product_type

    def to_dict(self):
        return {
            "productId": self.product_id,
            "productName": self.name,
            "productDescription": self.description,
            "productBrand": self.brand,
            "type": self.product_type
        }