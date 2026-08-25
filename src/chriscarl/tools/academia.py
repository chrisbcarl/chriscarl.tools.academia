#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Author:         Chris Carl
Email:          chrisbcarl@outlook.com
Date:           2026-02-20
Description:

tools.academia is a tool which manages notes and academic records related to those notes.

Examples:
    > # configure semester information
    > academia config default year=2026 semester=Spring "institution=San Jose State University" institution_abbrev=SJSU
    > academia config add  # interactive
    > academia config add department=Hello number=World year=1971 title=dev
    > academia config set cmpe-180c year=2025 --inactive

    > # makes new files
    > academia new init cmpe-180c
    > academia new lecture cmpe-180c --overwrite
    > academia new note cmpe-180c --overwrite

    > # collects HW, Ideas for the most recent week
    > academia collect hw ideas

Updates:
    2026-08-24 - tools.academia - added quiz type and simplified index calculation to a func
    2026-08-20 - tools.academia - added hw auto-increment
    2026-08-19 - tools.academia - added HOMEWORK_SHORT, HOMEWORK_NICE to get some auto formatting in the title
    2026-04-13 - tools.academia - added explicit lecture/note
    2026-02-23 - tools.academia - added homework.md and notebook.ipynb
    2026-02-20 - tools.academia - initial commit

TODO:
    - author/email, maybe config
'''

# stdlib imports
from __future__ import absolute_import, print_function, division, with_statement  # , unicode_literals
import os
import sys
import logging
import datetime
from typing import List, Generator, Optional, Dict, Any
from dataclasses import dataclass, field, fields, asdict
from argparse import ArgumentParser
from collections import OrderedDict
import json
import re

# third party imports

# project imports
from chriscarl.core.constants import TEMP_DIRPATH
from chriscarl.core.lib.stdlib.logging import NAME_TO_LEVEL, configure_ez
from chriscarl.core.lib.stdlib.argparse import ArgparseNiceFormat
from chriscarl.core.lib.stdlib.os import abspath, make_dirpath, dirpath, is_file, is_dir, walk_regex
from chriscarl.core.lib.stdlib.io import read_text_file, write_text_file
from chriscarl.core.lib.stdlib.json import read_json, write_json
from chriscarl.core.lib.stdlib.datetime import NOW, get_start_of_week, get_start_of_day, get_end_of_day, from_str as datetime_from_str
from chriscarl.core.lib.stdlib.subprocess import launch_editor
from chriscarl.core.functors.parse.markdown import markdown_to_doclets
from chriscarl.core.types.bool import boolean
from chriscarl.core.types.str import indent
from chriscarl.files import academia_documents

SCRIPT_RELPATH = 'chriscarl/tools/academia.py'
if not hasattr(sys, '_MEIPASS'):
    SCRIPT_FILEPATH = os.path.abspath(__file__)
else:
    SCRIPT_FILEPATH = os.path.abspath(os.path.join(sys._MEIPASS, SCRIPT_RELPATH))  # pylint: disable=no-member
SCRIPT_DIRPATH = os.path.dirname(SCRIPT_FILEPATH)
SCRIPT_NAME = os.path.splitext(os.path.basename(__file__))[0]
THIS_MODULE = sys.modules[__name__]
LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(logging.NullHandler())

# argument defaults
DEFAULT_FIB_INIT = [0, 1]
DEFAULT_OUTPUT_DIRPATH = abspath(TEMP_DIRPATH, 'tools.academia')
DEFAULT_LOG_FILEPATH = abspath(TEMP_DIRPATH, 'tools.academia.log')

# tool constants
DEFAULT_AUTHOR = 'Chris Carl'
DEFAULT_EMAIL = 'chris.carl@sjsu.edu'
DEFAULT_DIRPATH = abspath(os.getcwd())
DEFAULT_CONFIG_FILEPATH = abspath(DEFAULT_DIRPATH, 'tools.academia.cfg')
DEFAULT_DEPARTMENT = 'DEPT'
DEFAULT_NUMBER = '101'
DEFAULT_TITLE = 'Introduction'
SEMESTERS = ['Spring', 'Fall']

DOC_TYPE = ['lecture', 'note', 'init', 'hw', 'ipynb', 'quiz']
COURSE_DIRNAMES = ['assignments', 'exams', 'lectures', 'notes', 'quizes', 'resources']
COLLECT_SECTIONS = {
    'hw': ['hw', 'todo'],
    'ideas': ['ideas', 'sidebar'],
    'glossary': ['glossary', 'terms'],
    'questions': ['questions', 'problems', 'office hours'],
    'quiz': ['quiz'],
}


@dataclass
class Course:
    department: str = DEFAULT_DEPARTMENT
    number: str = DEFAULT_NUMBER
    section: int = 1
    title: str = 'Introduction'
    instructor: str = 'First Last'
    instructor_email: str = 'first.last@inst.edu'
    institution: str = 'San Jose State University'
    institution_abbrev: str = 'SJSU'
    year: int = 1970
    semester: str = 'Fall'
    active: bool = True

    def __repr__(self):
        return '\n'.join(f'{k}: {v}' for k, v in self.to_dict().items())

    def __str__(self):
        return f'Course<{self.department}-{self.number}>({self.semester} {self.year}) - {self.title} [{"" if self.active else "in"}active]'

    @classmethod
    def new(cls, kwargs):
        # type: (Dict[str, Any]) -> Course
        field_names = {fie.name: fie for fie in fields(Course)}
        for key, value in kwargs.items():
            field = field_names[key]
            if field.type is bool:
                value = boolean(value)
            elif isinstance(field.type, type):
                value = field.type(value)
            else:
                raise RuntimeError("impossible! fix Course typing!")
            kwargs[key] = value

        for key, field in field_names.items():
            if key not in kwargs:
                kwargs[key] = field.default

        return cls(**kwargs)

    def to_key(self):
        return f'{self.department}-{self.number}'

    def to_dict(self):
        return asdict(self)

    def set_attribute(self, key, value):
        field_names = {fie.name: fie for fie in fields(self)}
        field = field_names[key]
        if field.type is bool:
            value = boolean(value)
        elif isinstance(field.type, type):
            value = field.type(value)
        else:
            raise RuntimeError("impossible! fix Course typing!")
        setattr(self, key, value)


@dataclass
class Config:
    courses: List[Course] = field(default_factory=lambda: [])
    defaults: Dict[str, Any] = field(default_factory=lambda: {})
    filepath: str = DEFAULT_CONFIG_FILEPATH

    def add_course(self, course):
        # type: (Course) -> None
        course_key = course.to_key()
        try:
            if self.get_course(course_key):
                raise KeyError(f'attempting to add duplicate course! {course}')
        except ValueError:
            pass

        dirbase = os.path.dirname(self.filepath)
        for dirname in COURSE_DIRNAMES:
            make_dirpath(dirbase, course.to_key(), dirname)

        self.courses.append(course)

    def add_interactive(self):
        if not self.courses:
            print('no courses! use the "config add" command!', file=sys.stderr)
            return
        try:
            kwargs = {}
            for field in fields(Course):
                key = field.name
                value = input(f'    {field.name} (ex {field.default!r}): ')
                if not value:
                    value = field.default
                kwargs[key] = value
            course = Course(**kwargs)
            self.add_course(course)
        except KeyboardInterrupt:
            pass

    def add_batch(self, config_tokens):
        # type: (List[str]) -> None
        self.validate_config_tokens(config_tokens)
        kwargs = {}
        for t, config_token in enumerate(config_tokens):
            key, value = config_token.split('=')
            kwargs[key] = value

        course = Course.new(kwargs)
        if any([course.department == DEFAULT_DEPARTMENT, course.number == DEFAULT_NUMBER, course.title == DEFAULT_TITLE]):
            raise ValueError(f"Incomplete course info--cannot keep default department, course, title: {course}\n{indent(repr(course))}!")
        self.add_course(course)

    def print_courses(self):
        print('courses:')
        for c, course in enumerate(self.courses):
            print(f'    {c:02d} - {course}')

    def print_current_courses(self):
        print('current:')
        for c, course in enumerate(self.courses):
            if not course.active:
                continue
            print(f'    {c:02d} - {course}')

    def validate_config_tokens(self, config_tokens):
        # type: (List[str]) -> bool
        field_names = {fie.name: fie for fie in fields(Course)}
        for t, token in enumerate(config_tokens):
            if '=' not in token:
                raise ValueError(f'token {t} {token!r} doesnt have an =, consider using quotes!')
            try:
                key, _ = token.split('=')
            except Exception as ex:
                raise ValueError(f"token {t} {token!r} has too many = characters!") from ex
            if key not in field_names:
                raise KeyError(f'token {t} key {key!r} is not a real Course key!')
        return True

    def get_keys(self):
        # type: () -> List[str]
        lst = [f'{course.department}-{course.number}'.lower() for course in self.courses]
        return lst

    def get_course(self, course_key, active=True):
        # type: (str, bool) -> Course
        course_key_tokens = course_key.split('-')
        if len(course_key_tokens) != 2:
            raise ValueError(f'course key {course_key!r} has too many - characters!')
        department, number = course_key_tokens
        for course in self.courses:
            if active != course.active:
                continue
            if (course.department == department or course.department.lower() == department.lower()) and (course.number == number or course.number.lower() == number.lower()):
                return course
        raise ValueError(f'{"in" if not active else ""}active course {course_key!r} does not exist!')

    def set(self, course_key, config_tokens, active=True):
        # type: (str, List[str], bool) -> None
        self.validate_config_tokens(config_tokens)
        course = self.get_course(course_key, active=active)
        for t, config_token in enumerate(config_tokens):
            key, value = config_token.split('=')
            course.set_attribute(key, value)

    def set_defaults(self, config_tokens):
        self.validate_config_tokens(config_tokens)
        field_names = {fie.name: fie for fie in fields(Course)}
        for t, config_token in enumerate(config_tokens):
            key, value = config_token.split('=')
            field = field_names[key]
            if field.type is bool:
                value = boolean(value)
            elif isinstance(field.type, type):
                value = field.type(value)
            else:
                raise RuntimeError("impossible! fix Course typing!")
            self.defaults[key] = value

    def apply_defaults(self):
        field_names = {fie.name: fie for fie in fields(Course)}
        for name, field in field_names.items():
            if name in self.defaults:
                field.default = self.defaults[name]

    def most_recent_course(self):
        # type: () -> Course|None
        if self.courses:
            most_recent = sorted(self.courses, key=lambda x: (x.year, SEMESTERS.index(x.semester)), reverse=True)[0]
            return most_recent
        return None

    def get_active_courses(self):
        # type: () -> List[Course]
        return [course for course in self.courses if course.active]

    def get_inactive_courses(self):
        # type: () -> List[Course]
        return [course for course in self.courses if not course.active]

    def to_dict(self):
        return asdict(self)

    def save(self, filepath=''):
        write_json(filepath or self.filepath, self.to_dict())

    @classmethod
    def load(cls, filepath=DEFAULT_CONFIG_FILEPATH):
        # type: (str) -> Config
        if is_file(filepath):
            config = read_json(filepath)
            courses = []
            courses.extend(config.get('courses', []))
            courses = [Course(**kwargs) for kwargs in courses]
            defaults = config.get('defaults') or {}
            if not isinstance(defaults, dict):
                raise RuntimeError('did not expect defaults to not be of type dict...')
            cfg = Config(courses=courses, defaults=defaults)
            cfg.filepath = filepath
            return cfg
        return Config()


@dataclass
class Arguments:
    '''
    Document this class with any specifics for the process function.
    '''
    # app
    subcommand: str = ''
    config_mode: str = ''
    course_key: str = ''
    config_tokens: List[str] = field(default_factory=lambda: [])
    inactive: bool = False
    doc_type: str = ''
    date_note: datetime.datetime = NOW
    overwrite: bool = False
    collect_sections: List[str] = field(default_factory=lambda: [])
    date_start: datetime.datetime = NOW
    date_end: datetime.datetime = NOW
    # settings
    config_filepath: str = DEFAULT_CONFIG_FILEPATH
    dirpath: str = DEFAULT_DIRPATH
    # misc
    debug: bool = False
    log_level: str = 'INFO'
    log_filepath: str = DEFAULT_LOG_FILEPATH

    @classmethod
    def add_common_arguments(cls, parser):
        # type: (ArgumentParser) -> ArgumentParser
        settings = parser.add_argument_group('settings')
        settings.add_argument('--config-filepath', type=str, default=DEFAULT_CONFIG_FILEPATH, help='config filepath')
        settings.add_argument('--dirpath', '-o', type=str, default=DEFAULT_DIRPATH, help='where do you want to save any output')

        misc = parser.add_argument_group('misc')
        misc.add_argument('--debug', action='store_true', help='chose to print debug info')
        misc.add_argument('--log-level', type=str, default='INFO', choices=NAME_TO_LEVEL, help='log level?')
        misc.add_argument('--log-filepath', type=str, default=DEFAULT_LOG_FILEPATH, help='log filepath?')

        return parser

    @classmethod
    def argparser(cls):
        # type: () -> ArgumentParser
        current_config = Config.load()
        date_start = get_start_of_day(get_start_of_week())
        date_end = get_end_of_day(NOW)

        parser = ArgumentParser(prog=SCRIPT_NAME, description=__doc__, formatter_class=ArgparseNiceFormat)
        subcommands = parser.add_subparsers(title='subcommand', description='all subcommands', dest='subcommand')

        config = subcommands.add_parser('config', formatter_class=ArgparseNiceFormat, help='configure the semester information')
        config_subcommands = config.add_subparsers(title='config_mode', description='config subcommands', dest='config_mode')
        config_print = config_subcommands.add_parser('print', help='print the config')
        cls.add_common_arguments(config_print)

        config_add = config_subcommands.add_parser('add', help='add courses to the config, interractive if no key=value pairs')
        config_add.add_argument('config_tokens', type=str, nargs='*', help=f'key=value for any of these keys: {[fie.name for fie in fields(Course)]}')
        cls.add_common_arguments(config_add)

        config_set = config_subcommands.add_parser('set', help='set current courses')
        config_set.add_argument('course_key', type=str, choices=current_config.get_keys(), help=f'existing course by "dept-number" as key')
        config_set.add_argument('config_tokens', type=str, nargs='+', help=f'key=value for any of these keys: {[fie.name for fie in fields(Course)]}')
        config_set.add_argument('--inactive', action='store_true', help='search through inactive courses')
        cls.add_common_arguments(config_set)

        config_default = config_subcommands.add_parser('default', help='set global defaults for the courses')
        config_default.add_argument('config_tokens', type=str, nargs='+', help=f'key=value for any of these keys: {[fie.name for fie in fields(Course)]}')
        cls.add_common_arguments(config_default)

        cls.add_common_arguments(config)

        new = subcommands.add_parser('new', formatter_class=ArgparseNiceFormat, help='create new notes/lectures, initialize, etc')
        new.add_argument('doc_type', type=str, choices=DOC_TYPE, help='which type of new document?')
        new.add_argument('course_key', type=str, choices=current_config.get_keys(), help=f'existing course by "dept-number" as key')
        new.add_argument('--date_note', type=datetime_from_str, default=get_start_of_day(NOW), help='date of the note you want to make')
        new.add_argument('--inactive', action='store_true', help='search through inactive courses')
        new.add_argument('--overwrite', action='store_true', help='overwrite existing?')
        cls.add_common_arguments(new)

        collect = subcommands.add_parser(
            'collect', formatter_class=ArgparseNiceFormat, help='accumulate all notes and extract the sections that would be good to view all at once...'
        )
        collect.add_argument('collect_sections', type=str, nargs='+', choices=COLLECT_SECTIONS, help='which sections to collect?')
        collect.add_argument('--date-start', type=datetime_from_str, default=date_start, help='files created on or after this date?')
        collect.add_argument('--date-end', type=datetime_from_str, default=date_end, help='files created on or before this date?')
        collect.add_argument('--inactive', action='store_true', help='search through inactive courses')
        collect.add_argument('--course-key', type=str, choices=current_config.get_keys(), help=f'existing course by "dept-number" as key')
        cls.add_common_arguments(collect)

        return parser

    def process(self):
        make_dirpath(dirpath(self.config_filepath))
        if self.date_end < self.date_start:
            raise ValueError(f'--date-start > --date-end! {self.date_end} > {self.date_start}')
        if self.debug:
            self.log_level = 'DEBUG'
        configure_ez(level=self.log_level, filepath=self.log_filepath)

    @classmethod
    def parse(cls, parser=None, argv=None):
        # type: (Optional[ArgumentParser], Optional[List[str]]) -> Arguments
        parser = parser or cls.argparser()
        ns = parser.parse_args(argv)
        arguments = cls(**(vars(ns)))
        arguments.process()
        return arguments

    def to_dict(self):
        return {fie.name: getattr(self, fie.name) for fie in fields(self)}


def get_number_index_from_dirpath(dirpath):
    # type: (str) -> int
    index = -1
    if is_dir(dirpath):
        directories = [re.search(r'\d+', directory) for directory in os.listdir(dirpath)]
        if directories:
            indicies = [int(directory.group(0)) for directory in directories if directory is not None]
            if indicies:
                index = max(indicies)
    return index



def main():
    # type: () -> int
    parser = Arguments.argparser()
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    args = Arguments.parse(parser=parser)
    cfg = Config.load(filepath=args.config_filepath)
    cfg.apply_defaults()
    if args.debug:
        LOGGER.debug(args.to_dict())
        LOGGER.debug(json.dumps(cfg.to_dict(), indent=2))
    if args.subcommand == 'config':
        if args.config_mode == 'print':
            cfg.print_courses()
            cfg.print_current_courses()
        elif args.config_mode == 'add':
            if args.config_tokens:
                cfg.add_batch(args.config_tokens)
            else:
                cfg.add_interactive()
        elif args.config_mode == 'default':
            cfg.set_defaults(args.config_tokens)
        elif args.config_mode == 'set':
            cfg.set(args.course_key, args.config_tokens, active=not args.inactive)

        cfg.save(filepath=args.config_filepath)

    elif args.subcommand == 'new':
        course = cfg.get_course(course_key=args.course_key, active=not args.inactive)
        course_key = course.to_key()
        # semester = f'{course.year}{course.semester[0].lower()}'
        # course_dirpath = abspath(args.dirpath, semester, course_key)
        course_dirpath = abspath(args.dirpath, course_key)
        if args.doc_type == 'init':
            for basename in COURSE_DIRNAMES:
                new_dirpath = abspath(course_dirpath, basename)
                make_dirpath(new_dirpath)
                LOGGER.info('created "%s"', new_dirpath)
        else:
            SEMESTER_SHORT = course.semester[0].upper()
            DATE = args.date_note.strftime("%Y-%m-%d")
            filename = DATE
            dirname = f'{args.doc_type}s'  # note-s plural
            filename_short = ''
            filename_nice = ''
            index = -1
            if args.doc_type in ['hw', 'ipynb', 'quiz']:
                extension = 'md'
                template = ''
                if args.doc_type == 'quiz':
                    dirname = 'quizes'
                    output_dirpath = abspath(course_dirpath, dirname)
                    index = get_number_index_from_dirpath(output_dirpath) + 1
                    template = read_text_file(academia_documents.FILEPATH_ACADEMIA_QUIZ)
                    filename = f'quiz-{index}'
                    basename = f'{filename}.md'
                else:
                    if args.doc_type == 'hw':
                        template = read_text_file(academia_documents.FILEPATH_ACADEMIA_HOMEWORK)
                    if args.doc_type == 'ipynb':
                        template = read_text_file(academia_documents.FILEPATH_ACADEMIA_NOTEBOOK)
                        extension = 'ipynb'

                    output_dirpath = abspath(course_dirpath, 'assignments')
                    index = get_number_index_from_dirpath(output_dirpath) + 1

                    filename_short = f'HW{index}'
                    filename_nice = f'{course.year}{SEMESTER_SHORT} - {course.institution_abbrev} - {course.department} {course.number} - {filename_short} - {"_".join([ele.lower() for ele in DEFAULT_AUTHOR.split()])}'
                    # YYYYX-INST-DEPT000A-hw0-chris_carl
                    filename = filename_nice.replace(' ', '')
                    basename = f'{filename}.{extension}'
                    dirname = f'assignments/{filename_short.lower()}'
            else:
                if args.doc_type == 'note':
                    template = read_text_file(academia_documents.FILEPATH_ACADEMIA_NOTE)
                elif args.doc_type == 'lecture':
                    template = read_text_file(academia_documents.FILEPATH_ACADEMIA_LECTURE)
                else:
                    raise RuntimeError('we cant be here!')
                basename = f'{filename}.md'

            output_dirpath = abspath(course_dirpath, dirname)
            output_filepath = abspath(output_dirpath, basename)
            tpls = [(k.upper(), v) for k, v in course.to_dict().items()]
            tpls += [
                ('INDEX', index),
                ('AUTHOR', DEFAULT_AUTHOR),
                ('EMAIL', DEFAULT_EMAIL),
                ('SEMESTER_SHORT', SEMESTER_SHORT),
                ('DATE', DATE),
                ('TIME', NOW.strftime('%H:%M')),
                ('HOMEWORK', filename),
                ('HOMEWORK_SHORT', filename_short),
                ('HOMEWORK_NICE', filename_nice),
                ('DOCUMENT_FILEPATH', os.path.relpath(output_filepath, os.getcwd()).replace('\\', '/')),
                ('DOCUMENT_DIRPATH', os.path.relpath(output_dirpath, os.getcwd()).replace('\\', '/')),
                ('DOCUMENT_FILENAME', os.path.splitext(os.path.basename(output_filepath))[0]),
            ]
            kwargs = OrderedDict(sorted(tpls, key=lambda x: len(x[0]), reverse=True))
            for k, v in kwargs.items():
                template = template.replace(k, str(v))

            if is_file(output_filepath) and not args.overwrite:
                raise OSError(f'"{basename}" {args.doc_type} exists for {course}! \n     "{output_filepath}"\n    pass --overwrite')
            make_dirpath(output_dirpath)
            write_text_file(output_filepath, template)
            LOGGER.info('wrote "%s"', output_filepath)
            launch_editor(output_filepath)

    elif args.subcommand == 'collect':
        if not cfg.courses:
            LOGGER.error('cfg hasnt been configured yet at "%s"!', args.config_filepath)
            return 1

        doclets, _, _, _, _ = markdown_to_doclets(academia_documents.FILEPATH_ACADEMIA_NOTE)
        template_content_erase = [doclet.content for doclet in doclets if doclet.section in {'any', 'list'}]
        if args.course_key:
            courses = [cfg.get_course(args.course_key, active=not args.inactive)]
        else:
            courses = cfg.get_inactive_courses() if args.inactive else cfg.get_active_courses()
        accumulator = {}  # type: Dict[str, List[str]]
        for course in courses:
            course_key = course.to_key()
            course_dirpath = abspath(args.dirpath, course_key)
            LOGGER.info('analyzing %s', course)
            if not is_dir(course_dirpath):
                continue
            for filepath in walk_regex(course_dirpath, r'.*\d{4}-\d{1,2}-\d{1,2}.*\.md'):
                mo = re.search(r'(\d{4})-(\d{1,2})-(\d{1,2})', filepath)
                if not mo:
                    raise RuntimeError('this is impossible')
                groups = mo.groups()
                date = datetime.datetime(year=int(groups[0]), month=int(groups[1]), day=int(groups[2]))
                if not (args.date_start <= date and date <= args.date_end):
                    LOGGER.debug('rejecting "%s", !(%s < %s < %s)', filepath, args.date_start.strftime('%Y-%m-%d'), date.strftime('%Y-%m-%d'), args.date_end.strftime('%Y-%m-%d'))
                    continue
                LOGGER.debug('analyzing "%s"', filepath)
                doclets, _, _, _, _ = markdown_to_doclets(filepath)

                for section in args.collect_sections:
                    doclet_idx = -1
                    for term in COLLECT_SECTIONS[section]:
                        if doclet_idx > -1:
                            break
                        for d, doclet in enumerate(doclets):
                            if doclet.section != 'header':
                                continue
                            if term not in doclet.content.lower():
                                continue
                            doclet_idx = d + 1
                            break
                    if doclet_idx == -1:
                        continue

                    accumulate = []

                    doclet = doclets[doclet_idx]
                    while doclet.section != 'header':
                        content = doclet.content
                        for token in template_content_erase:
                            content = content.replace(token, '')
                        content = content.strip()
                        if content:
                            accumulate.append(content)

                        doclet_idx += 1
                        doclet = doclets[doclet_idx]

                    if not accumulate:
                        continue

                    title_text = f'## {course.department}-{course.number}: {course.title}'
                    if section not in accumulator:
                        accumulator[section] = []
                    if title_text not in accumulator[section]:
                        accumulator[section].append(title_text)
                    accumulator[section] += [f'### {date.strftime("%Y-%m-%d")}'] + accumulate

        if not accumulator:
            LOGGER.warning('couldnt find any documents with %s!', args.collect_sections)
        else:
            lines = []
            for key, values in accumulator.items():
                lines.append(f'# {key.upper()}')
                lines.extend(values)
            final_content = '\n\n'.join(lines)
            output_filepath = abspath(args.dirpath, 'ignoreme', f'{"-".join(args.collect_sections)}_{args.date_start.strftime("%Y%m%d")}-{args.date_end.strftime("%Y%m%d")}.md')
            write_text_file(output_filepath, final_content)
            LOGGER.info('wrote "%s"', output_filepath)
            launch_editor(output_filepath)

    return 0


if __name__ == '__main__':
    sys.exit(main())
