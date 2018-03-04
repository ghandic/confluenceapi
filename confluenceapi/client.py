import os
import requests
import json

class Confluence(object):
    
    """
        .. code-block:: python
        
          ## Example
          import os
          from confluenceapi import Confluence

          conf_server = os.environ['CONFLUENCE_IP'] + ':8090'
          credentials = ('admin', 'Password123')

          # Create a confluence object ready to submit requests 
          lc = Confluence(conf_server, credentials)

          # Add a page
          lc.add_page("Page about DS", "Data Science")
        
          # Add a child page to this page
          lc.add_page("New page about DS", "Data Science", "Page about DS", '<h1 style="color:red;">This is a title</h1>')

          # Update a page with raw HTML
          lc.update_page('Page about DS', 'Data Science', '<h1 style="color:red;">This is a new title</h1>')

          # Delete a page
          lc.delete_page('Page about DS', 'Data Science')
        
          # Get the contents of a page
          lc.get_page_contents("Page about DS", "Data Science")
        
          # Add attachment to page
          lc.upload_attachment('demo.txt', 'Page about DS', 'Data Science', 'First upload!')
        
          # Update attachment on page
          lc.update_attachment('demo.txt', 'Page about DS', 'Data Science', 'Second upload!')
        
          # Delete an attachment on page
          lc.delete_attachment('demo.txt', 'Page about DS', 'Data Science')
    """
    
    
    def __init__(self, server, auth):
        """
        Arguments:
            server (str): where the server is running eg: 172.17.0.2:8090
            auth (tuple): tuple of length 2, (username, password)
        
        """
        
        assert isinstance(auth, tuple) and len(auth) is 2, 'auth must be a tuple, (user, password)'
        assert isinstance(server, str), 'server must be a string to where the server is running'
        
        self.server = server
        self.auth = auth
        self.api_url = "http://{server}/rest/api/".format(server=server)
        self.headers = {'Accept':'application/json', 'Content-Type':'application/json'}
        
        self.__verify_user()

        
    def __verify_user(self):
        """Verifies that the username is valid"""
        
        response = requests.get(url=self.api_url + 'content/search?cql=user=' + self.auth[0], 
                                headers=self.headers, auth=self.auth)
        if response.status_code != 200:
            print("Couldn't connect to Confluence API with those credentials or server address")
    
        
    def delete_page(self, page_name, space_name, **kwargs):
        """
        Arguments:
            page_name (str): The title of the page
            space_name (str): The space name where the page is stored

        Returns:
            response (requests.models.Response): The response from the api request

        """
        
        assert isinstance(page_name, str), 'title should be the title of a page within the space defined'
        assert isinstance(space_name, str), 'space_name should be the space name where the page is stored'
        space_name_as_key = kwargs.pop('space_name_as_key', False)
        
        pageid = self._get_pageid(page_name, space_name, space_name_as_key)
        
        response = requests.delete(url=self.api_url + 'content/' + str(pageid), headers=self.headers, auth=self.auth)
        return response
    
    
    def update_page(self, page_name, space_name, body, **kwargs):
        """
        Arguments:
            page_name (str): The title of the page
            space_name (str): The space name where the page is stored
            body (str): A string full of html to populate the page with

        Returns:
            response (requests.models.Response): The response from the api request
                         
        """
        
        assert isinstance(page_name, str), 'title should be the title of a page within the space defined'
        assert isinstance(space_name, str), 'space_name should be the space name where the page is stored'
        assert isinstance(body, str), 'body should be a string full of html to populate the page with'
        space_name_as_key = kwargs.pop('space_name_as_key', False)
        
        pageid = self._get_pageid(page_name, space_name, space_name_as_key)
        
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
        
        response = requests.put(url=self.api_url + 'content/' + str(pageid), headers=self.headers, auth=self.auth, data=data)
        return response
        
        
    def upload_attachment(self, filepath, page_name, space_name, comment=None, **kwargs):
        """
        Arguments:
            filepath (str): The path to where the file is stored
            page_name (str): The title of the page
            space_name (str): The space name where the page is stored
            comment (Optional[str]): A comment to accompany the attachment

        Returns:
            response (requests.models.Response): The response from the api request
            
        """
        
        assert isinstance(page_name, str), 'title should be the title of a page within the space defined'
        assert isinstance(space_name, str), 'space_name should be the space name where the page is stored'
        assert isinstance(filepath, str), 'filepath should be the path to where the file is stored locally'
        assert isinstance(comment, str) or comment is None, 'comment must be a string or None'
        space_name_as_key = kwargs.pop('space_name_as_key', False)
        
        pageid = self._get_pageid(page_name, space_name, space_name_as_key)
        files = {'file': open(filepath, 'rb')}
        data = {}
        headers={"X-Atlassian-Token": "nocheck"}
        
        if comment:
            data = {"comment":comment}
        
        response = requests.post(url=self.api_url + 'content/' + str(pageid) + '/child/attachment',
                                 headers=headers, auth=self.auth, files=files, data=data)
        
        return response
    
    
    def update_attachment(self, filepath, page_name, space_name, comment=None, **kwargs):
        """
        Arguments:
            filepath (str): The path to where the file is stored
            page_name (str): The title of the page
            space_name (str): The space name where the page is stored
            comment (Optional[str]): A comment to accompany the attachment

        Returns:
            response (requests.models.Response): The response from the api request

        """
        
        assert isinstance(page_name, str), 'title should be the title of a page within the space defined'
        assert isinstance(space_name, str), 'space_name should be the space name where the page is stored'
        assert isinstance(filepath, str), 'filepath should be the path to where the file is stored locally'
        assert isinstance(comment, str) or comment is None, 'comment must be a string or None'
        space_name_as_key = kwargs.pop('space_name_as_key', False)
        
        pageid = self._get_pageid(page_name, space_name, space_name_as_key)
        
        attachment_name = os.path.basename(filepath)
        attachmentid = self._get_attachmentid(attachment_name, pageid)
        
        files = {'file': open(filepath, 'rb')}
        data = {}
        headers={"X-Atlassian-Token": "nocheck"}
        
        if comment:
            data = {"comment":comment}
        
        response = requests.post(url=self.api_url + 'content/' + str(pageid) + '/child/attachment/' + attachmentid + '/data',
                                 headers=headers, auth=self.auth, files=files, data=data)
        
        return response
    
    def delete_attachment(self, attachment_name, page_name, space_name, **kwargs):
        """
        Arguments:
            attachment_name (str): The name of the stored attachment
            page_name (str): The title of the page
            space_name (str): The space name where the page is stored

        Returns:
            response (requests.models.Response): The response from the api request
            
        """
        
        assert isinstance(page_name, str), 'title should be the title of a page within the space defined'
        assert isinstance(space_name, str), 'space_name should be the space name where the page is stored'
        assert isinstance(attachment_name, str), 'attachment_name should be the name of the attachemt to delete'
        space_name_as_key = kwargs.pop('space_name_as_key', False)
        
        pageid = self._get_pageid(page_name, space_name, space_name_as_key)
        attachmentid = self._get_attachmentid(attachment_name, pageid)
        response = requests.delete(url=self.api_url + 'content/' + attachmentid, headers=self.headers, auth=self.auth)
        
        return response
    
    
    def _get_version(self, pageid):
        """
        Arguments:
            pageid (int): The page id for the confluence page

        Returns:
            response (requests.models.Response): The response from the api request
            
        """
        
        assert isinstance(pageid, int), 'pageid should be an integer which corresponds to a page on the confluence server'

        response = requests.get(url=self.api_url + 'content/' + str(pageid) + '?expand=version',
                                headers=self.headers, auth=self.auth)
        return response

    
    def _get_pageid(self, page_name, space_name, space_name_as_key):
        """
        Arguments:
            page_name (str): The title of the page
            space_name (str): The space name where the page is stored

        Returns:
            pageid (int): The pageid for the given page_name and space_name
            
        """
        
        assert isinstance(page_name, str), 'title should be the title of a page within the space defined'
        assert isinstance(space_name, str), 'space_name should be the space name where the page is stored'
        
        space_key = self._get_space_key(space_name, space_name_as_key)

        response = requests.get(url=self.api_url + 'content?title=' + page_name.replace(' ', '%20') + '&spaceKey='+ space_key + '&expand=body.storage', headers=self.headers, auth=self.auth)
        
        if len(json.loads(response.text)['results']) is not 0:
            pageid = json.loads(response.text)['results'][0]['id']
            return int(pageid)
        raise ValueError('Page not found, has it been deleted or is it in a differant space?')
    
    
    def _get_space_key(self, space_name, space_name_as_key):
        """
        Arguments:
            space_name (str): The space name you want the key for
            force_space_name (bool): Whether to force using the name as the key

        Returns:
            spacekey (str): The spacekey for the given space_name
            
        """
        
        assert isinstance(space_name, str), 'space_name should be the space name where the page is stored'
        assert isinstance(space_name_as_key, bool), 'space_name_as_key should be a boolean value whether to use the space_name param but pass the key'
        
        if space_name_as_key:
            space_key = space_name
            self._verify_space_key(space_key)
            return space_key
        
        space_name_replaced = space_name.replace(' ', '%20')
        
        response = requests.get(url=self.api_url + 'content/search?cql=space.title%20%7E%20"' + space_name_replaced + '"&limit=1', headers=self.headers, auth=self.auth)
        
        if len(json.loads(response.text)['results']) == 1:
            space_key = json.loads(response.text)['results'][0]['_expandable']['space'].rsplit('/', 1)[-1]
            return space_key
        elif len(json.loads(response.text)['results']) > 1:
            raise ValueError('Duplicate space names found please use the spacekey')
        else:
            raise ValueError('Space not found, has it been deleted or is it called something else?')
        
        
    def _get_attachmentid(self, attachment_name, pageid):
        """
        Arguments:
            attachment_name (str): The name of the file attachment
            pageid (str): The pageid where the attachment is stored

        Returns:
            attachmentid (str): The attachmentid for the given attachment_name on the given pageid

        """
        
        assert isinstance(pageid, int), 'pageid should be the pageid of the requred page'
        assert isinstance(attachment_name, str), 'attachment_name should be a file name that is stored in the page and space'
        
        
        response = requests.get(url=self.api_url + 'content/' + str(pageid) + '/child/attachment',
                     headers=self.headers, auth=self.auth)
        
        for result in json.loads(response.text)['results']:
            if result['title'] == attachment_name:
                return result['id']
        else:
            print('No attachment found')
            
    
    def get_page_contents(self, page_name, space_name, **kwargs):
        """
        Arguments:
            page_name (str): The title of the page
            space_name (str): The space name where the page is stored

        Returns:
            contents (str): The contents of the given page
            
        """
        assert isinstance(page_name, str), 'title should be the title of a page within the space defined'
        assert isinstance(space_name, str), 'space_name should be the space name where the page is stored'
        space_name_as_key = kwargs.pop('space_name_as_key', False)
        
        pageid = self._get_pageid(page_name, space_name, space_name_as_key)
        
        response = requests.get(url='http://{server}/plugins/viewstorage/viewpagestorage.action?pageId={pageid}'.format(server=self.server, pageid=str(pageid)), 
                                headers=self.headers, auth=self.auth)
        return response.text
    
    
    def add_page(self, title, space_name, parent_page_name=None, body="", **kwargs):
        """
        Arguments:
            title (str): The title of the page to make
            space_name (str): The space name where the page is stored
            parent_page_name (str): The name of the parent page for the new page to be stored beneath
            body (str): The body text for the new page

        Returns:
            response (requests.models.Response): The response from the api request
            
        """
        space_name_as_key = kwargs.pop('space_name_as_key', False)
        
        space_key = self._get_space_key(space_name, space_name_as_key)
        payload = {
           "type":"page",
           "title":title,
           "space":{"key":space_key},
           "body":{
                    "storage":{
                    "value":body,
                    "representation":"storage"
                  }
               }
            }
        
        if parent_page_name:
            parent_page_id = self._get_pageid(parent_page_name, space_name, space_name_as_key)
            payload["ancestors"] = [{"id":parent_page_id}]

        data = json.dumps(payload)
        
        response = requests.post(url=self.api_url + 'content/', headers=self.headers, auth=self.auth, data=data)
        return response
        
    
    def _verify_space_key(self, space_key):
        """
        Arguments:
            space_key (str): The space key to be verified

        """
        
        response = requests.get(url=self.api_url + 'space?spaceKey={space_key}'.format(space_key=space_key),
            headers=self.headers, auth=self.auth)
        
        check = json.loads(response.text)['results']
        if len(check) != 1:
            raise ValueError('space_key: {space_key} doesnt exist'.format(space_key=space_key))

