"""
=====================================================
 PHPIPAM API Python Library
=====================================================
:Info: See https://github.com/enovance/phpipam/tree/master/api for API implementation.
:Author: Benton Snyder introspectr3@gmail.com
:Website: Noumenal Designs <http://www.noumenaldesigns.com>
:Date: $Date: 2013-12-2 
:Description: Python library for interfacing with PHPIPAM <http://www.phpipam.net>.
"""
# coding: utf-8
import httplib
import urllib
import base64
import rijndael
import json

KEY_SIZE = 16
BLOCK_SIZE = 32

def encrypt(key, plaintext):
    padded_key = key.ljust(KEY_SIZE, '\0')
    padded_text = plaintext + (BLOCK_SIZE - len(plaintext) % BLOCK_SIZE) * '\0'

    r = rijndael.rijndael(padded_key, BLOCK_SIZE)

    ciphertext = ''
    for start in range(0, len(padded_text), BLOCK_SIZE):
        ciphertext += r.encrypt(padded_text[start:start+BLOCK_SIZE])

    encoded = base64.b64encode(ciphertext)

    return encoded


def decrypt(key, encoded):
    padded_key = key.ljust(KEY_SIZE, '\0')

    ciphertext = base64.b64decode(encoded)

    r = rijndael.rijndael(padded_key, BLOCK_SIZE)

    padded_text = ''
    for start in range(0, len(ciphertext), BLOCK_SIZE):
        padded_text += r.decrypt(ciphertext[start:start+BLOCK_SIZE])

    plaintext = padded_text.split('\x00', 1)[0]

    return plaintext

class PHPIPAM:
    def __init__(self, url, api_id, api_key):
        """Constructor

        Parameters
            url - string base url to phpipam server
            api_id - string phpipam api id
            api_key - string phpipam api key
        """
        self.url = url
        self.api_id = api_id
        self.api_key = api_key

    def query_phpipam(self, **kwargs):
        """Query PHPIPAM API

        Sends HTTP POST query to PHPIPAM

        Parameters
            kwargs - dictionary
        Returns
            JSON
            {
                "success":true,
                "data": [{...}, ...]
            }
        """
        data = {
            'enc_request': encrypt(self.api_key, json.dumps(kwargs)),
            'app_id': self.api_id
        }
        data.update(kwargs)
        params = urllib.urlencode(data)

        headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
        conn = httplib.HTTPSConnection(self.url)
        conn.request("POST", "/phpipam/api/index.php", params, headers)
        response = conn.getresponse()

        data = response.read()
        conn.close()  

        return data            

    def generic(self, controller, action, **kwargs):
        """Query PHPIPAM 

        Parameters
            controller - string controller name
               valid controller values = ["sections", "subnets", "addresses", "vlans", "users", "groups", "requests"] 
            action - string action name
                valid action values = ["read", "create", "update", "delete"]
        Returns
            JSON
            {
                "success":true,
                "data": [{...}, ...]
            }                            
        """
        data = {"controller": controller, "action": action}
        data.update(kwargs)

        return self.query_phpipam(**data)

    def read_sections(self, filter=None):
        """Fetch sections

        Retrieve list of sections 

        Parameters
            filter - string filter by value
                None for all
                Number for by filter by ID
                String for filter by Name
        Returns
            JSON
            {
                "success":true,
                "data": [
                    {
                        "id":"1",
                        "name":"Customers",
                        "description":"Section for customers",
                        "masterSection":"0",
                        "permissions":"{\"3\":\"1\",\"2\":\"2\"}",
                        "strictMode":"1",
                        "subnetOrdering":null,
                        "order":null,
                        "editDate":null,
                        "showVLAN":"0"
                        ,"showVRF":"0"
                    },
                    ...
                ]
            }            
        """
        data = {"controller": "sections", "action": "read"}
        if filter == None:
            data.update({"all": True})
        elif filter.isdigit():
            data.update({"id": filter})
        elif filter.isalpha():
            data.update({"name": filter})

        return self.query_phpipam(**data)

    def create_section(self, name, description, strict_mode=None, order=None, subnet_ordering=None):
        """Create section

        Define new section with specified parameters

        Parameters
            name - string section name
            description = string description
            strictMode - optional bool strict mode on/off
            order - optional int section order position
            subnetOrdering - optional string order in which subnet is displayed (ex field,direction or subnet,desc)
        Returns
            JSON
            {
                "success":true,
                "data":"Section created"
            }
        """
        data = {
            "controller": "sections", 
            "action": "create",
            "name": name,
            "description": description,
            "strictMode": strict_mode
        }
        if strict_mode:
            data.update({"strictMode": strict_mode})
        if order:
            data.update({"order": order})
        if subnet_ordering:
            data.update({"subnetOrdering": subnet_ordering})

        return self.query_phpipam(**data)

    def update_section(self, id, name=None, description=None, strict_mode=None, order=None, subnet_ordering=None):
        """Update section

        Updates specified section values

        Parameters
            id - int section id
            name - optional string section name
            description - optional string description 
            strict_mode - optional bool strict mode on/off (default on)
            order - optional int section order position
            subnet_ordering - optional string order in which subnet is displayed (ex field,direction or subnet,desc)
        Returns
            JSON
            {
                "success":true,
                "data":"Section updated"
            }
        """
        data = {
            "controller": "sections",
            "action": "update",
            "id": id
        }    
        if name:
            data.update({"name": name})
        if description:
            data.update({"description": description})
        if strict_mode:
            data.update({"strictMode": strict_mode})
        if order:
            data.update({"order": order})
        if subnet_ordering:
            data.update({"subnetOrdering": subnet_ordering})  

        return self.query_phpipam(**data)   

    def delete_section(self, id):
        """Delete section

        Deletes specified section

        Parameters
            id - int section id
        Returns
            JSON
            {
                "success":true,
                "data":"Section deleted"
            }
        """
        data = {
            "controller": "sections",
            "action": "delete",
            "id": id
        }  

        return self.query_phpipam(**data)   

    def read_subnets(self, format="ip", id=None, section_id=None):           
        """Fetch subnets

        Retrieve list of subnets by specified filter

        Parameters
            format - string output format (ip/decimal)
            id - optional int subnet id
            section_id - optional int section_id
        Returns
            JSON
            {
                "success":true,
                "data": [
                    {
                        "id":"1",
                        "subnet":"fd13:6d20:29dc:cf27::",
                        "mask":"64",
                        "sectionId":"3",
                        "description":"Private subnet 1",
                        "vrfId":"0",
                        "masterSubnetId":"0",
                        "allowRequests":"1",
                        "vlanId":"1",
                        "showName":"1",
                        "permissions":"{\"3\":\"1\",\"2\":\"2\"}",
                        "pingSubnet":"0",
                        "isFolder":"0",
                        "editDate":null
                    },
                    ...
                ]
            }                    
        """
        data = {"controller": "subnets", "action": "read", "format": format}
        if not id and not section_id:
            data.update({"all": True})
        elif id:
            data.update({"id": id})
        elif section_id:
            data.update({"sectionId": section_id})

        return self.query_phpipam(**data)

    def create_subnet(self, section_id, subnet, mask, format="ip", master_subnet_id=0, vrf_id=0, vlan_id=0, allow_requests=0, show_name=0, ping_subnet=0, permissions=None, description=None):
        """Create subnet

        Defines new subnet

        Parameters
            section_id - int section id
            subnet - string network address
            mask - int cidr
            format - string output format (ip/decimal)
            master_subnet_id - int parent subnet id
            vrf_id - int vrf id
            vlan_id - int vlan id
            allow_requets - bool allow requests
            show_name - bool show subnet name
            ping_subnet - bool ping hosts in subnet
            permissions - optional string permissions values
            description - optional string subnet description 
        Returns
            JSON
            {
                "success":true,
                "data":"Subnet created"
            }            
        """
        data = {
            "controller": "subnets", 
            "action": "create", 
            "format": format,
            "subnet": subnet,
            "mask": mask,
            "sectionId": section_id,
            "masterSubnetId": master_subnet_id,
            "allowRequests": allow_requests,
            "vrfId": vrf_id,
            "vlanId": vlan_id,
        }

        if description:
            data.update({"description": description})
        if show_name:
            data.update({"showName": show_name})
        if permissions:
            data.update({"permissions": permissions})
        if ping_subnet:
            data.update({"pingSubnet": ping_subnet})

        return self.query_phpipam(**data)    

    def read_addresses(self, subnet_id):
        data = {"controller": "addresses", "action": "read", "format": "ip"}
        data.update({"subnetId": subnet_id})

        return self.query_phpipam(**data)
