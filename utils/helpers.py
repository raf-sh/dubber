import subprocess
import logging

# Configure logging
logging.basicConfig(
    filename="debug.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def run_subprocess_with_logging(command):
    """
    Runs a subprocess command and logs its output for debugging.
    """
    logging.info(f"Running command: {' '.join(command)}")
    try:
        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            shell=True
        )
        logging.info(f"STDOUT: {result.stdout}")
        logging.info(f"STDERR: {result.stderr}")
        logging.info(f"Return code: {result.returncode}")

        if result.returncode != 0:
            print(f"Splitting audio failed, return code: {result.returncode}")
            logging.error(f"Command failed with return code {result.returncode}")
            logging.error(f"Error output: {result.stderr}")
    except Exception as e:
        logging.error(f"Exception occurred while running command: {e}")
        raise