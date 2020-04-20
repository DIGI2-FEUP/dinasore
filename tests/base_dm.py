import unittest
from opc_ua import client


class BaseTests(unittest.TestCase):
    port_server = 4841
    base_list = [(0, 'Objects'), (2, 'SMART_COMPONENT')]
    manager_4diac = None

    # address = 'localhost'
    address = 'd_dinasore1'

    def test_fbs_creation(self):
        # check the number of fb
        n_fb = len(self.manager_4diac.manager_ua.config.fb_dictionary)
        # 1 start + 3*2 device + 1 service + 1 instance + 1*2 startpoint + 1 endpoint = 11
        self.assertEqual(n_fb, 11)

        c = client.UaClient('opc.tcp://{1}:{0}'.format(self.port_server, self.address))

        path = c.generate_path(self.base_list + [(2, 'DeviceSet')])
        children = c.get_object(path).get_children()
        self.assertEqual(len(children), 3)

        path = c.generate_path(self.base_list + [(2, 'ServiceDescriptionSet')])
        children = c.get_object(path).get_children()
        self.assertEqual(len(children), 1)

        path = c.generate_path(self.base_list + [(2, 'ServiceInstanceSet')])
        children = c.get_object(path).get_children()
        self.assertEqual(len(children), 1)

        path = c.generate_path(self.base_list + [(2, 'PointSet')])
        children = c.get_object(path).get_children()
        self.assertEqual(len(children), 2)

        c.disconnect()

    def test_methods(self):
        c = client.UaClient('opc.tcp://{1}:{0}'.format(self.port_server, self.address))

        method_path = c.generate_path(self.base_list + [(2, 'DeviceSet'), (2, 'TEMPERATURE_SENSOR_1'),
                                                        (2, 'Methods'), (2, 'CALIBRATE')])
        method_r = c.call_method(method_path.copy(), None)
        self.assertEqual(method_r, [True])

        method_path = c.generate_path(self.base_list + [(2, 'DeviceSet'), (2, 'PRESSURE_SENSOR_1'),
                                                        (2, 'Methods'), (2, 'CALIBRATE')])
        method_r = c.call_method(method_path.copy(), None)
        self.assertEqual(method_r, [True])

        method_path = c.generate_path(self.base_list + [(2, 'DeviceSet'), (2, 'PROCESS_TIME_1'),
                                                        (2, 'Methods'), (2, 'CALIBRATE')])
        method_r = c.call_method(method_path.copy(), None)
        self.assertEqual(method_r, [True])

        method_path = c.generate_path(self.base_list + [(2, 'ServiceInstanceSet'), (2, 'SERVICE_EXAMPLE_1'),
                                                        (2, 'Methods'), (2, 'CALIBRATE')])
        method_r = c.call_method(method_path.copy(), None)
        self.assertEqual(method_r, [True])

        method_path = c.generate_path(self.base_list + [(2, 'ServiceInstanceSet'), (2, 'SERVICE_EXAMPLE_1'),
                                                        (2, 'Methods'), (2, 'RUN')])
        method_r = c.call_method(method_path.copy(), 1, 1)
        self.assertEqual(isinstance(method_r[0], int), True)

        method_path = c.generate_path(self.base_list + [(2, 'PointSet'), (2, 'SP_EXAMPLE_1'),
                                                        (2, 'Methods'), (2, 'CALIBRATE')])
        method_r = c.call_method(method_path.copy(), None)
        self.assertEqual(method_r, [True])

        method_path = c.generate_path(self.base_list + [(2, 'PointSet'), (2, 'EP_EXAMPLE_1'),
                                                        (2, 'Methods'), (2, 'CALIBRATE')])
        method_r = c.call_method(method_path.copy(), None)
        self.assertEqual(method_r, [True])

        c.disconnect()

    def test_variables(self):
        c = client.UaClient('opc.tcp://{1}:{0}'.format(self.port_server, self.address))

        device1_vars = c.generate_path(self.base_list + [(2, 'DeviceSet'), (2, 'TEMPERATURE_SENSOR_1'),
                                                         (2, 'Variables')])
        device2_vars = c.generate_path(self.base_list + [(2, 'DeviceSet'), (2, 'PRESSURE_SENSOR_1'),
                                                         (2, 'Variables')])
        device3_vars = c.generate_path(self.base_list + [(2, 'DeviceSet'), (2, 'PROCESS_TIME_1'),
                                                         (2, 'Variables')])
        service_vars = c.generate_path(self.base_list + [(2, 'ServiceDescriptionSet'), (2, 'TEST_SERVICE'),
                                                         (2, 'Variables')])
        instances_vars = c.generate_path(self.base_list + [(2, 'ServiceInstanceSet'), (2, 'SERVICE_EXAMPLE_1'),
                                                           (2, 'Variables')])
        sp_vars = c.generate_path(self.base_list + [(2, 'PointSet'), (2, 'SP_EXAMPLE_1'), (2, 'Variables')])
        ep_vars = c.generate_path(self.base_list + [(2, 'PointSet'), (2, 'EP_EXAMPLE_1'), (2, 'Variables')])

        device1_children = c.get_object(device1_vars).get_children()
        device2_children = c.get_object(device2_vars).get_children()
        device3_children = c.get_object(device3_vars).get_children()
        service_children = c.get_object(service_vars).get_children()
        instance_children = c.get_object(instances_vars).get_children()
        sp_children = c.get_object(sp_vars).get_children()
        ep_children = c.get_object(ep_vars).get_children()

        self.assertEqual(len(device1_children), 1)
        self.assertEqual(len(device2_children), 1)
        self.assertEqual(len(device3_children), 1)
        self.assertEqual(len(service_children), 3)
        self.assertEqual(len(instance_children), 3)
        self.assertEqual(len(sp_children), 1)
        self.assertEqual(len(ep_children), 2)

        c.disconnect()

    def test_subscriptions(self):
        c = client.UaClient('opc.tcp://{1}:{0}'.format(self.port_server, self.address))

        device1 = c.generate_path(self.base_list + [(2, 'DeviceSet'), (2, 'TEMPERATURE_SENSOR_1'),
                                                    (2, 'Subscriptions')])
        device2 = c.generate_path(self.base_list + [(2, 'DeviceSet'), (2, 'PRESSURE_SENSOR_1'), (2, 'Subscriptions')])
        device3 = c.generate_path(self.base_list + [(2, 'DeviceSet'), (2, 'PROCESS_TIME_1'), (2, 'Subscriptions')])
        service = c.generate_path(self.base_list + [(2, 'ServiceDescriptionSet'), (2, 'TEST_SERVICE'),
                                                    (2, 'Subscriptions')])
        instances = c.generate_path(self.base_list + [(2, 'ServiceInstanceSet'), (2, 'SERVICE_EXAMPLE_1'),
                                                      (2, 'Subscriptions')])
        sp = c.generate_path(self.base_list + [(2, 'PointSet'), (2, 'SP_EXAMPLE_1'), (2, 'Subscriptions')])
        ep = c.generate_path(self.base_list + [(2, 'PointSet'), (2, 'EP_EXAMPLE_1'), (2, 'Subscriptions')])

        device1_children = c.get_object(device1).get_children()
        device2_children = c.get_object(device2).get_children()
        device3_children = c.get_object(device3).get_children()
        service_children = c.get_object(service).get_children()
        instance_children = c.get_object(instances).get_children()
        sp_children = c.get_object(sp).get_children()
        ep_children = c.get_object(ep).get_children()

        self.assertEqual(len(device1_children), 0)
        self.assertEqual(len(device2_children), 0)
        self.assertEqual(len(device3_children), 0)
        self.assertEqual(len(service_children), 0)
        self.assertEqual(len(instance_children), 1)
        self.assertEqual(len(sp_children), 0)
        self.assertEqual(len(ep_children), 1)

        c.disconnect()


class PipelineTests(unittest.TestCase):
    port_server = 4841
    base_list = [(0, 'Objects'), (2, 'SMART_COMPONENT')]
    manager_4diac = None
     # address = 'localhost'
    address = 'd_dinasore1'

    def test_workflow(self):
        c = client.UaClient('opc.tcp://{1}:{0}'.format(self.port_server, self.address))

        method_path = c.generate_path(self.base_list + [(2, 'ServiceInstanceSet'), (2, 'SERVICE_EXAMPLE_1'),
                                                        (2, 'Methods'), (2, 'RUN')])
        method_r = c.call_method(method_path.copy(), 1, 3)
        self.assertEqual(type(method_r[0]), int)

        final_var = c.generate_path(self.base_list + [(2, 'ServiceInstanceSet'), (2, 'SERVICE_EXAMPLE_3'),
                                                      (2, 'Variables'), (2, 'FREQUENCIES')])
        value = c.read(final_var)
        self.assertEquals(type(value), int)

        mid_var = c.generate_path(self.base_list + [(2, 'ServiceInstanceSet'), (2, 'SERVICE_EXAMPLE_2'),
                                                    (2, 'Variables'), (2, 'FREQUENCIES')])
        value = c.read(mid_var)
        self.assertEquals(type(value), int)

        c.disconnect()

    def test_workflow_method(self):
        c = client.UaClient('opc.tcp://{1}:{0}'.format(self.port_server, self.address))

        method_path = c.generate_path(self.base_list + [(2, 'ServiceInstanceSet'), (2, 'SERVICE_EXAMPLE_1'),
                                                        (2, 'Methods'), (2, 'RUN')])
        method_r = c.call_method(method_path.copy(), 3, 5)
        self.assertEqual(method_r[0], 8)

        method_path = c.generate_path(self.base_list + [(2, 'ServiceInstanceSet'), (2, 'SERVICE_EXAMPLE_1'),
                                                        (2, 'Methods'), (2, 'CALIBRATE')])
        method_r = c.call_method(method_path.copy(), None)
        self.assertEqual(method_r[0], True)

        init_var = c.generate_path(self.base_list + [(2, 'ServiceInstanceSet'), (2, 'SERVICE_EXAMPLE_1'),
                                                     (2, 'Variables'), (2, 'FREQUENCIES')])
        value = c.read(init_var)
        self.assertEquals(value, 9)

        mid_var = c.generate_path(self.base_list + [(2, 'ServiceInstanceSet'), (2, 'SERVICE_EXAMPLE_2'),
                                                    (2, 'Variables'), (2, 'FREQUENCIES')])
        value = c.read(mid_var)
        self.assertEquals(value, 12)

        final_var = c.generate_path(self.base_list + [(2, 'ServiceInstanceSet'), (2, 'SERVICE_EXAMPLE_3'),
                                                      (2, 'Variables'), (2, 'FREQUENCIES')])
        value = c.read(final_var)
        self.assertEquals(value, 18)

        c.disconnect()
