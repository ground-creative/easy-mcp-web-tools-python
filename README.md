# Eeasy MCP Web Tools

This is a set of web tools to be used with easy mcp server.<br>
https://github.com/ground-creative/easy-mcp-python

## Capabilities

- Perform google searches
- Scrape a given url (ask the agent to scrape one url at a time)

## Installation

1. Clone the repository from the root folder of the easy mcp installation:

```
git clone https://github.com/ground-creative/easy-mcp-web-tools-python.git app
```

2. Install requirements:

```
pip install -r app/requirements.txt
```

3. Create `access_keys.json` file in storage folder with your access keys:

```
[
    "myaccesskey",
    "anotheraccesskey"
]
```

4. Run the server:

```
# Run via fastapi wrapper
python3 run.py -s fastapi
```
