operation_list = {}
def get_operation(path, method):
    operation_list[path+method] = False
    return path, method