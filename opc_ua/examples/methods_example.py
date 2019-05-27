from opcua import ua


def hello_word(parent, *args):
    # print("Hello {}".format(x.Value[0]))
    "Hello {}".format(args[0].Value[0])
    return [ua.Variant(True, ua.VariantType.Boolean)]
