import argparse
from pathlib import Path
import sys

from .repo import Repository
from .storage import ObjectStore
from .index import Index
from .commit import create_commit
from .refs import create_branch, list_branches, checkout
from .checkout import checkout_branch
from .status import get_status
from .diff import diff_working_vs_index

# --------------------------
# Command implementations
# --------------------------

def cmd_init(args):
    repo = Repository.init(Path.cwd())
    print(f"Initialized pyvcs repository in {repo.vcs_dir}")


def cmd_add(args):
    repo = Repository.find(Path.cwd())
    store = ObjectStore(repo)
    index = Index(repo)

    for path_str in args.paths:
        path = Path(path_str)
        index.add(path, store)
        print(f"Added {path} to staging area")


def cmd_commit(args):
    repo = Repository.find(Path.cwd())
    try:
        commit_hash = create_commit(repo, args.message)
        print(f"Committed: {commit_hash}")
    except Exception as e:
        print(f"Error: {e}")


def cmd_branch(args):
    repo = Repository.find(Path.cwd())
    if args.name:
        try:
            create_branch(repo, args.name)
            print(f"Created branch {args.name}")
        except Exception as e:
            print(f"Error: {e}")
    else:
        branches = list_branches(repo)
        current = repo.current_branch()
        for b in branches:
            prefix = "*" if b == current else " "
            print(f"{prefix} {b}")


def cmd_checkout(args):
    repo = Repository.find(Path.cwd())
    try:
        checkout_branch(repo, args.name)
        print(f"Switched to branch {args.name}")
    except Exception as e:
        print(f"Error: {e}")

def cmd_status(args):
    repo = Repository.find(Path.cwd())
    status = get_status(repo)

    if status.staged:
        print("Changes to be committed:")
        for p in status.staged:
            print(f"  {p}")

    if status.modified:
        print("\nChanges not staged for commit:")
        for p in status.modified:
            print(f"  {p}")

    if status.untracked:
        print("\nUntracked files:")
        for p in status.untracked:
            print(f"  {p}")

    if not (status.staged or status.modified or status.untracked):
        print("Working tree clean")


def cmd_diff(args):
    repo = Repository.find(Path.cwd())
    diffs = diff_working_vs_index(repo)

    if not diffs:
        return

    for d in diffs:
        print(d.diff)


# --------------------------
# Argument parser setup
# --------------------------

def main():
    parser = argparse.ArgumentParser(prog="pyvcs")
    subparsers = parser.add_subparsers(dest="command")

    # init
    sp_init = subparsers.add_parser("init", help="Initialize a new pyvcs repository")
    sp_init.set_defaults(func=cmd_init)

    # add
    sp_add = subparsers.add_parser("add", help="Add file(s) to staging area")
    sp_add.add_argument("paths", nargs="+", help="Paths to files to add")
    sp_add.set_defaults(func=cmd_add)

    # commit
    sp_commit = subparsers.add_parser("commit", help="Commit staged changes")
    sp_commit.add_argument("-m", "--message", required=True, help="Commit message")
    sp_commit.set_defaults(func=cmd_commit)

    # branch
    sp_branch = subparsers.add_parser("branch", help="Create or list branches")
    sp_branch.add_argument("name", nargs="?", help="Name of branch to create")
    sp_branch.set_defaults(func=cmd_branch)

    # checkout
    sp_checkout = subparsers.add_parser("checkout", help="Switch branches")
    sp_checkout.add_argument("name", help="Branch name to checkout")
    sp_checkout.set_defaults(func=cmd_checkout)
    
    # status
    sp_status = subparsers.add_parser("status", help="Show working tree status")
    sp_status.set_defaults(func=cmd_status)

    # diff
    sp_diff = subparsers.add_parser("diff", help="Show unstaged changes")
    sp_diff.set_defaults(func=cmd_diff)

    # Parse arguments and dispatch
    args = parser.parse_args()
    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()