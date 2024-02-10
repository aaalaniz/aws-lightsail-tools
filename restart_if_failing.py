import boto3
import logging
import argparse
from logging.handlers import RotatingFileHandler
from aws_lightsail_tools.aws_lightsail_tools import AwsLightsailMonitor
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="Restart AWS Lightsail instance if it is failing.")
    parser.add_argument("--instance", type=str, help="Name of the AWS Lightsail instance", required=True)
    args = parser.parse_args()
    instance_name = args.instance
    log_file = f"{Path.home()}/check-{instance_name}.log"

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            RotatingFileHandler(log_file, maxBytes=1024*1024, backupCount=1)
        ]
    )

    monitor = AwsLightsailMonitor(lightsail=boto3.client('lightsail'))
    monitor.restart_if_failing(instance_name)


if __name__ == "__main__":
    main()
    