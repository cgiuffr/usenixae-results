input_dir             = '<your_input_directory_here>'
input_instances       = [] # List of instances
appendix_url_prefix   = '<your_url_here>'
accepted_htmls        = [] # List of accepted-papers HTML files
accepted_match_all    = True # for off-cycle submissions
paper_url_prefix      = '<your_url_here>'
paper_url_xpath_query = '<your_xpath_query_here>'

output_files           = '<your_files_here>' # .csv and .yaml files supported

# Formatting
input_csv_fmt         = '{instance}-data.csv'
input_pdf_fmt         = '{instance}-final{id}.pdf'
paper_search_fmt      = '"{title}" site:{paper_url_prefix}'
output_fields         = {'title' : 1, 'badges' : 3, 'artifact_url' : 2, 'appendix_url' : -1, 'paper_url' : -1}

csv_delimiter         = ','
csv_quotechar         = '"'
csv_force_delimiter   = True
yaml_indent           = 4
out_lf                = '\n'
out_unknown           = '???'
out_encoding          = 'utf-8'
in_encoding           = 'utf-8'