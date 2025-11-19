import urllib.request
import urllib.error
import json
import os
import re
import argparse
from html.parser import HTMLParser

BASE_URL = "https://adventofcode.com"
try:
    with open('headers.json', 'r') as f:
        HEADERS = json.load(f)
except FileNotFoundError:
    print("Error: headers.json not found. Please create it with your cookies.")
    exit(1)
except json.JSONDecodeError:
    print("Error: headers.json is not valid JSON.")
    exit(1)

class AoCParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []
        self.current_part = None
        self.capture = False
        self.in_code = False
        self.in_pre = False
        self.code_buffer = []
        self.list_stack = []
        self.href = None

    def handle_starttag(self, tag, attrs):
        if tag == 'article':
            for k, v in attrs:
                if k == 'class' and 'day-desc' in v:
                    self.capture = True
                    self.current_part = {'title': None, 'body': []}
        
        if not self.capture:
            return

        if tag == 'h2':
            pass
        elif tag == 'p':
            pass
        elif tag == 'em':
            if self.in_code:
                self.code_buffer.append('<em>')
            else:
                self.current_part['body'].append('**')
        elif tag == 'code':
            self.in_code = True
            self.code_buffer = []
        elif tag == 'pre':
            self.in_pre = True
            self.current_part['body'].append('\n```\n')
        elif tag == 'ul':
            self.list_stack.append('ul')
        elif tag == 'li':
            self.current_part['body'].append('\n' + '  ' * len(self.list_stack) + '- ')
        elif tag == 'a':
            for k, v in attrs:
                if k == 'href':
                    self.href = v
                    if self.href.startswith('/'):
                        self.href = BASE_URL + self.href
            self.current_part['body'].append('[')
        elif tag == 'span':
            pass

    def handle_endtag(self, tag):
        if tag == 'article':
            self.capture = False
            if self.current_part:
                self.current_part['body'] = "".join(self.current_part['body']).strip()
                self.parts.append(self.current_part)
                self.current_part = None
        
        if not self.capture:
            return

        if tag == 'h2':
            pass
        elif tag == 'p':
            self.current_part['body'].append('\n\n')
        elif tag == 'em':
            if self.in_code:
                self.code_buffer.append('</em>')
            else:
                self.current_part['body'].append('**')
        elif tag == 'code':
            self.in_code = False
            code_content = "".join(self.code_buffer)
            
            if self.in_pre:
                clean_content = re.sub(r'<[^>]+>', '', code_content)
                self.current_part['body'].append(clean_content)
            elif code_content.startswith('<em>') and code_content.endswith('</em>') and code_content.count('<em>') == 1:
                inner = code_content[4:-5]
                self.current_part['body'].append(f'`{inner}`')
            else:
                clean_content = re.sub(r'<[^>]+>', '', code_content)
                self.current_part['body'].append(f'`{clean_content}`')
        elif tag == 'pre':
            self.in_pre = False
            self.current_part['body'].append('```\n\n')
        elif tag == 'ul':
            if self.list_stack:
                self.list_stack.pop()
        elif tag == 'li':
            pass
        elif tag == 'a':
            self.current_part['body'].append(f']({self.href})')
            self.href = None

    def handle_data(self, data):
        if self.capture:
            if self.lasttag == 'h2':
                match = re.search(r'--- (.+) ---', data)
                if match:
                    self.current_part['title'] = match.group(1)
                else:
                    self.current_part['title'] = data.strip()
                return

            if self.in_code:
                self.code_buffer.append(data)
            else:
                text = re.sub(r'\s+', ' ', data)
                self.current_part['body'].append(text)

def make_request(url):
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req) as response:
            return response.read().decode('utf-8')
    except urllib.error.HTTPError as e:
        print(f"Error fetching {url}: {e}")
        return None

def fetch_problem(year, day):
    url = f"{BASE_URL}/{year}/day/{day}"
    print(f"Fetching problem {url}...")
    html = make_request(url)
    if html:
        parser = AoCParser()
        parser.feed(html)
        return parser.parts
    return []

def fetch_input(year, day):
    url = f"{BASE_URL}/{year}/day/{day}/input"
    print(f"Fetching input {url}...")
    return make_request(url)

def save_input(year, day, data):
    folder = f"{year}/data"
    if not os.path.exists(folder):
        os.makedirs(folder)
    
    filename = f"{folder}/advent_{day:02d}.txt"
    with open(filename, 'w') as f:
        f.write(data)
    print(f"Saved input to {filename}")

def create_notebook(year, day):
    folder = str(year)
    if not os.path.exists(folder):
        os.makedirs(folder)
    
    filename = f"{folder}/day_{day:02d}.ipynb"
    
    if os.path.exists(filename):
        print(f"Notebook {filename} already exists. Skipping creation.")
        return

    parts = fetch_problem(year, day)
    if not parts:
        print("Could not fetch problem content.")
        return

    part1 = parts[0]
    title = part1['title']
    body = part1['body']
    
    # Fetch input
    input_data = fetch_input(year, day)
    if input_data:
        save_input(year, day, input_data)

    # Create cells
    cells = []
    
    # Title Cell
    if title:
        problem_url = f"{BASE_URL}/{year}/day/{day}"
        cells.append({
            "cell_type": "markdown",
            "metadata": {},
            "source": [f"### [{title}]({problem_url})"]
        })
    
    # Part 1 Content Cell
    cells.append({
        "cell_type": "markdown",
        "metadata": {},
        "source": [body]
    })

    nb_content = {
        "cells": cells,
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3"
            },
            "language_info": {
                "codemirror_mode": {
                    "name": "ipython",
                    "version": 3
                },
                "file_extension": ".py",
                "mimetype": "text/x-python",
                "name": "python",
                "nbconvert_exporter": "python",
                "pygments_lexer": "ipython3",
                "version": "3.8.5"
            }
        },
        "nbformat": 4,
        "nbformat_minor": 4
    }
    
    with open(filename, 'w') as f:
        json.dump(nb_content, f, indent=1)
    print(f"Created {filename}")

def add_part_2(year, day):
    folder = str(year)
    filename = f"{folder}/day_{day:02d}.ipynb"
    
    if not os.path.exists(filename):
        print(f"Notebook {filename} does not exist. Cannot add Part 2.")
        return

    parts = fetch_problem(year, day)
    if len(parts) < 2:
        print("Part 2 not found in content.")
        return

    part2 = parts[1]
    body = part2['body']

    with open(filename, 'r') as f:
        try:
            nb_content = json.load(f)
        except json.JSONDecodeError:
            print(f"Corrupt notebook {filename}.")
            return
            
    # Append Part 2 cells
    nb_content['cells'].append({
        "cell_type": "markdown",
        "metadata": {},
        "source": ["### Part two"]
    })
    
    nb_content['cells'].append({
        "cell_type": "markdown",
        "metadata": {},
        "source": [body]
    })
    
    with open(filename, 'w') as f:
        json.dump(nb_content, f, indent=1)
    print(f"Added Part 2 to {filename}")

def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest='command', required=True)

    # Create command
    create_parser = subparsers.add_parser('create', help='Create a new notebook for a specific day')
    create_parser.add_argument('year', type=int, help='Year (e.g., 2022)')
    create_parser.add_argument('day', type=int, help='Day (1-25)')

    # Add Part 2 command
    add_part2_parser = subparsers.add_parser('part-two', help='Add Part 2 to an existing notebook')
    add_part2_parser.add_argument('year', type=int, help='Year (e.g., 2022)')
    add_part2_parser.add_argument('day', type=int, help='Day (1-25)')

    args = parser.parse_args()

    if args.command == 'create':
        create_notebook(args.year, args.day)
    elif args.command == 'part-two':
        add_part_2(args.year, args.day)

if __name__ == "__main__":
    main()
