from locust import HttpUser, task
from random import randint

class AwesomeApplication(HttpUser):
    @task
    def hello(self):
        self.client.get("/")
        
    # @task
    # def world(self):
    #     self.client.get("/world")     

    # @task
    # def square(self):
    #     self.client.get(f"/square/{randint(0,100)}")     