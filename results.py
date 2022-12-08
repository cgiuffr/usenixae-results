#!/usr/bin/python3

import sys
import os

import csv
import yaml
import lxml.html
import re

try:
    import params
except ImportError:
    print("Please create params.py based on params_default.py first.")
    sys.exit(1)


def xpath_query_preprocess(query):
    # lower-case support in xpath 1.0
    if query is None:
        return query
    xpatch_ci_hack = r'translate(\1, "ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz")'
    query = re.sub(r'lower-case\((text\(\))\)', xpatch_ci_hack, query)
    query = re.sub(r'lower-case\(([^)]*)\)', xpatch_ci_hack, query)
    return query


def xpath_param_escape(param):
    # escape special characters in xpath
    if param is None:
        return param
    special_chars = "<>&'\""
    replacement = " "
    for char in special_chars:
        if char in param:
            param = param.replace(char, replacement)
    return param


def yaml_dump(obj, out):
    yaml.dump(obj, out, sort_keys=False,
              indent=params.yaml_indent, line_break=params.out_lf, width=sys.maxsize, encoding=params.out_encoding, allow_unicode=True)


def entries_to_output(entries, out):
    if os.path.splitext(out.name)[1] == '.yaml':
        if not params.yaml_spaced_entries:
            yaml_dump(entries, out)
            return
        for entry in entries:
            yaml_dump([entry], out)
            out.write(params.out_lf)
    else:
        if params.csv_force_delimiter:
            out.write(f'SEP={params.csv_delimiter}{params.out_lf}')
        csvout = csv.writer(out,
                            delimiter=params.csv_delimiter, quotechar=params.csv_quotechar, lineterminator=params.out_lf)
        if len(entries) > 0:
            csvout.writerow(entries[0].keys())  # header
        for row in entries:
            csvout.writerow(row.values())


def row_to_paper_title(instance, row, htmls, title):
    if params.paper_title_xpath_query is None:
        return title
    titles = []
    for html in htmls:
        etitle = xpath_param_escape(title)
        tokens = html.xpath(params.paper_title_xpath_query.format(title=etitle))
        titles.extend(tokens)
    if len(titles) != 1:
        return params.out_unknown
    return titles[0].strip()


def row_to_paper_url(instance, row, htmls, title):
    urls = []
    for html in htmls:
        etitle = xpath_param_escape(title)
        tokens = html.xpath(params.paper_url_xpath_query.format(title=etitle))
        urls.extend(tokens)
    if len(urls) != 1:
        return params.out_unknown
    return str(f'{params.paper_url_prefix}{urls[0].strip()}')


def row_to_appendix_url(instance, row):
    id = row[0]
    input_pdf = params.input_pdf_fmt.format(instance=instance, id=id)
    if not os.path.exists(f'{params.input_dir}/{input_pdf}'):
        return params.out_unknown
    return str(f'{params.appendix_url_prefix}{input_pdf}')


def row_to_entry(instance, htmls, row):
    entry = dict()
    title = row[params.output_fields['title']]
    print(f' - Processing row: {title}')

    for key, col in params.output_fields.items():
        if key == 'title':
            entry[key] = row_to_paper_title(instance, row, htmls, title)
        elif key == 'paper_url':
            entry[key] = row_to_paper_url(instance, row, htmls, title)
        elif key == 'appendix_url':
            entry[key] = row_to_appendix_url(instance, row)
        elif col >= 0:
            value = row[col].strip()
            if key == 'artifact_url' and (value == 'N/A' or value == ''):
                continue
            entry[key] = value
            continue
        else:
            entry[key] = params.out_unknown
    return entry


def instance_to_entries(instance, htmls, entries):
    print(f'\nProcessing instance: {instance}')
    csvfilename = params.input_csv_fmt.format(instance=instance)
    csvfile = open(f'{params.input_dir}/{csvfilename}',
                   'r', encoding=params.out_encoding)
    datareader = csv.reader(csvfile,
                            delimiter=params.csv_delimiter, quotechar=params.csv_quotechar)

    is_header = True
    for row in datareader:
        if is_header:
            is_header = False
            continue
        entry = row_to_entry(instance, htmls, row)
        entries.append(entry)
    csvfile.close()


# init
htmls = [lxml.html.parse(f'{params.input_dir}/{html}')
         for html in params.accepted_htmls]
index = 0

# preprocess xpath queries
params.paper_url_xpath_query = xpath_query_preprocess(
    params.paper_url_xpath_query)
params.paper_title_xpath_query = xpath_query_preprocess(
    params.paper_title_xpath_query)

# grab entries for all the instances
entries = []
for instance in params.input_instances:
    instance_htmls = htmls if params.accepted_match_all else [htmls[index]]
    instance_to_entries(instance, instance_htmls, entries)
    index += 1

# output the entries for all the output files
for out_file in params.output_files:
    out = open(out_file, 'w', encoding=params.in_encoding)
    entries_to_output(entries, out)
    out.close()

sys.exit(0)
