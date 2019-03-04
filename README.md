# autograder-service

An autograding service that leverages a [LiteFlow](https://github.com/danielgerlag/liteflow) workflow to score  Jupyter notebooks using the [Gopher-Grader](https://github.com/data-8/Gofer-Grader) auto-grading library.

LiteFlow is used to manage a workflow whereby each submission is graded in an independent docker container, ensuring isolation of assignments during grading.  A configuration file 

The structure of this auto-grader service/workflow was inspired by [gofer_service](https://github.com/data-8/gofer_service).

## Docker

To build the generic docker image for grading notebooks
```
$ cd docker
$ docker build -t autograder .
```

To manually run the docker container to grade a notebook
```
$ cd ..
$ docker run --rm --mount type=bind,source="{full-path-to-submission-directory},target=/opt/submission,readonly --mount type=bind,source="{full-path-to-tests-directory},target=/opt/tests,readonly autograder
```

The running of docker containers is managed by the Autograde step of the AutograderWorkflow.

## Running the Workflow

To run the autograder workflow use python to execute ``autograder_workflow.py`` with a configuration file specified for the desired assignment.

example:
```bash
$ python3 autograder_workflow.py --config={config-file}
```

example output:
```bash
finished grading /Users/szednik/Projects/mgmt6940/autograder-service/assignment1_submissions/student2
finished grading /Users/szednik/Projects/mgmt6940/autograder-service/assignment1_submissions/student1
finished writing grades CSV
Do assignment cleanup here (archive submissions, tests, etc.)
DONE.  Press any key to exit

```

note - for the moment you will have to press a key after the workflow prints ``DONE.  Press any key to exit`` for the process to shutdown.

## Workflow Configuration

The assignment submission directory, tests directory, and grade CSV filename are specified to the workflow via a config file.

example:
```ini
[DEFAULT]
submissions_dir = assignment1_submissions
tests_dir = assignment1_tests
grade_csv = assignment1_grades.csv
```
