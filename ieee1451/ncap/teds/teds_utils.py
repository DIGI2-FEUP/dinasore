# *****************************************************************************************
# *    Copyright 2022 by Digital and Intelligent Industry Lab (DIGI2), systecfof@fe.up.pt *
# *    You may use, edit, run or distribute this file                                     *
# *    as long as the above copyright notice remains                                      *
# * THIS SOFTWARE IS PROVIDED "AS IS".  NO WARRANTIES, WHETHER EXPRESS, IMPLIED           *
# * OR STATUTORY, INCLUDING, BUT NOT LIMITED TO, IMPLIED WARRANTIES OF                    *
# * MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE APPLY TO THIS SOFTWARE.          *
# * DIGI2 Lab SHALL NOT, IN ANY CIRCUMSTANCES, BE LIABLE FOR SPECIAL, INCIDENTAL,         *
# * OR CONSEQUENTIAL DAMAGES, FOR ANY REASON WHATSOEVER.                                  *
# * For more information about the lab, see:                                              *
# * http://digi2.fe.up.pt                                                                 *
# *****************************************************************************************

import uuid
from sys import getsizeof

# Type 4, UUID, Globally Unique Identifier UUID, size 10
# TO-DO, implement as in the standard definition
def generate_uuid(north = None, west = None, year = None, date = None, sequence = None):
    return uuid.uuid4().bytes[:10]

def calc_length(data_block):
    return getsizeof(data_block, 0)

def calc_checksum(barray):

    sum = 0
#    for i in barray:
#        sum = sum + i
    
    return sum