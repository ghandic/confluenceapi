import os
import requests
import json
import pandas as pd


class Confluence(object):
    
    """
    Example:
    --------
    
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
        
        # Add attachment to page
        lc.upload_attachment('demo.txt', 'Page about DS', 'Data Science', 'First upload!')
        
        # Update attachment on page
        lc.update_attachment('demo.txt', 'Page about DS', 'Data Science', 'Second upload!')
        
        # Delete an attachment on page
        lc.delete_attachment('demo.txt', 'Page about DS', 'Data Science')
    """
    
    
    def __init__(self, server, auth):
        """
        Parameters:
        -----------
            
            server: string, where the server is running eg: 172.17.0.2:8090
            auth: tuple of length 2, (username, password)
        
        """
        
        assert isinstance(auth, tuple) and len(auth) is 2, 'auth must be a tuple, (user, password)'
        assert isinstance(server, str), 'server must be a string to where the server is running'
        
        self.url = "http://{server}/rest/api/content".format(server=server)
        self.headers = {'Accept':'application/json', 'Content-Type':'application/json'}
        self.auth = auth
        
        self.__verify_user()

        
    def __verify_user(self):
        
        response = requests.get(url=self.url + '/search?cql=user=' + self.auth[0], headers=self.headers, auth=self.auth)
        if response.status_code != 200:
            print("Couldn't connect to Confluence API with those credentials or server address")
    
        
    def delete_page(self, page_name, space_name):
        """
        Parameters:
        -----------
            
            page_name: str, the title of the page
            space_key: str, the space key where the page is stored
            
        """
        
        assert isinstance(page_name, str), 'title should be the title of a page within the space defined'
        assert isinstance(space_name, str), 'space_name should be the space name where the page is stored'
        
        pageid = self._get_pageid(page_name, space_name)
        
        response = requests.delete(url=self.url + '/' + str(pageid), headers=self.headers, auth=self.auth)
        return response
    
    
    def update_page(self, page_name, space_name, body):
        """
        Parameters:
        -----------
            
            page_name: str, the title of the page
            space_key: str, the space key where the page is stored
            body: str, a string full of html to populate the page with
        """
        
        assert isinstance(page_name, str), 'title should be the title of a page within the space defined'
        assert isinstance(space_name, str), 'space_name should be the space name where the page is stored'
        assert isinstance(body, str), 'body should be a string full of html to populate the page with'
        
        pageid = self._get_pageid(page_name, space_name)
        
        page_info = self._get_version(pageid)
        page_info_dict = json.loads(page_info.text)

        new_data = {
            'id': pageid,
            'type':'page',
            'title': page_info_dict['title'],
            'space': {'key':page_info_dict['_expandable']['space'].rsplit('/', 1)[-1]},
            'body': {"storage":{"value":body,"representation":"storage"}},
            'version':{'number':page_info_dict['version']['number']+1}
        }
        data = json.dumps(new_data)
        
        response = requests.put(url=self.url + '/' + str(pageid), headers=self.headers, auth=self.auth, data=data)
        return response
    
    
    def add_table_to_page(self, page_name, space_name, df):
        """
        Parameters:
        -----------
            
            page_name: str, the title of the page
            space_key: str, the space key where the page is stored
            df: DataFrame, dataframe to populate the page with
        """
        
        assert isinstance(page_name, str), 'title should be the title of a page within the space defined'
        assert isinstance(space_name, str), 'space_name should be the space name where the page is stored'
        assert isinstance(df, pd.DataFrame), 'df should be a dataframe to populate the page with'
        
        # Pandas will truncate after 50 chars if this isnt in
        with pd.option_context('display.max_colwidth', -1):
            output = df.to_html()
        
        return self.update_page(page_name, space_name, output)
        
        
    def upload_attachment(self, filepath, page_name, space_name, comment=None):
        """
        Parameters:
        -----------
            
            filepath: str, the path to where the file is stored
            page_name: str, the title of the page
            space_key: str, the space key where the page is stored
            comment: str, (optional) a comment to accompany the attachment
            
        """
        
        assert isinstance(page_name, str), 'title should be the title of a page within the space defined'
        assert isinstance(space_name, str), 'space_name should be the space name where the page is stored'
        assert isinstance(filepath, str), 'filepath should be the path to where the file is stored locally'
        assert isinstance(comment, str) or comment is None, 'comment must be a string or None'
        
        pageid = self._get_pageid(page_name, space_name)
        files = {'file': open(filepath, 'rb')}
        data = {}
        headers={"X-Atlassian-Token": "nocheck"}
        
        if comment:
            data = {"comment":comment}
        
        response = requests.post(url=self.url + '/' + str(pageid) + '/child/attachment',
                                 headers=headers, auth=self.auth, files=files, data=data)
        
        return response
    
    
    def update_attachment(self, filepath, page_name, space_name, comment=None):
        """
        Parameters:
        -----------
            
            filepath: str, the path to where the file is stored
            page_name: str, the title of the page
            space_key: str, the space key where the page is stored
            comment: str, (optional) a comment to accompany the attachment update
            
        """
        
        assert isinstance(page_name, str), 'title should be the title of a page within the space defined'
        assert isinstance(space_name, str), 'space_name should be the space name where the page is stored'
        assert isinstance(filepath, str), 'filepath should be the path to where the file is stored locally'
        assert isinstance(comment, str) or comment is None, 'comment must be a string or None'
        
        attachment_name = os.path.basename(filepath)
        attachmentid = self._get_attachmentid(attachment_name, page_name, space_name)
        pageid = self._get_pageid(page_name, space_name)
        
        files = {'file': open(filepath, 'rb')}
        data = {}
        headers={"X-Atlassian-Token": "nocheck"}
        
        if comment:
            data = {"comment":comment}
        
        response = requests.post(url=self.url + '/' + str(pageid) + '/child/attachment/' + attachmentid + '/data',
                                 headers=headers, auth=self.auth, files=files, data=data)
        
        return response
    
    def delete_attachment(self, attachment_name, page_name, space_name):
        """
        Parameters:
        -----------
            
            filepath: str, the path to where the file is stored
            page_name: str, the title of the page
            space_key: str, the space key where the page is stored
            
        """
        
        assert isinstance(page_name, str), 'title should be the title of a page within the space defined'
        assert isinstance(space_name, str), 'space_name should be the space name where the page is stored'
        assert isinstance(attachment_name, str), 'attachment_name should be the name of the attachemt to delete'
        
        attachmentid = self._get_attachmentid(attachment_name, page_name, space_name)
        response = requests.delete(url=self.url + '/' + attachmentid, headers=self.headers, auth=self.auth)
        
        return response
    
    
    def _get_version(self, pageid):
        """
        Parameters:
        -----------
            
            pageid: int, the page id for the confluence page
            
        """
        
        assert isinstance(pageid, int), 'pageid should be an integer which corresponds to a page on the confluence server'

        response = requests.get(url=self.url + '/' + str(pageid) + '?expand=version', headers=self.headers, auth=self.auth)
        return response

    
    def _get_pageid(self, page_name, space_name):
        """
        Parameters:
        -----------
            
            page_name: str, the title of the page
            space_key: str, the space key where the page is stored
            
        """
        
        assert isinstance(page_name, str), 'title should be the title of a page within the space defined'
        assert isinstance(space_name, str), 'space_name should be the space name where the page is stored'
        
        space_key = self._get_space_key(space_name)

        response = requests.get(url=self.url + '?title=' + page_name.replace(' ', '%20') + '&spaceKey='+ space_key + '&expand=body.storage', headers=self.headers, auth=self.auth)
        pageid = json.loads(response.text)['results'][0]['id']
        
        return int(pageid)
    
    
    def _get_space_key(self, space_name):
        """
        Parameters:
        -----------
            
            space_name: str, the space name you want the key for
            
        """
        
        assert isinstance(space_name, str), 'space_name should be the space name where the page is stored'
        
        space_name_replaced = space_name.replace(' ', '%20')
        
        response = requests.get(url=self.url + '/search?cql=space.title%20%7E%20"' + space_name_replaced + '"&limit=1', headers=self.headers, auth=self.auth)
        space_name = json.loads(response.text)['results'][0]['_expandable']['space'].rsplit('/', 1)[-1]
    
        return space_name
        
        
    def _get_attachmentid(self, attachment_name, page_name, space_name):
        """
        Parameters:
        -----------
            
            attachment_name: str, the name of the file attachment
            page_name: str, the title of the page
            space_key: str, the space key where the page is stored
            
        """
        
        assert isinstance(page_name, str), 'title should be the title of a page within the space defined'
        assert isinstance(space_name, str), 'space_name should be the space name where the page is stored'
        assert isinstance(attachment_name, str), 'attachment_name should be a file name that is stored in the page and space'
        
        pageid = self._get_pageid(page_name, space_name)
        
        response = requests.get(url=self.url + '/' + str(pageid) + '/child/attachment',
                     headers=self.headers, auth=self.auth)
        
        for result in json.loads(response.text)['results']:
            if result['title'] == attachment_name:
                return result['id']
        else:
            print('No attachment found')
        
