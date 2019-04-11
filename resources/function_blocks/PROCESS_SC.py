

class PROCESS_SC:

    def __init__(self):
        self.products_time = {'A': 10000,
                              'B': 15000,
                              'C': 20000}
        self.execution_index = 0
        self.product_list = None

        self.current_product_id = 0
        self.current_time = 0
        self.current_vs_result = 0

    def __del__(self):
        pass

    def schedule(self, event_name, event_value, product_str, vs_out):
        # INPUT VARIABLES
        # P_LIST - product list (HARDCODED)
        # VS_OUT - result from vision system inspection (VS_SC)

        # OUTPUT EVENTS
        # RA - start robotic arm (RA_SC)
        # VS - start vision system inspection (VS_SC)
        # ASB - start interface assembly (INTERFACE_SC)
        # INS - feedback inspection to interface (INTERFACE_SC)

        # OUTPUT VARIABLES
        # P_ID - product identifier (INTERFACE_SC)
        # TIME - process time (INTERFACE_SC)
        # VS_OUT - result from vision system inspection (INTERFACE_SC)

        # INIT - start the PROCESS_SC (INTERFACE_SC)
        if event_name == 'INIT':
            # splits the products string in a list of products
            self.product_list = product_str.split(',')
            self.execution_index = 0
            self.current_vs_result = 0
            # gets the current values of the product_id and time to send to the interface assembler
            self.current_product_id = self.product_list[self.execution_index]
            self.current_time = self.products_time[self.current_product_id]
            # start the robotic arm
            return [event_value, None, None, None,
                    self.current_product_id, self.current_time, self.current_vs_result]

        # NEW_PRODUCT - (INTERFACE_SC)
        elif event_name == 'NEW_PRODUCT':
            self.execution_index += 1
            # gets the current values of the product_id and time to send to the interface assembler
            self.current_product_id = self.product_list[self.execution_index]
            self.current_time = self.products_time[self.current_product_id]
            # start the robotic arm
            return [event_value, None, None, None,
                    self.current_product_id, self.current_time, self.current_vs_result]

        # RA_END - robotic arm ended the movement (RA_SC)
        elif event_name == 'RA_END':
            # gets the current values of the product_id and time to send to the interface assembler
            self.current_product_id = self.product_list[self.execution_index]
            self.current_time = self.products_time[self.current_product_id]
            # starts the assembly
            return [None, None, event_value, None,
                    self.current_product_id, self.current_time, self.current_vs_result]

        # VS_END - vision system ended the inspection (VS_SC)
        elif event_name == 'VS_END':
            # pass the result from the vision system
            self.current_vs_result = vs_out
            # sends the result from the vision system
            return [None, None, None, event_value,
                    self.current_product_id, self.current_time, self.current_vs_result]

        # ASB_END - interface system ended the assembly (INTERFACE_SC)
        elif event_name == 'ASB_END':
            # starts the vision system inspection
            return [None, event_value, None, None,
                    self.current_product_id, self.current_time, self.current_vs_result]
