from enum import Enum

auth_factor = Enum("AuthFactor",{"q":"1","W":"2"})

print(auth_factor)

print(list(auth_factor))