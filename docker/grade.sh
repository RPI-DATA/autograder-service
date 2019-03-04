#!/bin/bash
cp submission/*.ipynb .
jupyter nbconvert --to markdown --execute assignment.ipynb
python3 compute_grade.py assignment.md
