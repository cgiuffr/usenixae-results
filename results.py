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

csvout = None
csvout_source = None


def row_fields_to_results(row_fields, out):
    if os.path.splitext(out.name)[1] == '.yaml':
        yaml.dump([row_fields], out, sort_keys=False,
                  indent=params.yaml_indent, line_break=params.out_lf, width=sys.maxsize, encoding=params.out_encoding, allow_unicode=True)
        out.write(params.out_lf)
    else:
        global csvout, csvout_source
        if csvout_source != out:
            csvout = None
        if not csvout:
            if params.csv_force_delimiter:
                out.write(f'SEP={params.csv_delimiter}{params.out_lf}')
            csvout = csv.writer(out,
                                delimiter=params.csv_delimiter, quotechar=params.csv_quotechar, lineterminator=params.out_lf)
            csvout_source = out
            csvout.writerow(row_fields.keys())  # header
        csvout.writerow(row_fields.values())


def row_to_paper_url(instance, row, htmls, title):
    urls = []
    for html in htmls:
        tokens = html.xpath(params.paper_url_xpath_query.format(title=title))
        urls.extend(tokens)
    if len(urls) > 1:
        return params.out_unknown
    return str(f'{params.paper_url_prefix}{urls[0].strip()}')


def row_to_appendix_url(instance, row):
    id = row[0]
    input_pdf = params.input_pdf_fmt.format(instance=instance, id=id)
    if not os.path.exists(f'{params.input_dir}/{input_pdf}'):
        return params.out_unknown
    return str(f'{params.appendix_url_prefix}{input_pdf}')


def row_to_results(instance, htmls, row, out):
    row_fields = dict()
    title = row[params.output_fields['title']]
    print(f' - Processing row: {title}')

    for key, col in params.output_fields.items():
        if col >= 0:
            value = row[col].strip()
            if key == 'artifact_url' and (value == 'N/A' or value == ''):
                continue
            row_fields[key] = value
            continue
        if key == 'paper_url':
            row_fields[key] = row_to_paper_url(instance, row, htmls, title)
        elif key == 'appendix_url':
            row_fields[key] = row_to_appendix_url(instance, row)
        else:
            row_fields[key] = params.out_unknown
    row_fields_to_results(row_fields, out)


def instance_to_results(instance, htmls, out):
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
        row_to_results(instance, htmls, row, out)
    csvfile.close()


# init
htmls = [lxml.html.parse(f'{params.input_dir}/{html}')
         for html in params.accepted_htmls]
index = 0

# lower-case support in xpath 1.0
xpatch_ci_hack = r'translate(\1, "ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz")'
tmp = re.sub(r'lower-case\((text\(\))\)', xpatch_ci_hack,
             params.paper_url_xpath_query)
tmp = re.sub(r'lower-case\(([^)]*)\)', xpatch_ci_hack, tmp)
params.paper_url_xpath_query = tmp

# for each output file
for out_file in params.output_files:
    out = open(out_file, 'w', encoding=params.in_encoding)
    # for each instance
    for instance in params.input_instances:
        instance_htmls = htmls if params.accepted_match_all else [htmls[index]]
        instance_to_results(instance, instance_htmls, out)
        index += 1
    out.close()

sys.exit(0)