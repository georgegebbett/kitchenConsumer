class GrocyItem:
    def __init__(self, id: int, name: str):
        self.id = id
        self.name = name

    def __repr__(self):
        return f"Id: {self.id} Name: {self.name}"
