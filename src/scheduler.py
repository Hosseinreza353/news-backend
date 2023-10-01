import rocketry
from rocketry.conds import every
from rocketry.args import Task
from datetime import datetime
import aiofiles

# import os
import sys

# import contextlib
import subprocess

# import threading
from pathlib import Path


class Scheduler(object):
    engine: rocketry.Rocketry = None

    def __new__(cls, *args, **kwargs):
        if not Scheduler.engine:
            Scheduler.engine = rocketry.Rocketry(config={"task_execution": "thread"})
        return super().__new__(cls, *args, **kwargs)

    def add_crawler_task(self):
        # @contextlib.contextmanager
        # def cwd(path):
        #     prev_cwd = Path.cwd()
        #     os.chdir(path)
        #     try:
        #         yield
        #     finally:
        #         os.chdir(prev_cwd)

        async def run_crawler_task(this_task=Task()):
            if not this_task.session.parameters["first_run"]:
                # print(threading.get_ident(), end=" | ")
                print("run clustering at:", datetime.utcnow(), flush=True)
                HOME_DIR = Path(__file__).resolve().parents[1]
                crawler_script_cwd = HOME_DIR / "news_crawl" / "news_crawl"
                p = subprocess.Popen(
                    [sys.executable or "python", "main.py"],
                    cwd=str(crawler_script_cwd),
                    stdout=subprocess.PIPE,
                )
                # print("+"*20)
                async with aiofiles.open(
                    crawler_script_cwd.parents[0] / "crawler.log", "wb"
                ) as f:
                    # f.writelines(p.stdout.readline)
                    for line in iter(p.stdout.readline, b""):
                        # print(line)
                        await f.write(line)
                # print("-"*20, flush=True)
            else:
                this_task.session.parameters["first_run"] = False

        self.engine.params(first_run=True)
        self.engine.task(
            name=f"crawler_task",
            func=run_crawler_task,
            start_cond=every("5 minutes"),
            execution="thread",
            # parameters={"first_run": True},
        )
