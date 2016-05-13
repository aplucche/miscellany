# Miscellaneous Python and D3 scripts for data collection, manipulation and visualization

### Contents

generate_readme.py
    <pre><code>
    Generates readme from docstrings in repo.  Docstrings follow format shown
    here
    Usage::
        run in repo directory

</code></pre>



meetup.py
    <pre><code>
    Collects streaming meetup.com RSVP data.  Writes frequency count of topics 
    that meetup members are RSVPing to by city/state/country.
    Usage::
    	writes to freq_counts.json in directory where script is run
</code></pre>

Pinterest User Scraper
    <pre><code>
    Get links for all Pinterest boards associated with a user.  Uses selenium to
    account for Pinterest's infinite scrolling
    Usage::
        python pinterest_get_links.py https://www.pinterest.com/aboutdotcom/ >> results.txt
</code></pre>

Pinterest Board Metric Scraper
    <pre><code>
    Get metrics for a list of Pinterest boards provided as a text file with
    one board url per line (as generated by pinterest_get_links.py)
    Usage::
        python pinterest_get_metrics.py input_file.txt results.csv
</code></pre>