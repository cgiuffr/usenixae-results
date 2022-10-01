# usenixae-results
USENIX AE results script

Dependencies:
* Python 3.6+
* lxml (https://pypi.org/project/lxml)
* pyaml (https://pypi.org/project/PyYAML)

Usage:

```shell
$ cp params_default.py params.py # and edit params.py
$ ./results.py
```

Example HotCRP workflow to export USENIX Security'22 artifact results to secartifacts:
* For each instance at `https://sec22{summer|fall|winter}ae.usenix.hotcrp.com/search?q=`:
  * View options -> select only the field with the final stable URL -> Redisplay.
  * Select all submissions with badges -> Download -> Documents -> Final versions.
  * Select all submissions with badges -> Download -> Paper information -> CSV.
* Download all the HTMLs at `https://www.usenix.org/conference/usenixsecurity22/{summer|fall|winter}-accepted-papers`:
  * Save them as `{summer|fall|winter}-accepted-papers.html`.
* Copy all the downloaded CSV, PDF, and HTML files to some input directory.
* Create a `params.py` file from `params_default.py` file.
* Edit `params.py` as follows:
  * `input_dir`: Enter the input directory above.
  * `input_instances`: `['sec22summerae', 'sec22fallae', 'sec22winterae']`.
  * `appendix_url_prefix` : `https://secartifacts.github.io/usenixsec2022/appendix-files/`.
  * `accepted_htmls` : `['summer-accepted-papers.html', 'fall-accepted-papers.html', 'winter-accepted-papers.html']`.
  * `accepted_match_all` : `True` (enable off-cycle submissions).
  * `paper_url_prefix`: `'https://www.usenix.org'`.
  * `paper_url_xpath_query` : `'//a[contains(lower-case(text()),lower-case("{title}"))]/@href'`.
  * `output_files`: `['results.yaml', 'results.csv']`.
* Run `./results.py` to produce the desired YAML output.
* Check and manually correct any `???` entry (likely with mismatching paper titles) in the output file.
