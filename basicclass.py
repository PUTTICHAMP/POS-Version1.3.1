class Dog():
    """นี่คือคลาสของหมา"""
    def __init__(self, name):
        self.name = name
        print('My name is ', self.name)
        self.sit()

    def sit(self):
        """สั่งให้นั่ง"""
        print(self.name + 'กำลังนั่ง')

# bob = Dog('Bob')

class SARDog(Dog):
    def __init__(self, name):
        super().__init__(name)

    def search(self):
        print(self.name + 'กำลังค้นหา')


bobby = SARDog('bobby')
bobby.search()

