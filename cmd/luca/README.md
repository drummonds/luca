# Luca CLI

This is going to be a test bed for the parser.

## Parser Implementation

This project uses [participle](https://github.com/alecthomas/participle) to parse text files containing structured entries. Participle is a parser library for Go that makes it easy to create parsers using struct tags.

### Example File Format

To see tested file formats look at the test code which is test to parse

For illustration the parser will handle text files with the following structure:

entry "My First Entry" {
date: 2024-03-20
tags: ["personal", "notes"]
content: """
This is a multi-line
content block.
"""
}
entry "Another Entry" {
date: 2024-03-21
tags: ["work"]
content: "Single line content"
}