term-key-survey
===============

This repository holds several tools that I've been building to examine the current state of keyboard input in terminal emulators.

There is a rather large variation between different terminals, and I've often wished to get a better overview of what's supported by what terminals.
In the future, I'd love to even push for some standardization of keyboard handling... but for now I'll settle for just understanding what's happening where so I can configure around it.


The `term-key-survey.py` script
-------------------------------

This is the most important tool here - when run, it gathers information about the terminal it's running under, and then asks you to press several key combinations.
It then builds a JSON file with the resulting data.


The `term-key-viewer` app
-------------------------

This is a Vue.js web app built to view and compare the results of several `term-key-survey.py` sessions.
It depends on a `term-key-viewer/src/results.json` file that can be built/updated by the `term-key-viewer/update-results.sh` script
