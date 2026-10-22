class Detail:
    def __init__(self, name, length):
        self.name = name
        self.length = length

    def printLenth(self):
        print(f"Деталь {self.name} имеет длину {self.length} мм.")


detal_1 = Detail("Polka", 10)
detal_1.printLenth()
