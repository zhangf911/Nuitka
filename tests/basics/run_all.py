#!/usr/bin/env python
#     Copyright 2015, Kay Hayen, mailto:kay.hayen@gmail.com
#
#     Python tests originally created or extracted from other peoples work. The
#     parts were too small to be protected.
#
#     Licensed under the Apache License, Version 2.0 (the "License");
#     you may not use this file except in compliance with the License.
#     You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#     Unless required by applicable law or agreed to in writing, software
#     distributed under the License is distributed on an "AS IS" BASIS,
#     WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#     See the License for the specific language governing permissions and
#     limitations under the License.
#

import os, sys

# Find common code relative in file system. Not using packages for test stuff.
sys.path.insert(
    0,
    os.path.normpath(
        os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            ".."
        )
    )
)
from test_common import (
    my_print,
    setup,
    decideFilenameVersionSkip,
    compareWithCPython,
    hasDebugPython,
    createSearchMode
)

python_version = setup(needs_io_encoding = True)

search_mode = createSearchMode()

if python_version >= "3.4":
    # These tests don't work with 3.4 yet, and the list is considered the major
    # TODO for 3.4 support.
    search_mode.mayFailFor(
        # The "__class__" doesn't work as expected.
        "BuiltinSuper.py",

        # Too little attributes for generator objects, "__del__" is missing it
        # seems.
        "GeneratorExpressions.py",

        # Prepared dictionaries of "enum.Enums" are not used early enough
        "Classes34.py",
    )


# Create large constants test on the fly, if it's not there, not going to
# add it to release archives for no good reason.
if not os.path.exists("BigConstants.py"):
    with open("BigConstants.py", 'w') as output:
        output.write(
            "# Automatically generated test, not part of releases or git.\n\n"
        )
        output.write(
            "print('%s')\n" % ("1234" * 17000)
        )

# Now run all the tests in this directory.
for filename in sorted(os.listdir('.')):
    if not filename.endswith(".py"):
        continue

    if not decideFilenameVersionSkip(filename):
        continue

    extra_flags = ["expect_success", "remove_output"]

    # This test should be run with the debug Python, and makes outputs to
    # standard error that might be ignored.
    if filename.startswith("Referencing"):
        extra_flags.append("python_debug")

    # This tests warns about __import__() used.
    if filename == "OrderChecks.py":
        extra_flags.append("ignore_stderr")

    # TODO: Nuitka does not give output for ignored exception in dtor, this is
    # not fully compatible and potentially an error.
    if filename == "YieldFrom33.py":
        extra_flags.append("ignore_stderr")

    active = search_mode.consider(
        dirname  = None,
        filename = filename
    )

    if active:
        if filename.startswith("Referencing") and not hasDebugPython():
            my_print("Skipped (no debug Python)")
            continue

        needs_2to3 = python_version.startswith('3') and \
                     not filename.endswith("32.py") and \
                     not filename.endswith("33.py")

        compareWithCPython(
            dirname     = None,
            filename    = filename,
            extra_flags = extra_flags,
            search_mode = search_mode,
            needs_2to3  = needs_2to3
        )
    else:
        my_print("Skipping", filename)

search_mode.finish()