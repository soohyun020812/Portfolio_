import re
import sys

if len(sys.argv) == 2:
    branch_name = sys.argv[1]
    pattern = re.compile(r".*feature-(.+)/(.+)")
    matches = pattern.match(branch_name)

    if matches:
        app_name, feature_name = matches.groups()
        app_name = app_name.replace("-", "_")
        words = feature_name.split("-")
        tc_feature_name = "".join([word.title() for word in words]) + "TestCase"
        print(f"{app_name} {tc_feature_name}")
