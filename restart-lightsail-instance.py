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
try:
    lightsail.stop_instance(instanceName=instance_name)

    # Wait until the instance is stopped
    retries = 0
    while retries < 10:
        response = lightsail.get_instance(instanceName=instance_name)
        state = response['instance']['state']['name']
        if state == 'stopped':
            break
        time.sleep(3)
        retries = retries + 1

    # Start the instance
    print(f"Starting Lightsail instance '{instance_name}'")
    lightsail.start_instance(instanceName=instance_name)
except:
    print("An error occurred trying to restart the instance. Ignoring the error...")
