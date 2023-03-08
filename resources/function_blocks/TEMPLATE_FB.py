

class TEMPLATE_FB:

    def __init__(self):
        pass

    def schedule(self, event_input_name, event_input_value, input_var1):

        if event_input_name == 'INIT':
            print('initialization...')
            output_var1 = "initialized."
            return [event_input_value, None, output_var1]

        elif event_input_name == 'RUN':
            print("execution...")
            output_var1 = 'hello ' + input_var1
            return [None, event_input_value, output_var1]
