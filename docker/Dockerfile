FROM jupyter/minimal-notebook:7f1482f5a136
RUN pip install git+https://github.com/grading/gradememaybe.git

RUN mkdir -p /opt/submission
RUN mkdir -p /opt/tests

WORKDIR /opt
VOLUME /opt/submission
VOLUME /opt/tests

COPY grade.sh /opt/grade.sh
COPY compute_grade.py /opt/compute_grade.py

# when creating image, copy the ipynb to /opt/submission/assignment.ipynb

CMD ["/bin/bash", "/opt/grade.sh"]