from locust import Locust, TaskSet, task, between


class MyTaskSet(TaskSet):
    @task
    def my_task(self):
        print("executing my_task")


class User(Locust):
    task_set = MyTaskSet
    wait_time = between(5, 15)
