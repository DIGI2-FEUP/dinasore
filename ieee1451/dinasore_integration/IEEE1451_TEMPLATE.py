class IEEE1451_TEMPLATE:

    def __init__(self, ncap):
        self.ncap = ncap
        ## Insert initialization code here ##    
        pass
    
    def schedule(self, event_name, event_value): 
    # FB InputVars should appear as arguments of this function
        
        if event_name == 'INIT':
            ## Insert INIT event triggered code here ##
            return [event_value, None]

        if event_name == 'RUN': # event_name == 'READ'
            ## Insert RUN/READ event triggered code here ##
            return [None, event_value]
        
        # FB OutputEvents and OutputVars should appear as return values of each condition