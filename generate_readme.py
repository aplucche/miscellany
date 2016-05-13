"""
    generate_readme.py
    ~~~~~~~~~~~~~~~~~~
    Generates readme from docstrings in repo.  Docstrings follow format shown
    here
    Usage::
        run in repo directory

"""
import os
import re

header = '''
# Miscellaneous Python and D3 scripts for data collection, manipulation and visualization

### Contents
'''
docstrings = []
for file in os.listdir('./'):
    if re.search('\.py$', file):
        with open(file, 'rb') as f:
            block = ''
            writing = False
            for line in f:
                if line.strip() == "\"\"\"" and writing == True:
                    break
                if writing == True:
                    block += line
                if line.strip() == "\"\"\"" and writing == False:
                    writing = True
            docstrings.append(block)

def translate_docstring_to_markdown(docstring):
    docstring = re.sub('~+', '<pre><code>',docstring)
    if '<pre><code>' in docstring:
        docstring += '</code></pre>'
    return docstring

docstrings = [translate_docstring_to_markdown(d) for d in docstrings]

sections = [header] + docstrings
sections = [section.strip() for section in sections]
sections = '\n\n'.join(sections)

with open('readme.md', 'wb') as f:
    f.write(sections)