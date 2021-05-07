class Policy:

    pass


class PasswordPolicy(Policy):
    
    length_min: int = 0
    length_max: int = -1

    upper_min: int = 0
    upper_max: int = -1

    lower_min: int = 0
    lower_max: int = -1

    digit_min: int = 0
    digit_max: int = -1

    special_min: int = 0
    special_max: int = -1
