---
header-includes: |
title: >
  NOTE
subtitle:
author: AUTHOR <EMAIL>
toc: true
geometry:
    - "margin=0.25in"
    # - landscape
template: "math"  # "chicago" "math"
# ieee
abstract: NOTE for DEPARTMENT NUMBER at INSTITUTION_ABBREV instructed by Dr. INSTRUCTOR in SEMESTER YEAR.
keywords: midterm, final, exam
# custom
doublespaced: false
course: INSTITUTION_ABBREV YEARSEMESTER_SHORT - DEPARTMENT NUMBER - TITLE
authors:
    - name: AUTHOR
      email: EMAIL
      institution: INSTITUTION
      location: San Jose, CA, United States of America
      occupation: Masters of Science in Computer Engineering Student
---

<!--
Updates:
    DATE TIME - HOMEWORK - initial commit

Examples:
    md2pdf "DOCUMENT_FILEPATH" `
        -o "DOCUMENT_DIRPATH/render" -ss -alc

    pandoc "DOCUMENT_FILEPATH" `
        --from=gfm --to=pdf --standalone --mathjax `
        --resource-path "DOCUMENT_DIRPATH" `
        --output "DOCUMENT_DIRPATH/DOCUMENT_FILENAME.pdf"
-->


# Introduction - Ch. 1


## Overview
- Problem / Requirements: What is the thing "Y" that you're actually solving? 30000 ft level description.
- Given / Presumptions: You have tools "A", "B", "C" already discovered, these are the pieces of the puzzle available to solve the problem.
- Answer / Solutions: Invent an "X" - a thing that uses "A" + "B" in a novel way that achieves "Y"


## Glossary / Terms:
- *term*: definitin or illustration


## Concepts:
- elaborate
- on
- the
- solution


## Examples / Questions:
- A multiple choice question should be responded to in-line.
    - a) `[ ]` A only;
    - b) `[x]` B only;
    - c) `[ ]` A and B;
    - d) `[ ]` something else;
- An essay type question
    - can have user response

        > with quotes if needed

        Standalone and indented is perfectly fine

        ```python
        print('hello world')
        ```

    - can have an LLM repsonse

        > with quotes if needed
        >> [chat link](https://www.example.com)

        Standalone and indented is perfectly fine

        ```python
        print('hello world')
        ```


