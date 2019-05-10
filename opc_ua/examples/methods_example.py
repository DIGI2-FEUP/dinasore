from opcua import ua


def hello_word(parent, x):
    # print("Hello {}".format(x.Value[0]))
    "Hello {}".format(x.Value[0])
    return [ua.Variant(True, ua.VariantType.Boolean)]
