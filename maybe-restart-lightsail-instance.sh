# Check if the instance name is provided
if [ $# -lt 1 ]; then
    echo "Usage: $0 <LIGHTSAIL_INSTANCE_NAME>"
    exit 1
fi

# Set variables
LIGHTSAIL_INSTANCE_NAME=$1
CURRENT_DIRECTORY="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
LOG_FILE="$HOME/.check-lightsail-$LIGHTSAIL_INSTANCE_NAME.log"
CHECK_ALARMS_SCRIPT="$CURRENT_DIRECTORY/check-lightsail-alarms.py"
RESTART_INSTANCE_SCRIPT="$CURRENT_DIRECTORY/restart-lightsail-instance.py"
PYTHON_PATH_PREFIX=$2

# Create a new log
echo "$(date '+%Y-%m-%d %H:%M:%S') Running $0" > $LOG_FILE

# Set python path
if [ -n "$PYTHON_PATH_PREFIX" ]; then
    echo "Using python with full path: $PYTHON_PATH_PREFIX" >> $LOG_FILE
    PYTHON=$PYTHON_PATH_PREFIX/python
else
    echo "Using python without full path" >> $LOG_FILE
    PYTHON=python
fi

# Check the system instance alarm
echo "Checking $LIGHTSAIL_INSTANCE_NAME instance" >> $LOG_FILE
$PYTHON $CHECK_ALARMS_SCRIPT $LIGHTSAIL_INSTANCE_NAME >> $LOG_FILE

# Check if the system instance alarm tripped
if [ $? -ne 0 ]; then
    echo "The system instance check failed. Restarting $LIGHTSAIL_INSTANCE_NAME ..." >> $LOG_FILE
    $PYTHON $RESTART_INSTANCE_SCRIPT $LIGHTSAIL_INSTANCE_NAME >> $LOG_FILE
    if [ $? -ne 0 ]; then
        echo "Failed to restart instance $LIGHTSAIL_INSTANCE_NAME" >> $LOG_FILE
        exit 1
    fi
else
    echo "The $LIGHTSAIL_INSTANCE_NAME system instance check succeeded." >> $LOG_FILE
fi
