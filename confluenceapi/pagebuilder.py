from jinja2 import Template
import pandas as pd


class ConfluencePageBuilder(object):
    
    
    def __init__(self):
        self.html = ""
        
        
    def add_title(self, title, heading="h1"):
        t = Template("""
        <{{ heading }}>{{ title }}</{{ heading }}>
        """)
        self.html += t.render(title=title, heading=heading)
    
    
    def add_new_line(self):
        self.html += "<br></br>"
        
        
    def add_table(self, df):
        assert isinstance(df, pd.DataFrame), "df should be a pandas data frame object"
        self.html += df.to_html()
    
    
    def add_chart(self, df, graph_type, title=None):
        t = Template("""
        <ac:structured-macro ac:name="chart">
            {% if title %}<ac:parameter ac:name="title">{{ title }}</ac:parameter>{% endif %}
            <ac:parameter ac:name="type">{{ graph_type }}</ac:parameter>
            <ac:rich-text-body>{{ html_df }}</ac:rich-text-body>
        </ac:structured-macro>
        """)
        self.html += t.render(title=title, html_df=df.to_html(), graph_type=graph_type)
    
    
    def add_warning(self, text, warning_type="warning", title=None, icon=True):
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
        assert isinstance(code, str), "code should be a string representing the code to display"
        assert isinstance(title, str) or title is None, "title should be a string representing the title for the codeblock to display"
        assert isinstance(theme, str) or theme is None, "theme should be a string representing the theme to display the codeblock in"
        assert isinstance(linenumbers, bool), "linenumbers should be a bool representing whether or not to disply the codeblack with line numbers or not"
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
        t = Template("""
        <ac:link><ri:user ri:username="{{ username }}"/></ac:link>
        """)
        self.html += t.render(username=username)
    
    
    def add_page_link(self, page, space):
        t =  Template("""
        <ac:link><ri:page ri:space-key="{{ space }}" ri:content-title="{{ page }}"/></ac:link>
        """)
        self.html += t.render(page=page, space=space)
        
    
    def add_pdf_preview(self, filename):
        t = Template("""
        <ac:structured-macro ac:name="viewpdf">
          <ac:parameter ac:name="name"><ri:attachment ri:filename="{{ filename }}"/></ac:parameter>
        </ac:structured-macro>
        """)
        self.html += t.render(filename=filename)
        
    def add_table_of_contents(self, style="disc", outline=False, printable=True, 
                              max_level=7, indent="0px", min_level=1,
                              exclude="", toc_type="list", include=".*"):
    
        t = Template("""
        <ac:structured-macro ac:name="toc">
          <ac:parameter ac:name="printable">{{ printable }}</ac:parameter>
          <ac:parameter ac:name="style">{{ style }}</ac:parameter>
          <ac:parameter ac:name="maxLevel">{{ max_level }}</ac:parameter>
          <ac:parameter ac:name="indent">{{ indent }}</ac:parameter>
          <ac:parameter ac:name="minLevel">{{ min_level }}</ac:parameter>
          <ac:parameter ac:name="exclude">{{ exclude }}</ac:parameter>
          <ac:parameter ac:name="type">{{ toc_type }}</ac:parameter>
          <ac:parameter ac:name="outline">{{ outline }}</ac:parameter>
          <ac:parameter ac:name="include">{{ include }}</ac:parameter>
        </ac:structured-macro>
        """)
        self.html += t.render(style=style, outline=outline, printable=printable, 
                              max_level=max_level, indent=indent, min_level=min_level,
                              exclude=exclude, toc_type=toc_type, include=include)
        
    def add_custom_html(self, html):
        self.html += html
    
    
    def restart(self):
        self.html = ""
    
    
    def render(self):
        return self.html