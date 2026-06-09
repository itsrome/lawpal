# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'web'))
from app import app

if __name__ == "__main__":
    app.run()
