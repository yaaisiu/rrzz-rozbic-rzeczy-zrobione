import re
from typing import List, Dict, Any, NamedTuple

class Note(NamedTuple):
    content: str
    indentation: int
    tags: List[str]
    line_number: int

def get_indentation(line: str) -> int:
    """Calculates the indentation level of a line based on leading spaces."""
    return len(line) - len(line.lstrip(' '))

def parse_line(line: str, line_number: int) -> Note:
    """Parses a single line into a Note object."""
    indentation = get_indentation(line)
    content = line.strip()
    tags = re.findall(r"#(\w+)", content)
    # Remove tags from content
    content_without_tags = re.sub(r"\s*#\w+", "", content).strip()
    return Note(
        content=content_without_tags,
        indentation=indentation,
        tags=tags,
        line_number=line_number
    )

def parse_file(file_path: str) -> List[Note]:
    """Reads a file and parses it into a list of Note objects."""
    notes: List[Note] = []
    with open(file_path, 'r') as f:
        for i, line in enumerate(f):
            if line.strip():  # Ignore empty lines
                notes.append(parse_line(line.rstrip('\n'), i + 1))
    return notes

if __name__ == '__main__':
    # Example usage:
    notes = parse_file('gtd.txt')
    for note in notes:
        print(note) 