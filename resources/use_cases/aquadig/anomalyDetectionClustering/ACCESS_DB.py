#The function block accesses a given Host, by a specified port. It sends the authorization token and might (or not)
# specify the instants between capture (t_start and t_end)
# Inputs:
#   * Host-> specifying the Host name
#   * portGateway-> specifying the port to communicate with
#   * Authorization-> the token
#   *t_start-> (optional) instant to begin capture
#   *t_end-> (optional) instant to end capture
# The output consists in a partial-built Get request, along with the parameters to feedforward:
#   *request-> partial Get request
#   *authorization-> the authorization token is passed to the following fbt
#   *t_start-> (optional) the parameter is copied to the output
#   *t_end-> (optional) copied to the output

class ACCESS_DB:

    def __init__(self):
        self.host=""
        self.portGateway=""
        self.request=""
        self.authorization=""
        self.t_start=0
        self.t_end=0


    def schedule(self, event_input_name, event_input_value, Host, portGateway, Authorization, t_start, t_end):

        if event_input_name == 'INIT':
            return [event_input_value, None, None, None, 0, 0]

        elif event_input_name == 'RUN':
            self.host = Host
            self.portGateway = portGateway
            #creates the get request
            self.request = "http://{0}:{1}/measurements/".format(Host, portGateway)
            self.authorization=Authorization
            self.t_start=t_start
            self.t_end=t_end

            return [None, event_input_value, self.request, self.authorization, self.t_start, self.t_end]