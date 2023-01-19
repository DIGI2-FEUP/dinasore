from can_bus.isotp import Address, AddressingMode, TargetAddressType
class Address_Socketless(Address):

    def __init__(self, addressing_mode = AddressingMode.Normal_11bits, txid=None, rxid=None, target_address=None, source_address=None, address_extension=None, **kwargs):

        self.addressing_mode    = addressing_mode
        self.target_address     = target_address
        self.source_address     = source_address
        self.address_extension  = address_extension
        self.txid               = txid
        self.rxid               = rxid
        self.is_29bits          = True if self.addressing_mode in [ AddressingMode.Normal_29bits, AddressingMode.NormalFixed_29bits, AddressingMode.Extended_29bits, AddressingMode.Mixed_29bits] else False

        self.validate()

        # From here, input is good. Do some precomputing for speed optimization without bothering about types or values
        self.tx_arbitration_id_physical     = self._get_tx_arbitraton_id(self.source_address,TargetAddressType.Physical)
        self.tx_arbitration_id_functional   = self._get_tx_arbitraton_id(self.source_address,TargetAddressType.Functional) 
        self.tx_payload_prefix = bytearray()
        self.rx_prefix_size = 0

        if self.addressing_mode in [AddressingMode.Extended_11bits, AddressingMode.Extended_29bits]:
            self.tx_payload_prefix.extend(bytearray([self.target_address]))
            self.rx_prefix_size = 1
        elif self.addressing_mode in [AddressingMode.Mixed_11bits, AddressingMode.Mixed_29bits]:
            self.tx_payload_prefix.extend(bytearray([self.address_extension]))
            self.rx_prefix_size = 1

        self.rxmask = None
        if self.addressing_mode == AddressingMode.NormalFixed_29bits:
            self.rxmask = 0x18DA0000    # This should ignore variant between Physical and Functional addressing
        elif self.addressing_mode == AddressingMode.Mixed_29bits:
            self.rxmask = 0x18CD0000    # This should ignore variant between Physical and Functional addressing

        if self.addressing_mode in [AddressingMode.Normal_11bits, AddressingMode.Normal_29bits]:
            self.is_for_me = self._is_for_me_normal
        elif self.addressing_mode in [AddressingMode.Extended_11bits, AddressingMode.Extended_29bits]:
            self.is_for_me = self._is_for_me_extended
        elif self.addressing_mode == AddressingMode.NormalFixed_29bits:
            self.is_for_me = self._is_for_me_normalfixed
        elif self.addressing_mode == AddressingMode.Mixed_11bits:
            self.is_for_me = self._is_for_me_mixed_11bits
        elif self.addressing_mode == AddressingMode.Mixed_29bits:
            self.is_for_me = self._is_for_me_mixed_29bits
        else:
            raise RuntimeError('This exception should never be raised.')


    def get_tx_arbitraton_id(self, source_address=0, address_type=TargetAddressType.Physical):
        if address_type == TargetAddressType.Physical:
            return self._get_tx_arbitraton_id(source_address, address_type)
            #return self.tx_arbitration_id_physical
        else:
            return self._get_tx_arbitraton_id(source_address, TargetAddressType.Functional)
            #return self.tx_arbitration_id_functional

    def get_rx_arbitraton_id(self, address_type=TargetAddressType.Physical):
        if address_type == TargetAddressType.Physical:
            return self.rx_arbitration_id_physical
        else:
            return self.rx_arbitration_id_functional

    def _get_tx_arbitraton_id(self, remote_address, address_type):
        if self.addressing_mode == AddressingMode.Normal_11bits:
            return self.txid
        elif self.addressing_mode == AddressingMode.Normal_29bits:
            return self.txid
        elif self.addressing_mode == AddressingMode.NormalFixed_29bits:
            bits23_16 = 0xDA0000 if address_type==TargetAddressType.Physical else 0xDB0000
            return 0x18000000 | bits23_16 | (remote_address << 8) | self.source_address
        elif self.addressing_mode == AddressingMode.Extended_11bits:
            return self.txid
        elif self.addressing_mode == AddressingMode.Extended_29bits:
            return self.txid
        elif self.addressing_mode == AddressingMode.Mixed_11bits:
            return self.txid
        elif self.addressing_mode == AddressingMode.Mixed_29bits:
            bits23_16 = 0xCE0000 if address_type==TargetAddressType.Physical else 0xCD0000
            return 0x18000000 | bits23_16 | (self.target_address << 8) | self.source_address

    def _is_for_me_normalfixed(self, msg):
        if self.is_29bits == msg.is_extended_id:
            return ((msg.arbitration_id >> 16) & 0xFF) in [218,219] and (msg.arbitration_id & 0xFF00) >> 8 == self.source_address
            #return ((msg.arbitration_id >> 16) & 0xFF) in [218,219] and (msg.arbitration_id & 0xFF00) >> 8 == self.source_address and msg.arbitration_id & 0xFF == self.target_address
        return False
