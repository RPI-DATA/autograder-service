import configparser
import argparse

import csv
import json

from os import listdir, getcwd
from os.path import isfile, join, isdir

from liteflow.core import *

import docker
from docker.types import Mount


class AutograderData:

    def __init__(self, submissions_dir=None, cwd=None, tests_dir=None, grader_image=None, grades_csv=None):
        self.submissions_dir = submissions_dir
        self.tests_dir = tests_dir
        self.submissions = None
        self.cwd = cwd
        self.grader_image = grader_image
        self.grades_csv = grades_csv
        self.submission_grades = []
        self.finished = False


class PrepareSubmissions(StepBody):

    def __init__(self):
        self.submissions_dir = None
        self.submissions = None

    def full_path(self, f):
        return join(getcwd(), self.submissions_dir, f)

    def is_dir(self, f):
        return isdir(join(self.submissions_dir, f))

    def run(self, context: StepExecutionContext) -> ExecutionResult:
        self.submissions = [self.full_path(f) for f in listdir(self.submissions_dir) if self.is_dir(f)]
        return ExecutionResult.next()


class Autograde(StepBody):

    def __init__(self):
        self.cwd = None
        self.tests_dir = None
        self.grader_image = None
        self.submission_grades = None

    @staticmethod
    def get_submission_name(path):
        return path[str.rfind(path, "/")+1:]

    def run(self, context: StepExecutionContext) -> ExecutionResult:
        submission = context.execution_pointer.context_item
        tests = f"{self.cwd}/{self.tests_dir}"

        docker_client = docker.from_env()

        mounts = [
            Mount(type='bind', source=submission, target='/opt/submission', read_only=True),
            Mount(type='bind', source=tests, target='/opt/tests', read_only=True)
        ]

        r = docker_client.containers.run(self.grader_image, mounts=mounts, auto_remove=True)
        this_grade = json.loads(r.decode("utf-8").strip())
        print(f"finished grading {context.execution_pointer.context_item}")

        # add the student to the JSON
        student = Autograde.get_submission_name(context.execution_pointer.context_item)
        this_grade["student"] = student

        self.submission_grades.append(this_grade)
        return ExecutionResult.next()


class AutograderCleanup(StepBody):

    def run(self, context: StepExecutionContext) -> ExecutionResult:
        print("Do assignment cleanup here (archive submissions, tests, etc.)")
        return ExecutionResult.next()


class AutograderDone(StepBody):

    def run(self, context: StepExecutionContext) -> ExecutionResult:
        print("DONE.  Press any key to exit")
        return ExecutionResult.next()


class SaveGradesToCSV(StepBody):

    def __init__(self):
        self.submission_grades = None
        self.grades_csv = None

    def run(self, context: StepExecutionContext) -> ExecutionResult:
        fieldnames = ["student", "score", "points_possible"]
        with open(self.grades_csv, "w") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.submission_grades)

        print("finished writing grades CSV")
        return ExecutionResult.next()


class AutograderWorkflow(Workflow):

    def id(self):
        return "AutograderWorkflow"

    def version(self):
        return 1

    def build(self, builder: WorkflowBuilder):
        builder \
            .start_with(PrepareSubmissions) \
            .input("submissions_dir", lambda data, context: data.submissions_dir) \
            .output('submissions', lambda step: step.submissions) \
            .for_each(lambda data, context: data.submissions) \
            .do(lambda x: x.start_with(Autograde)
                .input("cwd", lambda data, context: data.cwd) \
                .input("tests_dir", lambda data, context: data.tests_dir) \
                .input("grader_image", lambda data, context: data.grader_image) \
                .input("submission_grades", lambda data, context: data.submission_grades) \
                .output("submission_grades", lambda step: step.submission_grades)
                ) \
            .then(SaveGradesToCSV) \
            .input("grades_csv", lambda data, context: data.grades_csv) \
            .input("submission_grades", lambda data, context: data.submission_grades) \
            .then(AutograderCleanup) \
            .then(AutograderDone)


def run(config):

    host = configure_workflow_host()
    host.register_workflow(AutograderWorkflow())
    host.start()

    data = AutograderData(
        submissions_dir=config["DEFAULT"]["submissions_dir"],
        cwd=getcwd(),
        tests_dir=config["DEFAULT"]["tests_dir"],
        grader_image="autograder",
        grades_csv=config["DEFAULT"]["grade_csv"]
    )

    wid = host.start_workflow("AutograderWorkflow", 1, data)

    # TODO run workflow as part of Flask/Tornado service?
    input()
    host.stop()


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--config', help="configuration file for assignment to autograde", default="config.ini")
    args = parser.parse_args()

    config = configparser.ConfigParser()
    config.read(args.config)
    run(config)
