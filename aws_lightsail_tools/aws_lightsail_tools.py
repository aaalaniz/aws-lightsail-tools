import time
from boto3.exceptions import Boto3Error
import logging


class AwsLightsailMonitorResult:
    pass


class AwsLightsailMonitorError(AwsLightsailMonitorResult):
    def __init__(self, error):
        self.error = error
        
    def __eq__(self, other):
        return self.__class__ == other.__class__ and self.error == other.error


class CheckInstanceFailed(AwsLightsailMonitorError):
    def __init__(self, error):
        super().__init__(error)
        
        
class RestartInstanceFailed(AwsLightsailMonitorError):
    def __init__(self, error):
        super().__init__(error)


class InstanceStatusOk(AwsLightsailMonitorResult):
    pass


class InstanceStatusCheckFailed(AwsLightsailMonitorResult):
    pass


class RestartInstanceSuccess(AwsLightsailMonitorResult):
    pass


class AwsLightsailMonitor:
    def __init__(self, lightsail, max_restart_waits=100, restart_wait_time=3):
        """
        Constructor for AwsLightsailMonitor.

        Parameters:
        - lightsail: Boto3 Lightsail client.
        - max_restart_waits: Number of times restart_instance should retry
        - restart_wait_time: Duration waited waiting for an instance to stop during a restart 
        """
        self.lightsail = lightsail
        self.max_restart_waits = max_restart_waits
        self.restart_wait_time = restart_wait_time

    def check_instance(self, instance_name):
        """
        Check the status of a Lightsail instance.

        Parameters:
        - instance_name: Name of the Lightsail instance to check.

        Returns:
        - A AwsLightsailMonitorResult that indicates the instance status.
        """

        try:
            logging.info(f"Getting alarms for instance {instance_name}")
            alarms_response = self.lightsail.get_alarms(
                monitoredResourceName=instance_name
            )

            for alarm in alarms_response['alarms']:
                logging.info(f"Checking alarm {alarm['metricName']}")
                if alarm['state'] == 'ALARM' and alarm['metricName'] == 'StatusCheckFailed_Instance':
                    logging.warning(f"{instance_name} status check failed")
                    return InstanceStatusCheckFailed
                logging.info(f"Alarm {alarm['metricName']} ok")

            return InstanceStatusOk

        except Boto3Error as error:
            logging.error(f"Error occurred checking the instance: {error}")
            return CheckInstanceFailed(error=error)

    def restart_instance(self, instance_name):
        """
        Restarts Lightsail instance
        
        Parameters:
        - instance_name: Name of the Lightstail instance to restart
        
        Returns:
        - A AwsLightsailMonitorResult that indicates the instance was successfully restarted or an error occurred 
        """
        
        # Stop the instance
        logging.info(f"Stopping instance {instance_name}")
        try:
            self.lightsail.stop_instance(instanceName=instance_name)

            # Wait until the instance is stopped
            retries = 0
            instance_stopped = False
            while retries < self.max_restart_waits:
                logging.info(f"Getting instance {instance_name}")
                response = self.lightsail.get_instance(instanceName=instance_name)
                state = response['instance']['state']['name']
                logging.info(f"{instance_name} state: {state}")
                if state == 'stopped':
                    logging.info(f"{instance_name} has stopped")
                    instance_stopped = True
                    break
                logging.info(f"Waiting for {instance_name} to stop. Trying again")
                time.sleep(self.restart_wait_time)
                retries = retries + 1
                
            if not instance_stopped:
                logging.error(f"Timed out waiting for {instance_name} to stop")
                return RestartInstanceFailed(error=RuntimeError("Timed out waiting for instance to stop"))

            # Start the instance
            logging.info(f"Starting instance {instance_name}")
            self.lightsail.start_instance(instanceName=instance_name)
            
            return RestartInstanceSuccess
        except Boto3Error as error:
            logging.error(f"Error occurred restarting the instance: {error}")
            return RestartInstanceFailed(error=error)
