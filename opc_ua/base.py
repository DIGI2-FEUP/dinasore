from opcua import ua


class UaBase:

    def __init__(self):
        self.root = None
        self.methods_dictionary = dict()
        self.variables_dictionary = dict()

    def get_object(self, path):
        obj = self.root.get_child(path)
        return obj

    def create_object(self, index, new_obj_name, path=None):
        if path is None:
            self.root.add_object(index, new_obj_name)
        else:
            my_obj = self.root.get_child(path)
            my_obj.add_object(index, new_obj_name)

    def create_variable(self, path, index, var_name, val, writable):
        my_obj = self.root.get_child(path)
        my_var = my_obj.add_variable(index, var_name, val)

        if writable:
            my_var.set_writable()

    def create_method(self, path, index, method_name, func, input_args=None, output_args=None):
        my_obj = self.root.get_child(path)
        my_obj.add_method(index, method_name, func, input_args, output_args)

    def write(self, path, val):
        my_obj = self.root.get_child(path)
        my_obj.set_attribute(ua.AttributeIds.Value, ua.DataValue(val))

    def read(self, path):
        my_obj = self.root.get_child(path)
        val = my_obj.get_value()
        return val

    def call_method(self, path, *args):
        method_name = path[-1]
        del path[-1]

        path_string = "-".join(path)
        if path_string not in self.methods_dictionary:
            self.methods_dictionary[path_string] = self.root.get_child(path)

        result = self.methods_dictionary[path_string].call_method(method_name, *args)
        return result

    @staticmethod
    def generate_path(pair_list):
        path = []
        for index, object_name in pair_list:
            pair_string = "{0}:{1}".format(index, object_name)
            path.append(pair_string)
        return path
