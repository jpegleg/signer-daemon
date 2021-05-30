#!/usr/bin/env bash

echo "$1" | nc localhost 9948 | redis-cli -x set "$2"
