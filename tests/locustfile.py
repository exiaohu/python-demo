from locust import HttpUser, between, task


class APIUser(HttpUser):
    wait_time = between(1, 3)

    @task
    def health_check(self):
        self.client.get("/healthz")

    @task(3)
    def read_root(self):
        self.client.get("/")

    @task(2)
    def metrics(self):
        self.client.get("/metrics")
