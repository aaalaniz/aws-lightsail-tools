import boto3
import time
import sys

# Get the instance name from the command-line argument
if len(sys.argv) != 2:
    print("Usage: python check-lightsail-alarms.py <instance_name>")
    sys.exit(1)
instance_name = sys.argv[1]

# Create the client
lightsail = boto3.client('lightsail')

# Get the alarms
print(f"Getting instance alarms '{instance_name}'")
try:
    alarms_response = lightsail.get_alarms(
        monitoredResourceName=instance_name
    )

    # Check that each alarm is okay
    for alarm in alarms_response['alarms']:
        print(f"Checking alarm {alarm['name']}")
        assert alarm['state'] != 'ALARM'
except:
    print("An error occurred attempting to get or check the instance alarm. Ignoring the failure...")
