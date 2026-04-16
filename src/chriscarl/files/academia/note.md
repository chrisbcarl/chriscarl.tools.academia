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
        --from=gfm --to=pdf --standalone --mathjax --toc-depth=4 `
        --resource-path "DOCUMENT_DIRPATH" `
        --output "DOCUMENT_DIRPATH/DOCUMENT_FILENAME.pdf"
-->


# Introduction - Ch. 1


## Overview / Introductions:
- Problem / Requirements: What is the thing "Y" that you're actually solving? 30000 ft level description.
- Given / Presumptions: You have tools "A", "B", "C" already discovered, these are the pieces of the puzzle available to solve the problem.
- Answer / Solutions: Invent an "X" - a thing that uses "A" + "B" in a novel way that achieves "Y"


## Glossary / Terms:
- *term*: definitin or illustration


## Systems / Concepts:
- elaborate
- on
- the
    - compare/contrast: strat1, strat2, strat3

        |          |strategy1|strategy2|strategy3|
        |---       |---      |---      |---      |
        |dimension1|---      |---      |---      |
        |dimension2|---      |---      |---      |
        |dimension3|---      |---      |---      |
        |dimension4|---      |---      |---      |
        |dimension5|---      |---      |---      |
- solution


## Examples / Questions:

### Multiple Choice
- M1. A multiple choice question should be responded to in-line.
    - a) `[ ]` A only;
    - b) `[x]` B only;
    - c) `[ ]` A and B;
    - d) `[ ]` something else;

### Fill In the Blank
- B1. Question text with `______` used for the blank and <u>underlined</u> for the answer.

### Essay
#### E1: Question Topic
An essay type question with the prompt here.

- my response:

    Standalone and indented is perfectly fine

    > with quotes if needed

    ```python
    print('hello world')
    ```

- LLM-v0-Thinking response:

    Standalone and indented is perfectly fine

    > with quotes if needed
    >> [chat link](https://www.example.com)

    ```python
    print('hello world')
    ```


