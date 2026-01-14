# PyVCS

A lightweight version control system written in Python, implementing core VCS functionality with a Git-like interface and architecture.

## Overview

PyVCS is a command-line version control system that provides essential features for tracking file changes, managing branches, and maintaining project history. Built with a focus on simplicity and clarity, it demonstrates core VCS concepts including content-addressable storage, commit trees, and branch management.

## Features

- **Repository Management**: Initialize and manage repositories with a simple `.pyvcs` directory structure
- **Staging Area**: Add files to a staging index before committing
- **Commits**: Create immutable commit objects with tree-based snapshots
- **Branching**: Create and switch between branches for parallel development
- **Status Tracking**: View staged, modified, and untracked files
- **Diff Viewing**: Compare working directory changes against the staging area
- **Content-Addressable Storage**: SHA-1 based object storage for efficient deduplication

## Installation

### Requirements

- Python 3.8+

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd pyvcs
```

2. (Optional) Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies (if any):
```bash
pip install -r requirements.txt
```

## Usage

### Basic Workflow

1. **Initialize a repository**:
```bash
pyvcs init
```

2. **Add files to the staging area**:
```bash
pyvcs add file1.txt file2.txt
```

3. **Commit changes**:
```bash
pyvcs commit -m "Initial commit"
```

4. **Check repository status**:
```bash
pyvcs status
```

5. **View differences**:
```bash
pyvcs diff
```

6. **Create and switch branches**:
```bash
pyvcs branch feature-branch
pyvcs checkout feature-branch
```

7. **List branches**:
```bash
pyvcs branch
```

### Command Reference

| Command | Description |
|---------|-------------|
| `init` | Initialize a new PyVCS repository in the current directory |
| `add <paths...>` | Add file(s) to the staging area |
| `commit -m <message>` | Create a commit with the staged changes |
| `status` | Show the working tree status (staged, modified, untracked files) |
| `diff` | Show unstaged changes between working directory and index |
| `branch [name]` | Create a new branch or list all branches |
| `checkout <name>` | Switch to the specified branch |

## Architecture

PyVCS follows a Git-like architecture with the following components:

- **Repository** (`.pyvcs/`): Contains all repository metadata
  - `objects/`: Content-addressable storage for blobs, trees, and commits
  - `refs/heads/`: Branch references pointing to commit hashes
  - `HEAD`: Points to the current branch reference
  - `index`: Staging area (JSON format)

- **Object Types**:
  - **Blob**: Stores file content
  - **Tree**: Directory structure mapping names to object hashes
  - **Commit**: Snapshot with tree hash, parent commit, message, and timestamp

- **Storage**: Objects are stored using SHA-1 hashing in a two-level directory structure for efficient access

## Development

### Running Tests

```bash
pytest
```

### Project Structure

```
pyvcs/
├── vcs/              # Core VCS implementation
│   ├── repo.py       # Repository management
│   ├── storage.py    # Object storage backend
│   ├── index.py      # Staging area
│   ├── commit.py     # Commit creation
│   ├── objects.py    # Blob, Tree, Commit objects
│   ├── refs.py       # Branch references
│   ├── checkout.py   # Branch switching
│   ├── status.py     # Status tracking
│   ├── diff.py       # Diff computation
│   └── cli.py        # Command-line interface
├── tests/            # Test suite
└── README.md         # This file
```

