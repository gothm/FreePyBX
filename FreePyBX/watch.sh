#!/bin/sh
watchmedo log \
    --patterns="*.py;*.txt;*.html" \
    --ignore-directories \
    --recursive \
    .


