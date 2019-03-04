import argparse

def run(assignment):

    with open(assignment) as output:
        content = output.readlines()
        content = [x.strip() for x in content if x != '']
        content = list(filter(lambda x: x != '', content))

    _codeblock = False
    _okpy_check = False

    num_checks = 0
    num_passes = 0
    
    for x in content:
        if x == "```python":
            _codeblock = True
        elif _codeblock and "check('tests" in x:
            _okpy_check = True
        elif _codeblock and x == "```":
            _codeblock = False
        elif _okpy_check and not _codeblock:
            num_checks = num_checks + 1
            _okpy_check = False
            if x == "<p>All tests passed!</p>":
                num_passes = num_passes + 1

    print(f"{{\"score\": {num_passes}, \"points_possible\": {num_checks}}}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('submission', help=".ipynb notebook to grade")
    args = parser.parse_args()
    run(args.submission)
