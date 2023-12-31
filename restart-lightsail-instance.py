import boto3
import time
import sys

# Get the instance name from the command-line argument
if len(sys.argv) != 2:
    print("Usage: python restart-lightsail-instance.py <instance_name>")
    sys.exit(1)
instance_name = sys.argv[1]

# Create the client
lightsail = boto3.client('lightsail')

# Stop the instance
print(f"Stopping Lightsail instance '{instance_name}'")
lightsail.stop_instance(instanceName=instance_name)

# Wait until the instance is stopped
while True:
    response = lightsail.get_instance(instanceName=instance_name)
    state = response['instance']['state']['name']
    if state == 'stopped':
        break
    time.sleep(3)

# Start the instance
print(f"Starting Lightsail instance '{instance_name}'")
lightsail.start_instance(instanceName=instance_name)
