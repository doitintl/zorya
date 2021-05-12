import os
import multiprocessing


def max_workers():
    return multiprocessing.cpu_count()


worker_class = "uvicorn.workers.UvicornWorker"
workers = max_workers()

bind = "0.0.0.0:" + os.environ.get("PORT", "8080")
workers = multiprocessing.cpu_count() * 2 + 1
