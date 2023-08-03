#!/bin/bash
cd models
aerich upgrade
cd ..
uvicorn main:app --host 0.0.0.0 --port 8000