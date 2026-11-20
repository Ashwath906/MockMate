
from pathlib import Path
from langchain.tools import tool


# ==================================================
# WORKSPACE CONFIGURATION
# ==================================================

WORKSPACE = Path("workspace").resolve()


# ==================================================
# WORKSPACE SECURITY
# ==================================================

def get_safe_path(filename: str) -> Path:
    """
    Allow file access only inside workspace/.

    Reject:
    - Empty filenames
    - Parent directory traversal
    - Absolute paths outside workspace
    - Windows absolute paths outside workspace
    - Symlink paths escaping workspace
    """

    if not isinstance(filename, str) or not filename.strip():
        raise ValueError("Filename cannot be empty.")

    raw_path = Path(filename.strip())

    # Reject absolute paths, including Windows-style paths.
    if raw_path.is_absolute() or raw_path.drive:
        raise ValueError(
            "Access denied: Absolute paths are not allowed."
        )

    # Resolve the final path to prevent directory traversal.
    file_path = (WORKSPACE / raw_path).resolve()

    # Ensure the final resolved path is inside workspace.
    if not file_path.is_relative_to(WORKSPACE):
        raise ValueError(
            "Access denied: Path is outside workspace."
        )

    return file_path


# ==================================================
# APPROVAL HANDLING
# ==================================================

def request_approval(action: str, filename: str) -> bool:
    """Request explicit approval before destructive operations."""

    print("\n========== APPROVAL REQUIRED ==========")
    print(f"Action: {action}")
    print(f"File: {filename}")

    print("\n1. Approve")
    print("2. Reject")

    choice = input("Choose (1/2): ").strip().lower()

    if choice in ("1", "yes", "approve"):
        print("Operation approved.")
        return True

    print("Operation rejected.")
    print("Original file remains unchanged.")

    return False


# ==================================================
# SAVE FILE TOOL
# ==================================================

@tool
def save_file(filename: str, content: str) -> str:
    """
    Save a file inside workspace/.

    If the file already exists, request approval before
    overwriting it. Rejecting leaves the original unchanged.
    """

    try:

        file_path = get_safe_path(filename)

        if file_path.exists():

            if not file_path.is_file():
                return "Error: Target is not a regular file."

            approved = request_approval(
                "Overwrite existing file",
                filename,
            )

            if not approved:
                return "File overwrite rejected."

        # Create directories only after path validation.
        file_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        # Verify the resolved path again before writing.
        file_path = get_safe_path(filename)

        if file_path.exists() and not file_path.is_file():
            return "Error: Target is not a regular file."

        file_path.write_text(
            content,
            encoding="utf-8",
        )

        return f"File saved successfully: {filename}"

    except (ValueError, OSError) as error:

        return f"Error: {error}"


# ==================================================
# DELETE FILE TOOL
# ==================================================

@tool
def delete_file(filename: str) -> str:
    """
    Delete a file inside workspace/ only after approval.
    """

    try:

        file_path = get_safe_path(filename)

        if not file_path.is_file():
            return "Error: File does not exist or is not a regular file."

        approved = request_approval(
            "Delete file",
            filename,
        )

        if not approved:
            return "File deletion rejected."

        # Verify path again before deleting.
        file_path = get_safe_path(filename)

        if not file_path.is_file():
            return "Error: File no longer exists."

        file_path.unlink()

        return f"File deleted successfully: {filename}"

    except (ValueError, OSError) as error:

        return f"Error: {error}"
