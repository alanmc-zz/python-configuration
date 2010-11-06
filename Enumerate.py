class Enumerate:
    
    def __init__(self, names):
        for number, name in enumerate(names.split()):
            setattr(self, name, number)
