from jinja2 import Template
import pandas as pd


class ConfluencePageBuilder(object):
    
    
    def __init__(self):
        self.html = ""
        
        
    def add_title(self, title, heading="h1"):
        """
            Parameters:
            -----------
            
            title: string, the title to add
            heading: string, the heading type (h1,h2,h3....h7)
        """
        assert isinstance(title, str), "title should be a string representating the title to be added"
        assert isinstance(heading, str), "heading should be a string representating html heading tag, one of ('h1','h2','h3'....'h7')"

        t = Template("""
        <{{ heading }}>{{ title }}</{{ heading }}>
        """)
        self.html += t.render(title=title, heading=heading)
    
    
    def add_new_line(self):
        self.html += "<br></br>"
        
        
    def add_table(self, df, escape=False):
        """
            Parameters:
            -----------
            
            df: DataFrame, dataframe to populate the page with
            escape: bool, Whether to escape from html (allows html in df to be rendered)
        """
        assert isinstance(df, pd.DataFrame), "df should be a pandas data frame object"
        
        # Pandas will truncate after 50 chars if this isnt in
        with pd.option_context('display.max_colwidth', -1):
            self.html += df.to_html(escape=escape)
    
    
    def add_chart(self, df, graph_type, title=None):
        """
            Parameters:
            -----------
            
            df: DataFrame, dataframe to populate the chart with
            title: string, the title for the chart
            graph_type: string, the graph type can be one of 'bar', 'pie', 'area' or 'line'
        """
        assert isinstance(df, pd.DataFrame), "df should be a pandas data frame object"
        assert isinstance(graph_type, str) and graph_type in ['bar', 'pie', 'line', 'area'], "graph_type should be a string of either 'bar', 'pie', 'line' or 'area'"
        assert isinstance(title, str) or title is None, "title should be a string representating the title for the graph"
                          
        t = Template("""
        <ac:structured-macro ac:name="chart">
            {% if title %}<ac:parameter ac:name="title">{{ title }}</ac:parameter>{% endif %}
            <ac:parameter ac:name="type">{{ graph_type }}</ac:parameter>
            <ac:rich-text-body>{{ html_df }}</ac:rich-text-body>
        </ac:structured-macro>
        """)
        self.html += t.render(title=title, html_df=df.to_html(), graph_type=graph_type)
    
    
    def add_warning(self, text, warning_type="warning", title=None, icon=True):
        """
            Parameters:
            -----------
            
            text: string, the text to put into the warning
            warning_type: string, the warning_type for the macro, can be one of 'warning', 'note', 'tip' or 'info'
            title: string, the title for the warning
            icon: bool, whether to display an icon on the macro or not
        """
        assert warning_type in ['warning', 'note', 'tip', 'info'], 'warning_note can only take the forms of "note", "tip", "info" and "warning"'
        assert isinstance(title, str) or title is None, "title should be a string representing the title for the warning macro to display"
        assert isinstance(icon, bool), "title should be a bool representing whether to display an icon on the macro or not"
        
        t = Template("""
        <ac:structured-macro ac:name="{{ warning_type }}">
        {% if title %}<ac:parameter ac:name="title">{{ title }}</ac:parameter>{% endif %}
        {% if icon == false%}<ac:parameter ac:name="icon">false</ac:parameter>{% endif %}
        <ac:rich-text-body>{{ text }}</ac:rich-text-body>
        </ac:structured-macro>
        """)
        self.html += t.render(text=text, warning_type=warning_type, icon=icon, title=title)
        
        
    def add_code_block(self, code, title=None, theme=None, linenumbers=False,
                       language=None, collapse=False):
        """
            Parameters:
            -----------
            
            code: string, the code to put into the code block
            title: string, the title for the code block
            theme: string, the theme for the code block
            linenumbers: bool, whether or not to display the codeblock with line numbers or not
            language: string, the language for the code block to apply syntax highlighting to
            collapse: bool, whether or not to collapse the codebock on init
        """
        
        assert isinstance(code, str), "code should be a string representing the code to display"
        assert isinstance(title, str) or title is None, "title should be a string representing the title for the codeblock to display"
        assert isinstance(theme, str) or theme is None, "theme should be a string representing the theme to display the codeblock in"
        assert isinstance(linenumbers, bool), "linenumbers should be a bool representing whether or not to display the codeblock with line numbers or not"
        assert isinstance(language, str) or language is None, "language should be a string representing the language of the codeblock to display"
        assert isinstance(collapse, bool), "collapse should be a bool representing whether or not to collapse the codebock on init"

        t = Template("""
        <ac:structured-macro ac:name="code">
        {% if title %}<ac:parameter ac:name="title">{{ title }}</ac:parameter>{% endif %}
        {% if theme %}<ac:parameter ac:name="theme">{{ theme }}</ac:parameter>{% endif %}
        {% if linenumbers == true %}<ac:parameter ac:name="linenumbers">true</ac:parameter>{% endif %}
        {% if language %}<ac:parameter ac:name="language">{{ language }}</ac:parameter>{% endif %}
        {% if collapse == true %}<ac:parameter ac:name="collapse">true</ac:parameter>{% endif %}
          <ac:plain-text-body><![CDATA[{{ code }}]]></ac:plain-text-body>
        </ac:structured-macro>
        """)
        self.html += t.render(code=code, title=title, theme=theme, linenumbers=linenumbers,
                             language=language, collapse=collapse)
    
    
    def add_tag_user(self, username):
        """
            Parameters:
            -----------
            
            username: string, the username to tag
        """
        assert isinstance(username, str), "username should be a string representing the username you wish to tag"
        t = Template("""
        <ac:link><ri:user ri:username="{{ username }}"/></ac:link>
        """)
        self.html += t.render(username=username)
    
    
    def add_page_link(self, page, space):
        """
            Parameters:
            -----------
            
            page: string, the page to link to within the given space
            space: string, the space link to for the given page
        """
        assert isinstance(page, str), "page should be a string representing the page to link to within the given space"
        assert isinstance(space, str), "space should be a string representing the space link to for the given page"
        
        t =  Template("""
        <ac:link><ri:page ri:space-key="{{ space }}" ri:content-title="{{ page }}"/></ac:link>
        """)
        self.html += t.render(page=page, space=space)
        
    
    def add_pdf_preview(self, filename):
        """
            Parameters:
            -----------
            
            filename: string, the filename of the pdf to view (must be attached to the page to preview)
            """
        assert isinstance(filename, str), "filename should be a string representing the pdf file you wish to preview"
        t = Template("""
        <ac:structured-macro ac:name="viewpdf">
          <ac:parameter ac:name="name"><ri:attachment ri:filename="{{ filename }}"/></ac:parameter>
        </ac:structured-macro>
        """)
        self.html += t.render(filename=filename)
        
    def add_table_of_contents(self, toc_type="list", min_level=1, max_level=7,
                              style="disc", outline=False, indent="0px",
                              exclude=None, include=None, printable=True):
        """
            Parameters:
            -----------
            
            toc_type: string, possible options are 'list' or 'flat'.
            min_level: int, The highest heading level to start your TOC  list.  For example, entering 2 will include levels 2, and lower, headings, but will not include level 1 headings.
            max_level: int, The lowest heading level to include.  For example, entering 2 will include levels 1 and 2, but will not include level 3 headings and below.
            style: string, The style of the toc list bullet points can be any valid CSS style eg 'circle', 'disc', 'square', 'decimal', 'lower-alpha, 'lower-roman', 'upper-roman'
            outline: bool, whether to apply outline numbering to your headings, for example: 1.1, 1.2, 1.3.
            indent: string, Sets the indent for a list according to CSS quantities. Entering 10px will successively indent heading groups by 10px. For example, level 1 headings will be indented 10px and level 2 headings will be indented an additional 10px.
            exclude: string, Filter headings to enclude according to specific criteria
            include: string, Filter headings to include according to specific criteria.
            printable: bool, Whether to allow the TOC to be visible when you print the page.
        """
        assert isinstance(toc_type, str) and toc_type in ['list', 'flat'], "toc_type should be a string representing the table of contents type, can be 'list' or 'flat'"
        assert isinstance(min_level, int), "min_level should be a integer representing the highest heading level to start your TOC  list"
        assert isinstance(max_level, int), "max_level should be a integer representing the lowest heading level to include in your TOC  list"
        assert isinstance(style, str), "style should be a string representing the CSS style of the list bullets eg 'circle', 'disc', 'square', 'decimal', 'lower-alpha, 'lower-roman', 'upper-roman'"
        assert isinstance(outline, bool), "outline should be a boolean value representing whether or not to apply outline numbering to your headings, for example: 1.1, 1.2, 1.3."
        assert isinstance(indent, str), "indent should be a string representing the pixel indent for each line"
        assert isinstance(exclude, str) or exclude is None, "exclude should be a string representing the regex criteria to filter the headings on which to exclude"
        assert isinstance(include, str) or include is None, "include should be a string representing the regex criteria to filter the headings on which to include"
        assert isinstance(printable, bool), "printable should be a boolen value representing whether to allow the TOC to be visible when you print the page."
        
        t = Template("""
        <ac:structured-macro ac:name="toc">
          <ac:parameter ac:name="printable">{{ printable }}</ac:parameter>
          <ac:parameter ac:name="style">{{ style }}</ac:parameter>
          <ac:parameter ac:name="maxLevel">{{ max_level }}</ac:parameter>
          <ac:parameter ac:name="indent">{{ indent }}</ac:parameter>
          <ac:parameter ac:name="minLevel">{{ min_level }}</ac:parameter>
          {% if exclude %}<ac:parameter ac:name="exclude">{{ exclude }}</ac:parameter>{% endif %}
          <ac:parameter ac:name="type">{{ toc_type }}</ac:parameter>
          <ac:parameter ac:name="outline">{{ outline }}</ac:parameter>
          {% if include %}<ac:parameter ac:name="include">{{ include }}</ac:parameter>{% endif %}
        </ac:structured-macro>
        """)
        self.html += t.render(style=style, outline=outline, printable=printable, 
                              max_level=max_level, indent=indent, min_level=min_level,
                              exclude=exclude, toc_type=toc_type, include=include)
        
    def add_custom_html(self, html):
        """
            Parameters:
            -----------
            
            html: string, the custom html you wish to add to the page
            """
        assert isinstance(html, str), "html should be a string representing the custom html you wish to add to the page"
        self.html += html
    
    
    def restart(self):
        self.html = ""
    
    
    def render(self):
        return self.html
