def generate_html_log(response_data):
    styles = """
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #f4f4f4;
            color: #333;
        }
        .container {
            width: 80%;
            margin: auto;
            overflow: hidden;
        }
        header {
            background: #50b3a2;
            color: #fff;
            padding-top: 30px;
            min-height: 70px;
            border-bottom: #e8491d 3px solid;
        }
        header a {
            color: #ffffff;
            text-decoration: none;
            text-transform: uppercase;
            font-size: 16px;
        }
        header ul {
            padding: 0;
            margin: 0;
            list-style: none;
            overflow: hidden;
        }
        header li {
            float: left;
            display: inline;
            padding: 0 20px 0 20px;
        }
        header #branding {
            float: left;
        }
        header #branding h1 {
            margin: 0;
        }
        header nav {
            float: right;
            margin-top: 10px;
        }
        header .highlight, header .current a {
            color: #e8491d;
            font-weight: bold;
        }
        header a:hover {
            color: #ffffff;
            font-weight: bold;
        }
        .log-entry {
            background-color: #e7ffe7;
            padding: 10px;
            margin-bottom: 10px;
            border-left: 6px solid #2ecc71;
        }
        .error-entry {
            background-color: #ffebeb;
            padding: 10px;
            margin-bottom: 10px;
            border-left: 6px solid #e74c3c;
        }
    </style>
    """

    html_log = f"<html><head><title>Log Output</title>{styles}</head><body>"
    html_log += "<header><div class='container'><h1>Log Output</h1></div></header>"
    html_log += "<div class='container'>"

    if 'log' in response_data:
        log_entries = response_data['log'].split('\n')
        for entry in log_entries:
            if entry.strip():
                html_log += f"<div class='log-entry'>{entry}</div>"

    if 'errors' in response_data and response_data['errors'].strip():
        html_log += f"<div class='error-entry'>{response_data['errors']}</div>"

    html_log += "</div></body></html>"
    return html_log