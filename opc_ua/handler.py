from threading import Thread
from opc_ua.examples import workers_example


class SubHandler(object):
    """
    Subscription Handler. To receive events from server for a subscription
    data_change and event methods are called directly from receiving thread.
    Do not do expensive, slow or network operation there. Create another
    thread if you need to do such a thing
    """

    def event_notification(self, event):
        print ("New event received: ", event)

    def datachange_notification(self, node, val, data):
        t = Thread(target=workers_example.SubWorkers.datachange_notification_worker, args=(node, val, data))
        t.start()


