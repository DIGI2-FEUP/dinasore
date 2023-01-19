import threading

from can_bus.can_isotp import *

import moduleCommunication.moduleCommunication as mc

class CAN_DOTX:

    exit_request = False
    commModuleDotX = None
    receptionStarted = False
    def __init__(self,commModuleDotX, source, target):
        CAN_DOTX.commModuleDotX = commModuleDotX
        self.commModuleDotX = commModuleDotX
        CAN_DOTX.startSocketlessReception()
        self.socket = isotp.socket()
        # Configuring the sockets.
        self.busy = False
        
        #self.socket.set_fc_opts(stmin=1, bs=10)
        self.target= target
        self.thread_exit_request = False

        #print(source, target)
        addr = Address(AddressingMode.NormalFixed_29bits, source_address=source, target_address=target)
        #print(hex(addr.rx_arbitration_id_physical))
        if(target != 0) and (target!=2):
            CAN_ISOTP.filter_out_destination(target)

        #print(hex(addr.get_tx_arbitraton_id()))
        
        #print(hex(addr.get_rx_arbitraton_id()))
        self.socket.bind("can0", address = addr)
        #print("Open CommChannel between", source, "and ", target)
        #print(self.socket._socket.rxid)
        #print("Timeout", self.socket._socket.gettimeout())
    
    def sendMessage(self,message):    
        #print(" Sending ISOTP Message with address ", self.socket.address, message)
        self.socket.send(message)
    
    
    def close(self):
        self.thread_exit_request = True
        while(self.thread.is_alive()):
            pass
        if(self.target != 0) and (self.target!=2):
            CAN_ISOTP.add_destination(self.target)
        self.socket.close()
        
    def rcvMessage(self):
        self.thread = threading.Thread(target = CAN_DOTX.ISOTPMessageReception, args=(self,))
        self.thread.start()

    def ISOTPMessageReception(self):
        payload = None
        while(payload == None):
            if(self.thread_exit_request):
                return
            else:
                payload = self.socket.recv()
            
        thread = threading.Thread(target = CAN_DOTX.handleMessage, args =(self.commModuleDotX, self.target, payload))
        thread.start()


    def sendCANMessage(self,message, source, target):
        #print('SendingCanMessage')
        CAN_ISOTP.sendMessage(message, source, target)

    def socketlessReception():
        CAN_DOTX.reception = ThreadedCANReception()
        CAN_DOTX.reception.start()

                
        payload = []
        while CAN_DOTX.exit_request == False:
            if CAN_ISOTP.stack.available():
                #print('Received')
                [remote, payload] = CAN_ISOTP.stack.recv()
                thread = threading.Thread(target = CAN_DOTX.handleMessage, args =(CAN_DOTX.commModuleDotX, remote, payload))
                thread.start()

        CAN_DOTX.reception.shutdown()


    def startSocketlessReception():
        CAN_DOTX.exit_request=False
        if(not CAN_DOTX.receptionStarted):
            #print('Starting Reception')
            thread = threading.Thread(target = CAN_DOTX.socketlessReception)
            thread.start()
            CAN_DOTX.receptionStarted = True
    
    def stopSocketlessReception():
        CAN_DOTX.exit_request=True
        CAN_DOTX.receptionStarted = False


    def handleMessage(commModuleDotX, target, payload):

        msgId = int.from_bytes(payload[:2], 'big')
        #print('Handling message from', target)
        if(msgId == 0):
            pass
            # TIM Initiated Message (no reply expected)
    
            #print("Received payload on %d %d: %s" % (source, target, payload))
    
        if(msgId > 0x1000 and commModuleDotX.discovery_done == True):
            
            #print("Received TIM initiated Message")
            # TIM Initiated Message (reply Expected)

            [maxPayloadLen, commId] = commModuleDotX.open(target, True)
            commChannel = mc.CommChannel.getCommChannel(commModuleDotX.commChannels, commId)

            msgId = int.from_bytes(payload[:2], 'big')
        
            commChannel.inMessages.append(mc.Message(msgId, payload[2:]))

            length = len(payload[2:])

            commModuleDotX.commModuleDot0.notifyMsg(commId, True, length, length, length, 0)
        
            #print("Received payload on %d %d: %s" % (source, target, payload))
    
        elif(msgId > 0x0000 and msgId < 0x1000):
            # NCAP Initiated Message (reply expected)

            message = mc.Message(msgId, payload[2:])
            commChannel = mc.CommChannel.getCommChannelByOutMsg(commModuleDotX.commChannels, msgId)
            
            commChannel.inMessages.append(message)

            length = len(payload[2:])

            commModuleDotX.commModuleDot0.notifyRsp(commChannel.commId, msgId, length, length, length)

            #print("Received payload on %d %d: %s" % (source, target, payload))