
To build the docker image
```
$ docker build -t autograder .
```

To run the docker container to grade a notebook
```
$ cd ..
$ docker run --rm --mount type=bind,source="$(pwd)"/submissions,target=/opt/submission,readonly --mount type=bind,source="$(pwd)"/tests,target=/opt/tests,readonly autograder
```