import logging
import csv
from datetime import datetime
import os

class CSVFormatter(logging.Formatter):
    def __init__(self):
        super().__init__()
        self.output = []
        self.start_time = datetime.now()

    def format(self, record):
        timestamp = datetime.fromtimestamp(record.created)
        time_since_start = (timestamp - self.start_time).total_seconds()
        return [timestamp.strftime('%Y-%m-%d %H:%M:%S'), record.getMessage(), f"{time_since_start:.2f}"]

class CSVHandler(logging.Handler):
    def __init__(self, filename):
        super().__init__()
        self.filename = filename
        self.formatter = CSVFormatter()

    def emit(self, record):
        formatted_record = self.formatter.format(record)
        with open(self.filename, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(formatted_record)

def setup_logger():
    logger = logging.getLogger('app_logger')
    logger.setLevel(logging.INFO)

    csv_file = 'app_log.csv'
    file_exists = os.path.isfile(csv_file)

    handler = CSVHandler(csv_file)
    logger.addHandler(handler)

    if not file_exists:
        with open(csv_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Timestamp', 'Event', 'Time Since Start (s)'])

    return logger

logger = setup_logger()