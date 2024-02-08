import boto3
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
alarms_response = lightsail.get_alarms(
    monitoredResourceName=instance_name
)
print(f"Alarms response '{alarms_response}'")

# Check that each alarm is okay
for alarm in alarms_response['alarms']:
    print(f"Checking alarm {alarm['name']}")
    assert alarm['state'] != 'ALARM'
