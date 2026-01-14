import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import pytest
from vcs.repo import Repository
import os


@pytest.fixture
def temp_repo(tmp_path):
    cwd = os.getcwd()
    os.chdir(tmp_path)

    repo = Repository.init(tmp_path)

    yield repo

    os.chdir(cwd)