class Meas_Times:

    ### Register Tests ###
    # first_frame_register = []
    # message_register = []
    # close_file_register = []
    # before_file_register = []
    ### -------------- ###

    ### Discover Tests ###
    # ncap_startup = []
    # start_discover = []
    # send_discover = []
    # discover_response_ff = []
    # discover_response_msg = []
    # before_file = []
    # close_file = []
    ### -------------- ###
    
    ### Read Tests ###
    # read_service = []
    # open_channel = []
    # before_send_msg = []
    # before_send_ff = []
    # after_rcv_lf = []
    # after_rcv_msg = []
    # return_data = []
    # close_channel = []
    # ff = False
    # ### ---------- ###

    ### Read Tests ###
    # def __init__(self):
    #     self.read_service = []
    #     self.open_channel = []
    #     self.before_send_msg = []
    #     self.before_send_ff = []
    #     self.after_rcv_lf = []
    #     self.after_rcv_msg = []
    #     self.return_data = []
    #     self.close_channel = []
    #     self.ff = False
    ### ---------- ####

    def saveResult():
        pass

        ### Discover Tests ###

        # with open('/home/pi/Desktop/ncap_startup.txt', 'a') as f:
        #     f.write(str(Meas_Times.close_file[3] - Meas_Times.start_discover[0]) + '\n')
        #     f.close()
        # with open('/home/pi/Desktop/start_discover.txt', 'a') as f:
        #     f.write(str(Meas_Times.start_discover[0]-Meas_Times.ncap_startup[0]) + '\n')
        #     f.close()
        # with open('/home/pi/Desktop/send_discover.txt', 'a') as f:
        #     f.write(str(Meas_Times.send_discover[0]-Meas_Times.start_discover[0]) + '\n')
        #     f.close()
        # with open('/home/pi/Desktop/discover_response_ff.txt', 'a') as f:
        #     f.write(str(Meas_Times.discover_response_ff[0]-Meas_Times.send_discover[0]) + '\n')
        #     f.close()
        # with open('/home/pi/Desktop/discover_response_msg.txt', 'a') as f:
        #     f.write(str(Meas_Times.discover_response_msg[0]-Meas_Times.discover_response_ff[0]) + '\n')
        #     f.close()
        # with open('/home/pi/Desktop/before_file.txt', 'a') as f:
        #     f.write(str(Meas_Times.before_file[0]-Meas_Times.discover_response_msg[0]) + '\n')
        #     f.close()
        # with open('/home/pi/Desktop/close_file.txt', 'a') as f:
        #     f.write(str(Meas_Times.close_file[0]-Meas_Times.before_file[0]) + '\n')
        #     f.close()

    def showResults(self):
        pass

        ### Read Tests ###
        # print("Read Service -- Open Channel")
        # for i in range(20):
        #     value = Meas_Times.open_channel[i] - Meas_Times.read_service[i]
        #     print(value)

        # print("Open Channel -- Before Send Msg")
        # for i in range(20):
        #     value = Meas_Times.before_send_msg[i] - Meas_Times.open_channel[i]
        #     print(value)

        # print("Before Send Msg -- Before Send FF")
        # for i in range(20):
        #     value = Meas_Times.before_send_ff[i] - Meas_Times.before_send_msg[i]
        #     print(value)

        # print("Before Send FF -- After Rcv LF")
        # for i in range(20):
        #     value = Meas_Times.after_rcv_lf[i] - Meas_Times.before_send_ff[i]
        #     print(value)

        # print("After Rcv LF -- After Rcv Msg")
        # for i in range(20):
        #     value = Meas_Times.after_rcv_msg[i] - Meas_Times.after_rcv_lf[i]
        #     print(value)

        # print("After Rcv Msg -- Return Data")
        # for i in range(20):
        #     value = Meas_Times.return_data[i] - Meas_Times.after_rcv_msg[i]
        #     print(value)

        # print("Return Data -- Close Channel")
        # for i in range(20):
        #     value = Meas_Times.close_channel[i] - Meas_Times.return_data[i]
        #     print(value)

        # print("Read Service -- Close Channel")
        # for i in range(20):
        #     value = self.close_channel[i] - self.read_service[i]
        #     print(value)

        # print("Between Reads")
        # for i in range(19):
        #     value = self.read_service[i + 1] - self.read_service[i]
        #     print(value)

        ### Register Tests ###

        # print("First Frame -- Close File")
        # sum = 0
        # for i in range(20):
        #     value = Meas_Times.close_file_register[i*4 + 3] - Meas_Times.first_frame_register[i*4]
        #     sum = sum + value
        #     print(value)
        # print(sum / 20)

        # print("First Frame -- Message Received")
        # sum = 0
        # for i in range(20):
        #     value = Meas_Times.message_register[i] - Meas_Times.first_frame_register[i*2]
        #     sum = sum + value
        #     print(value)
        # print(sum / 20)
        
        # print("Message Received -- Before File")
        # sum = 0
        # for i in range(20):
        #     value = Meas_Times.before_file_register[i] - Meas_Times.message_register[i]
        #     sum = sum + value
        #     print(value)
        # print(sum / 20)

        # print("Before File -- Close File")
        # sum = 0
        # for i in range(20):
        #     value = Meas_Times.close_file_register[i] - Meas_Times.before_file_register[i]
        #     sum = sum + value
        #     print(value)
        # print(sum / 20)

        # print("First Frame")
        # for i in range(15):
        #     value = Meas_Times.first_frame_register[i]
        #     print(value)

        # print("Message Register")
        # for i in range(20):
        #     value = Meas_Times.message_register[i]
        #     print(value)

        # print("Before File")
        # for i in range(20):
        #     value = Meas_Times.before_file_register[i]
        #     print(value)

        # print("Close File")
        # for i in range(15):
        #     value = Meas_Times.close_file_register[i]
        #     print(value)