# Advent of Code

Python solutions to the problems of the <a href="https://adventofcode.com/">Advent of Code</a>.

## Notebook helper script

Use `aoc_to_notebook.py` to create starter notebooks that already contain the
puzzle text and puzzle input. The script expects a `headers.json` file in the
repository root that includes your Advent of Code session cookie, for example:

```json
{
  "Cookie": "session=YOUR_SESSION_ID"
}
```

Run the script with Python:

```bash
# Create a notebook for a specific puzzle
python aoc_to_notebook.py create 2024 1

# Append the Part Two description
python aoc_to_notebook.py part-two 2024 1
```
