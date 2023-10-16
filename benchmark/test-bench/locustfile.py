import tempfile
import time
from pathlib import Path

from locust import HttpUser, run_single_user, task


class BenchmarkSetup(HttpUser):
    # instruct Locust to ignore the weight property
    fixed_count = 1

    # number of HTTP requests to be sent per run
    request_repetitions = 50_000

    # location where result csv files will be stored
    results_directory = Path(tempfile.gettempdir()).joinpath("benchmark_results")
    results_filepath = None

    # lines are buffered in memory and written in batches
    # to not interfere with the benchmark
    results_buffer = []
    results_buffer_size = 10_000
    results_last_written_index = -1

    @task
    def benchmark(self):
        for _ in range(self.request_repetitions):
            self.client.get("/")

        # respect a special flag that might be set when this is run from the cli
        if hasattr(self, "stop_after_run") and self.stop_after_run:
            self.stop()
        else:
            self.environment.runner.quit()

    def on_start(self):
        self._reset_buffer()
        self._create_csv_file()
        assert self.results_filepath is not None
        self.environment.events.request.add_listener(self.request_success_listener)
        print(f"suite started. results will be written to {self.results_filepath}")

    def on_stop(self):
        self._write_buffer()
        self._reset_buffer()
        self.environment.events.request.remove_listener(self.request_success_listener)
        print(f"suite finished. results written to {self.results_filepath}")

    def request_success_listener(
        self, start_time, response_time, response, exception, **kwargs
    ):
        if exception is not None or response.status_code != 200:
            print(f"error ocurred. code: {response.status_code}. error: {exception}")
            return

        self._add_measurement_to_buffer(start_time, response_time)

    def _reset_buffer(self):
        self.results_buffer = []
        self.results_last_written_index = -1

    def _create_csv_file(self):
        self.results_directory.mkdir(parents=True, exist_ok=True)

        # clear old file paths
        self.results_filepath = None

        now = time.time()
        filename = f"benchmark_{time.strftime('%H-%M-%S', time.localtime(now))}_{int(now * 1000)}.csv"
        self.results_filepath = self.results_directory.joinpath(filename)
        self.results_filepath.touch(exist_ok=False)

        # write csv header to file
        with open(self.results_filepath, "a+") as f:
            f.write("start_time,response_time\n")

    def _add_measurement_to_buffer(self, start_time, response_time):
        self.results_buffer.append((start_time, response_time))

        # check if we potentially need to write the buffer to disk
        num_writeable = len(self.results_buffer) - self.results_last_written_index - 1
        if num_writeable >= self.results_buffer_size:
            self._write_buffer()

    def _write_buffer(self):
        with open(self.results_filepath, "a+") as f:
            last_index = len(self.results_buffer)
            for i in range(self.results_last_written_index + 1, last_index):
                start_time, response_time = self.results_buffer[i]
                f.write(f"{start_time:f},{response_time:.10f}\n")
            self.results_last_written_index = last_index - 1


if __name__ == "__main__":
    # instruct Locust to do one run and then stop (local debugging)
    BenchmarkSetup.stop_after_run = True
    BenchmarkSetup.host = "http://host.docker.internal:8080"
    run_single_user(BenchmarkSetup)
