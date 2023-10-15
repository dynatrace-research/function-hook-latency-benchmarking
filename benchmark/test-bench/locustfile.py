import csv
import os
import time

import numpy as np
from locust import HttpUser, run_single_user, task

# commandline options https://github.com/SvenskaSpel/locust-plugins#command-line-options
# locust -f any-locustfile-that-imports-locust_plugins.py --help


class BenchmarkSetup(HttpUser):
    # locust variable
    fixed_count = 1

    # object variables
    request_repetitions = 50_000

    # variables for csv export
    dir = "cvs_exports"
    filename = None  # will defined later since time when executed is included

    errors_during_test = 0
    csv_next_row_id = 0
    csv_logs_buffer_size = request_repetitions // 10
    csv_logs_colums_count = 2
    csv_logs_buffer = np.empty(
        [csv_logs_buffer_size, csv_logs_colums_count], dtype=float
    )

    def on_start(self):
        print("suite started")

        # add handler to forward finished requests to csv exporter
        self.environment.events.request.add_listener(self.request_success_listener)

        # create directory for the benchmarks data (csv)
        if not os.path.exists(self.dir):
            os.mkdir(self.dir)

        # create benchmark file with name "benchmark_<time in millisec>.csv"
        current_time = time.time()
        filename = (
            "benchmark_"
            + time.strftime("%H-%M-%S", time.localtime(current_time))
            + "_"
            + str(int(current_time * 1000))
            + ".csv"
        )
        self.filename = os.path.join(self.dir, filename)
        if not os.path.exists(self.filename):
            open(self.filename, "w").close()

        # write csv header
        with open(self.filename, "a+") as f:
            f.write("start_time,response_time\n")

    def on_stop(self):
        self.write_statistic()
        print("suite finished")

    def request_success_listener(
        self, start_time, response_time, response, exception, **_kwargs
    ):
        if exception or response.status_code != 200:
            self.errors_during_test += 1
            print(
                "Error ocurred, HTTP status code was " + str(response.status_code) + "!"
            )
            return

        self.saveStatistic(start_time, response_time)

    def saveStatistic(self, start_time, response_time):
        if self.csv_next_row_id >= self.csv_logs_buffer_size:
            self.write_statistic()
        self.csv_logs_buffer[self.csv_next_row_id] = [start_time, response_time]
        self.csv_next_row_id += 1

    def write_statistic(self):
        with open(self.filename, "a+") as f:
            csv_writer = csv.writer(f)

            for i in range(self.csv_next_row_id):
                csv_writer.writerow(self.csv_logs_buffer[i])
            self.csv_next_row_id = 0

    @task
    def benchmark(self):
        for i in range(self.request_repetitions):
            self.client.get("/")

        # stop benchmark
        if hasattr(self, "debugFlag"):
            # stop user and with that exit run_single_user() function
            self.stop()
        else:
            self.environment.runner.quit()


# if launched directly, e.g. "python3 debugging.py", not "locust -f debugging.py"
if __name__ == "__main__":
    BenchmarkSetup.debugFlag = True
    BenchmarkSetup.host = "http://host.docker.internal:8080"
    run_single_user(BenchmarkSetup)
