import logging
import os
import unittest
from unittest.mock import Mock
from aws_lightsail_tools.aws_lightsail_tools import CheckInstanceFailed, InstanceStatusOk, InstanceStatusCheckFailed, \
    RestartInstanceFailed, RestartInstanceSuccess
from aws_lightsail_tools.aws_lightsail_tools import AwsLightsailMonitor
from boto3.exceptions import Boto3Error
import json


class TestLightsailError(Boto3Error):
    pass


fixtures_dir = os.path.dirname(os.path.abspath(__file__)) + "/fixtures/"


def read_json_fixture(fixture_file):
    fixture_path = fixtures_dir + fixture_file

    with open(fixture_path, 'r') as file:
        return json.load(file)


class TestAwsLightsailMonitor(unittest.TestCase):

    def setUp(self):
        logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)
        self.lightsail = Mock()
        self.aws_lightsail_monitor = AwsLightsailMonitor(lightsail=self.lightsail)

    def test_check_instance_handles_failure_to_get_alarms(self):
        get_alarms_error = TestLightsailError("A failure occurred getting the instance alarms")
        self.lightsail.get_alarms.side_effect = get_alarms_error
        monitor_result = self.aws_lightsail_monitor.check_instance("test-instance")
        self.assertEqual(monitor_result, CheckInstanceFailed(error=get_alarms_error))

    def test_check_instance_with_no_alarms(self):
        no_alarms_response = read_json_fixture('aws-lightsail-response-no-alarms.json')
        self.lightsail.get_alarms.return_value = no_alarms_response
        monitor_result = self.aws_lightsail_monitor.check_instance("test-instance")
        self.assertEqual(monitor_result, InstanceStatusOk)

    def test_check_instance_with_instance_alarm_ok(self):
        alarm_ok_response = read_json_fixture('aws-lightsail-response-alarm-ok.json')
        self.lightsail.get_alarms.return_value = alarm_ok_response
        monitor_result = self.aws_lightsail_monitor.check_instance("test-instance")
        self.assertEqual(monitor_result, InstanceStatusOk)

    def test_check_instance_with_instance_alarm_failing(self):
        alarm_failing_response = read_json_fixture('aws-lightsail-response-alarm-failing.json')
        self.lightsail.get_alarms.return_value = alarm_failing_response
        monitor_result = self.aws_lightsail_monitor.check_instance("test-instance")
        self.assertEqual(monitor_result, InstanceStatusCheckFailed)

    def test_restart_instance_stop_instance_fails(self):
        stop_instance_error = TestLightsailError("A failure occurred stopping the instance")
        self.lightsail.stop_instance.side_effect = stop_instance_error
        monitor_result = self.aws_lightsail_monitor.restart_instance("test-instance")
        self.assertEqual(monitor_result, RestartInstanceFailed(error=stop_instance_error))
        self.lightsail.stop_instance.assert_called()
        self.lightsail.get_instance.assert_not_called()
        self.lightsail.start_instance.assert_not_called()

    def test_restart_instance_get_instance_fails(self):
        get_instance_error = TestLightsailError("A failure occurred getting the instance")
        self.lightsail.get_instance.side_effect = get_instance_error
        monitor_result = self.aws_lightsail_monitor.restart_instance("test-instance")
        self.assertEqual(monitor_result, RestartInstanceFailed(error=get_instance_error))
        self.lightsail.stop_instance.assert_called()
        self.lightsail.get_instance.assert_called()
        self.lightsail.start_instance.assert_not_called()

    def test_restart_instance_start_instance_fails(self):
        start_instance_error = TestLightsailError("A failure occurred starting the instance")
        stopped_response = read_json_fixture('aws-lightsail-get-instance-response-stopped.json')
        self.lightsail.get_instance.return_value = stopped_response
        self.lightsail.start_instance.side_effect = start_instance_error
        monitor_result = self.aws_lightsail_monitor.restart_instance("test-instance")
        self.assertEqual(monitor_result, RestartInstanceFailed(error=start_instance_error))
        self.lightsail.stop_instance.assert_called()
        self.lightsail.get_instance.assert_called()
        self.lightsail.start_instance.assert_called()

    def test_restart_instance_fails_waiting_for_instance_to_stop(self):
        self.aws_lightsail_monitor = AwsLightsailMonitor(
            lightsail=self.lightsail,
            max_restart_waits=3,
            restart_wait_time=0.1
        )
        stopping_response = read_json_fixture('aws-lightsail-get-instance-response-stopping.json')
        self.lightsail.get_instance.return_value = stopping_response
        monitor_result = self.aws_lightsail_monitor.restart_instance("test-instance")
        self.assertIsInstance(monitor_result, RestartInstanceFailed)
        self.assertIsInstance(monitor_result.error, RuntimeError)
        self.lightsail.stop_instance.assert_called()
        self.assertGreater(self.lightsail.get_instance.call_count, 1)
        self.lightsail.start_instance.assert_not_called()

    def test_restart_instance_success(self):
        stopped_response = read_json_fixture('aws-lightsail-get-instance-response-stopped.json')
        self.lightsail.get_instance.return_value = stopped_response
        monitor_result = self.aws_lightsail_monitor.restart_instance("test-instance")
        self.assertEqual(monitor_result, RestartInstanceSuccess)

    def test_restart_when_failing_with_failure_to_get_alarms(self):
        get_alarms_error = TestLightsailError("A failure occurred getting the instance alarms")
        self.lightsail.get_alarms.side_effect = get_alarms_error
        monitor_result = self.aws_lightsail_monitor.restart_if_failing("test-instance")
        self.assertEqual(monitor_result, CheckInstanceFailed(error=get_alarms_error))

    def test_restart_when_failing_success(self):
        alarm_failing_response = read_json_fixture('aws-lightsail-response-alarm-failing.json')
        stopped_response = read_json_fixture('aws-lightsail-get-instance-response-stopped.json')
        self.lightsail.get_alarms.return_value = alarm_failing_response
        self.lightsail.get_instance.return_value = stopped_response
        monitor_result = self.aws_lightsail_monitor.restart_if_failing("test-instance")
        self.assertEqual(monitor_result, RestartInstanceSuccess)

    def test_restart_when_failing_fails(self):
        alarm_failing_response = read_json_fixture('aws-lightsail-response-alarm-failing.json')
        start_instance_error = TestLightsailError("A failure occurred starting the instance")
        stopped_response = read_json_fixture('aws-lightsail-get-instance-response-stopped.json')
        self.lightsail.get_alarms.return_value = alarm_failing_response
        self.lightsail.get_instance.return_value = stopped_response
        self.lightsail.start_instance.side_effect = start_instance_error
        monitor_result = self.aws_lightsail_monitor.restart_if_failing("test-instance")
        self.assertEqual(monitor_result, RestartInstanceFailed(error=start_instance_error))


if __name__ == '__main__':
    unittest.main()
