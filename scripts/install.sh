#!/usr/bin/env bash

install() {
  python -m pip install -U pip
  pip install -r requirements/all.txt
  pip install -e .
}

install
