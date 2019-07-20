#!/usr/bin/env python
# -*- coding: utf-8 -*-

import glob
import json
from multiprocessing import Pool

import html2text
import javalang


def _clean_javadoc(doc):
    if not doc:
        return ''
    doc_string = ' '.join(
        [l.strip() for l in doc.replace(' * ', '').replace(' *', '').splitlines()[1:-1] if len(l.strip()) > 0])
    h = html2text.HTML2Text()
    return h.handle(doc_string)


def _get_permission(v):
    if type(v) is javalang.tree.Literal:
        return {
            'qualifier': v.qualifier,
            'member': str(v.value).replace('"', ''),
        }
    else:
        return {
            'qualifier': v.qualifier,
            'member': v.member,
        }


def _get_methods_with_permissions(class_file):
    with open(class_file, mode='r') as zz:
        methods = {}
        try:
            tree = javalang.parse.parse(zz.read())
        except javalang.parser.JavaSyntaxError:
            return {}
        if not tree.package:
            return {}
        package = tree.package.name
        for t in tree.types:
            class_name = t.name
            for m in t.methods:
                method_full_name = '{}.{}.{}'.format(package, class_name, m.name)
                methods[method_full_name] = {
                    'documentation': _clean_javadoc(m.documentation),
                    'file': class_file,
                    'line': m.position.line,
                    'permissions': []
                }
                for a in m.annotations:
                    if a.name == 'RequiresPermission':
                        if type(a.element) is not list:
                            methods[method_full_name]['permissions'].append(_get_permission(a.element))
                        else:
                            for e in a.element:
                                # print(type(e.value))
                                if type(e.value) is javalang.tree.ElementArrayValue:
                                    for v in e.value.values:
                                        try:
                                            methods[method_full_name]['permissions'].append(_get_permission(v))
                                        except:
                                            print(v)
                                            print(type(v))
                                else:  # type(e.value) is javalang.tree.MemberReference:
                                    methods[method_full_name]['permissions'].append(_get_permission(e.value))

                if len(methods[method_full_name]['permissions']) == 0:
                    methods.pop(method_full_name, None)
        return methods


def extract_required_permissions_from_sources(src_path):
    java_files = []

    for f in glob.iglob('{}/**/*.java'.format(src_path), recursive=True):
        java_files.append(f)

    with Pool(2) as p:
        results = p.map(_get_methods_with_permissions, java_files)

    methods = {}
    for r in results:
        if r:
            for k, v in r.items():
                if k not in methods:
                    methods[k] = v

    return methods


if __name__ == "__main__":
    import sys

    aosp = '/tmp/aosp/telephony/java/'
    json_output = 'methods.json'
    methods = extract_required_permissions_from_sources(aosp)
    with open(json_output, mode='w') as output:
        json.dump(methods, output, sort_keys=True, indent=2)

    # if len(sys.argv) != 3:
    #     print('Usage: python extract_required_permissions.py [path to the Java source dir] [output file path]')
    # methods = extract_required_permissions_from_sources(sys.argv[1])
    # with open(sys.argv[2], mode='w') as output:
    #     json.dump(methods, output, sort_keys=True, indent=2)
