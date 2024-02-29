# AWS Lightsail Tools

A Python module and scripts to help manage AWS Lightsail resources. Lightsail provides options for monitoring system health such as CPU utilization or instance status checks. Use this project to automate simple adminstration tasks such as checking or restarting an instance.

## Getting Started

To get started, install the following.

* Python 3.11
* Pip
* Pyinstaller (Optional)

You will need to setup an AWS CLI with valid credentials as documented [here](https://docs.aws.amazon.com/en_us/lightsail/latest/userguide/lightsail-how-to-set-up-access-keys-to-use-sdk-api-cli.html), and then, install the project's dependencies with pip as shown below.

```bash
pip install -r requirements.txt
```

## Usage

The primary use of this project is to restart a Lightsail instance if the system status check is failing. This is often the most common remediation when an instance fails the check. A system status check alarm is required for this script to work as expected. For more details about setting up AWS Lightsail monitors, see the [documentation](https://docs.aws.amazon.com/en_us/lightsail/latest/userguide/amazon-lightsail-viewing-instance-health-metrics.html).

```bash
python restart_if_failing.py --instance your-instance-name
```

Alternatively, if setting up this script to run as a cron job then you can use `pyinstaller` to create an executable on your host.

```bash
pyinstaller restart_if_failing.py
```

The executable will be available at `dist/restart_if_failing/restart_if_failing` and then you can setup a cron job to check the host every few minutes and restart the instance if it is failing the status check.

```bash
CURRENT_DIRECTORY="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Schedule a check every five minutes
echo "*/5 * * * * $CURRENT_DIRECTORY/dist/restart_if_failing/restart_if_failing --instance your-instance-name e cron" | crontab -
```

## Running Tests

The project includes some unit tests. To run, execute the following.

```bash
python -m unittest discover tests
```

## License

This project is available under the [MIT license](LICENSE).
