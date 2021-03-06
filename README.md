# confluenceapi
[![GitHub release](https://img.shields.io/github/release/ghandic/confluenceapi.svg)](http://github.com/ghandic/confluenceapi/releases) [![License](https://img.shields.io/badge/License-MIT_License-green.svg)](http://github.com/ghandic/confluenceapi/)

A python package for connecting to conluence API

## Installation
```bash
pip install git+https://github.com/ghandic/confluenceapi.git
```


## Demo environment
You can test out this package using a Jupyter notebook and Confluence running in Docker by running the following:

Make sure you create a folder on your desktop called confluence or change where the volume will be stored (by changing ~/Desktop/confluence to your required folder)

```bash
docker run -v ~/Desktop/confluence:/var/atlassian/application-data/confluence --name="confluence" -d -p 8090:8090 -p 8091:8091 atlassian/confluence-server

docker-ip() {
	docker inspect --format '{{ .NetworkSettings.IPAddress }}' "$@"
}

export CONFLUENCE_IP=`docker-ip confluence`

docker run -d -p 8888:8888 --name notebook -e CONFLUENCE_IP=$CONFLUENCE_IP -v ~:/home/jovyan/work jupyter/scipy-notebook start-notebook.sh --NotebookApp.token=''
```


Examples:
--------

[See the full set of notebook examples](examples)

```python
# Assuming you have used the docker environment stated above you should be able to get the server ip as we added it to the environment variables inside the docker container. We also know what port the confluence container is running on (8090)

import os
import pandas as pd
from confluenceapi import Confluence, ConfluencePageBuilder

conf_server = os.environ['CONFLUENCE_IP'] + ':8090'
credentials = ('admin', 'Password123')

# Creating a dummy dataframe for later
df = pd.DataFrame({'2006': [100, 200, 50], '2007': [300, 400, 200]},
                  index=['Salmon', 'Herring', 'Shrimp'])

# Create a confluence object ready to submit requests 
lc = Confluence(conf_server, credentials)

# Add a blank page to confluence
lc.add_page('Page about DS', 'Data Science')

# Create a confluence page builder to develop a page
cp = ConfluencePageBuilder()

# Build a page with a title, toc, note, codeblock, table and a chart then tag myself (admin)
cp.add_title("My title", "h2")
cp.add_table_of_contents()
cp.add_warning("Oh no, the cat is out of the bag!", "note", "cat bag")
cp.add_code_block("import pandas as pd", language="python", theme="midnight")
cp.add_title("My graph", "h3")
cp.add_chart(df, 'area')
cp.add_new_line()
cp.add_table(df)
cp.add_custom_html("The page was last updated by:")
cp.add_tag_user("admin")

# Now update the confluence page with the built page
lc.update_page('Page about DS', 'Data Science', cp.render())

# Restart a ConfluencePageBuilder object (clears the html)
cp.restart()
# Get the current content of a page
current_content = lc.get_page_contents('Page about DS', 'Data Science')
# Add some new content and update the page
cp.add_custom_html(current_content)
cp.add_new_line()
cp.add_warning("We just appended this warning!", "warning")
lc.update_page('Page about DS', 'Data Science', cp.render())

# Update a page with raw HTML
lc.update_page('Page about DS', 'Data Science', '<h1 style="color:red;">This is a new title</h1>')

# Delete a page
lc.delete_page('Page about DS', 'Data Science')

# Add attachment to page
lc.upload_attachment('demo.txt', 'Page about DS', 'Data Science', 'First upload!')

# Update attachment on page
lc.update_attachment('demo.txt', 'Page about DS', 'Data Science', 'Second upload!')

# Delete an attachment on page
lc.delete_attachment('demo.txt', 'Page about DS', 'Data Science')
```

Hints:
------

**Tagging users in your html body:**

```python
# Lets say you want to tag Joe Bloggs with username bloggsj

lc.update_page('Page about DS', 'Data Science', '''
<h1 style="color:red;">This is a new title</h1>
<br></br>
<ac:link>
	<ri:user ri:username="bloggsj"/>
</ac:link>
''')
```


**Linking to relative pages:**

```python
# Lets say you want to link to a page called 'Page about DS 2' which is inside the same space

lc.update_page('Page about DS', 'Data Science', '''
<h1 style="color:red;">This is a new title</h1>
<br></br>
<ac:link>
	<ri:page ri:content-title="Page about DS 2"/>
</ac:link>
''')
```


**Linking to pages in other spaces:**

```python
# Lets say you want to link to a page called 'Page not about DS' which is in the space 'Not Data Science' (which has key NDS)

lc.update_page('Page about DS', 'Data Science', '''
<h1 style="color:red;">This is a new title</h1>
<br></br>
<ac:link>
	<ri:page ri:space-key="NDS" ri:content-title="Page not about DS"/>
</ac:link>
''')
```


**Adding emoticons:**

```python
# Lets you have a health check of your servers and you create a dataframe with information about them

df = pd.DataFrame({
    'Server name':['server x','server y','server z'],
    'Free disk space':[0.2,0.9,0.5]
})

def add_emotion(x):
    
    if x < 0.4:
        return '<ac:emoticon ac:name="sad" />'
    elif x >= 0.4 and x < 0.6:
        return '<ac:emoticon ac:name="smile" />'
    else:
        return '<ac:emoticon ac:name="laugh" />'

df['Status'] = df['Free disk space'].apply(lambda x: add_emotion(x))

df.set_index('Server name', inplace=True)

lc.update_page('Page about DS', 'Data Science', df.to_html(escape=False))
```


**Using macros:**

```python
# Let's add a warning message using the warning macro

lc.update_page('Page about DS', 'Data Science', '''
<h1 style="color:red;">This is a new title</h1>
<br></br>
<ac:structured-macro ac:name="warning">
<ac:rich-text-body>
<p> Oh no, the cat is out of the bag!</p>
</ac:rich-text-body>
</ac:structured-macro>
''')
```

Note: to see more examples of builing macros check out [this confluence page](https://confluence.atlassian.com/display/CONF55/Working+with+Macros)

**Creating graphs:**

```python
# Let's add a graph of fish sales for 2006, 2007
df = pd.DataFrame({'name':['Salmon', 'Herring', 'Shrimp'],
                   '2006': [100, 200, 50],
                   '2007': [300, 400, 200]})
df.set_index(['name'], inplace=True)

graph_type = 'bar' # Can be 'line', 'pie', 'bar', 'area'
title = 'Fish Sold'

lc.update_page('Page about DS', 'Data Science', '''
<ac:structured-macro ac:name="chart">
<ac:parameter ac:name="title">''' + title + '''</ac:parameter>
<ac:parameter ac:name="type">''' + graph_type + '''</ac:parameter>
<ac:rich-text-body>"''' + df.to_html() + '''
</ac:rich-text-body>
</ac:structured-macro>
''')
```

For more ideas see the [confluence api docs](https://confluence.atlassian.com/doc/confluence-storage-format-790796544.html)
