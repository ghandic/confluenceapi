# confluenceapi
A python package for connecting to conluence API


## Demo environment
You can test out this package using a Jupyter notebook and Confluence running in Docker by running the following:

Make sure you create a folder on your desktop called confluence or change where the volume will be stored (by changing ~/Desktop/confluence to your required folder)

```
docker run -v ~/Desktop/confluence:/var/atlassian/application-data/confluence --name="confluence" -d -p 8090:8090 -p 8091:8091 atlassian/confluence-server

docker-ip() {
	docker inspect --format '{{ .NetworkSettings.IPAddress }}' "$@"
}

export CONFLUENCE_IP=`docker-ip confluence`

docker run -d -p 8888:8888 --name notebook -e CONFLUENCE_IP=$CONFLUENCE_IP -v ~:/home/jovyan/work jupyter/scipy-notebook start-notebook.sh --NotebookApp.token=''


```


Example:
--------
```
# Assuming you have used the docker environment stated above you should be able to get the server ip as we added it to the environment variables inside the docker container. We also know what port the confluence container is running on (8090)

import os
import pandas as pd
from confluenceapi import Confluence

conf_server = os.environ['CONFLUENCE_IP'] + ':8090'
credentials = ('admin', 'Password123')

# Create a confluence object ready to submit requests 
lc = Confluence(conf_server, credentials)

# Update a page with raw HTML
lc.update_page('Page about DS', 'Data Science', '<h1 style="color:red;">This is a new title</h1>')

# Add a table to a page from pandas
df = pd.get_dummies(pd.Series(list('abcd')))
lc.add_table_to_page('Page about DS', 'Data Science', df)

# Delete a page
lc.delete_page('Page about DS', 'Data Science')
```

Hints:
------

**Tagging users in your html body:**

```
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

```
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

```
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

```
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


For more ideas see the [confluence api docs](https://confluence.atlassian.com/doc/confluence-storage-format-790796544.html)