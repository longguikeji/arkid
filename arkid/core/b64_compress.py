
class Compress(object):

    jinzhi = 64

    def __init__(self):
        pass

    def encode_b64(self, n):
        table = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-_"
        # print(table, len(table))
        result = []
        temp = n
        if 0 == temp:
            result.append('0')
        else:
            while 0 < temp:
                index = int(temp % self.jinzhi)
                result.append(table[index])
                temp //= self.jinzhi
                # print(index, temp)
        return ''.join([x for x in reversed(result)])

    def decode_b64(self, str):
        table = {"0": 0, "1": 1, "2": 2, "3": 3, "4": 4, "5": 5,
            "6": 6, "7": 7, "8": 8, "9": 9,
            "a": 10, "b": 11, "c": 12, "d": 13, "e": 14, "f": 15, "g": 16,
            "h": 17, "i": 18, "j": 19, "k": 20, "l": 21, "m": 22, "n": 23,
            "o": 24, "p": 25, "q": 26, "r": 27, "s": 28, "t": 29, "u": 30,
            "v": 31, "w": 32, "x": 33, "y": 34, "z": 35,
            "A": 36, "B": 37, "C": 38, "D": 39, "E": 40, "F": 41, "G": 42,
            "H": 43, "I": 44, "J": 45, "K": 46, "L": 47, "M": 48, "N": 49,
            "O": 50, "P": 51, "Q": 52, "R": 53, "S": 54, "T": 55, "U": 56,
            "V": 57, "W": 58, "X": 59, "Y": 60, "Z": 61,
            "-": 62, "_": 63}
        result = 0
        for i in range(len(str)):
            result *= self.jinzhi
            result += table[str[i]]
        return result
    
    def _encrypt(self, test_str):
        '''
        识别带0b1的
        '''
        int_2 = int(test_str, 2)
        int_64 = self.encode_b64(int_2)
        return int_64
    
    def encrypt(self, test_str):
        '''
        识别不带0b1的
        '''
        test_str = '0b1{}'.format(test_str)
        return self._encrypt(test_str)
    
    def _decrypt(self, int_64):
        '''
        解析出带0b1的
        '''
        return bin(self.decode_b64(int_64))
    
    def decrypt(self, int_64):
        '''
        解析出不带0b1的
        '''
        return self.remove_0b1(self._decrypt(int_64))
    
    def remove_0b1(self, test_str):
        '''
        移除0b1
        '''
        return test_str.replace('0b1', '')