from pathlib import Path


PYVCS_DIR = ".pyvcs"
OBJECTS_DIR = "objects"
REFS_DIR = "refs"
HEADS_DIR = "heads"
HEAD_FILE = "HEAD"
INDEX_FILE = "index"


class RepositoryError(Exception):
    pass


class Repository:
    def __init__(self, root: Path):
        self.root = root
        self.vcs_dir = root / PYVCS_DIR
        self.objects_dir = self.vcs_dir / OBJECTS_DIR
        self.refs_dir = self.vcs_dir / REFS_DIR
        self.heads_dir = self.refs_dir / HEADS_DIR
        self.head_file = self.vcs_dir / HEAD_FILE
        self.index_file = self.vcs_dir / INDEX_FILE

    @staticmethod
    def find(start: Path | None = None) -> "Repository":
        """
        Locate a pyvcs repository by walking up the directory tree.
        """
        if start is None:
            start = Path.cwd()

        current = start.resolve()

        while True:
            if (current / PYVCS_DIR).exists():
                return Repository(current)

            if current.parent == current:
                break

            current = current.parent

        raise RepositoryError("Not inside a pyvcs repository")

    @staticmethod
    def init(path: Path | None = None) -> "Repository":
        """
        Initialize a new pyvcs repository.
        """
        if path is None:
            path = Path.cwd()

        path = path.resolve()
        vcs_dir = path / PYVCS_DIR

        if vcs_dir.exists():
            raise RepositoryError("Repository already initialized")

        # Create directory structure
        (vcs_dir / OBJECTS_DIR).mkdir(parents=True)
        (vcs_dir / REFS_DIR / HEADS_DIR).mkdir(parents=True)

        # Create HEAD pointing to main branch
        head_file = vcs_dir / HEAD_FILE
        head_file.write_text("refs/heads/main")

        # Create main branch reference
        main_ref = vcs_dir / REFS_DIR / HEADS_DIR / "main"
        main_ref.write_text("")

        # Create empty index
        index_file = vcs_dir / INDEX_FILE
        index_file.write_text("")

        return Repository(path)

    def current_branch(self) -> str:
        """
        Return the name of the current branch.
        """
        if not self.head_file.exists():
            raise RepositoryError("HEAD file missing")

        ref = self.head_file.read_text().strip()
        if not ref.startswith("refs/heads/"):
            raise RepositoryError("Detached HEAD not supported")

        return ref.replace("refs/heads/", "")

    def head_ref_path(self) -> Path:
        """
        Return the file path of the current branch reference.
        """
        branch = self.current_branch()
        return self.heads_dir / branch

    def head_commit(self) -> str | None:
        """
        Return the hash of the current HEAD commit, or None if no commits yet.
        """
        ref_path = self.head_ref_path()
        if not ref_path.exists():
            return None

        content = ref_path.read_text().strip()
        return content if content else None