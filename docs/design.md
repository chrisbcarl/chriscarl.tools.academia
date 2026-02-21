academia, need to make the questions/hw/todo section accumulator
lecture/notes generator, etc.
I NEED THIS.
academia manifest of classes and semeseters and state

commands
```bash
academia config add  # interactive
academia config default year=2026 semester=Spring "institution=San Jose State University" institution_abbrev=SJSU
academia config add department=Hello number=World year=1971 title=dev
academia config set cmpe-180c year=2025 --inactive


# makes new files
academia new init cmpe-180c
academia new lecture cmpe-180c --overwrite
academia new note cmpe-180c --overwrite


academia collect hw ideas  # collects HW, Ideas for the most recent week
```

state:
current: {
    'classes': {
        'cmpe-180c': 0
        'cmpe-180a': 1
        'math-161b': 2
    },
    'institution': 'SJSU',
    'year': 2026,
    'semester': Fall
}
classes: [
    {
        dep: CMPE
        class: 180C
        section: 02
        title: Operating Systems
        instructor: Dr. Something Other
        institution: SJSU
        year: 2026
        semester: Spring/Fall
    }
]


# NOTE:
- development began at Fri Feb 20 13:56:03
- I'm writing this now at 20:17. thanks to this spec I was able to pump out exactly what I needed and (somewhat) quickly.