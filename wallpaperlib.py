#!/usr/bin/python
# -*- coding: utf-8 -*-
# Check if exists ~/.cache/cinnamon/profiles path
# $ mkdir -p ~/.cache/cinnamon/profiles
# Script can be called  in two modes
    # Author
        # Get photos of author
            # Example ./wallpaperlib.py author photos ondrej.kolin
        # Get author profile photo
            # Example ./wallpaperlib.py author profile ondrej.kolin
    # Tags
        # Example ./wallpaperlib.py tags "sun beach" "all"
import sys
import xml.etree.ElementTree as ET
import os.path
import urllib
from os.path import expanduser
class flickr_api():
    #initing function
    def __init__(self):
        self.path = expanduser("~")+'/.cache/cinnamon/'
        self.api_key = 'e1eb10bf9d9dfe5ceb3f5330c4559e2d'
        self.prefix = 'https://api.flickr.com/services/rest/?method='
        self.service = 'flickr'
    #Get author id from its name
    def get_author_id(self, name):
        url = self.prefix + "flickr.people.findByUsername&api_key="+self.api_key+"&username="+name+"&format=rest"
        tree = ET.fromstring(urllib.urlopen(url).read());
        if tree.attrib["stat"] <> "ok":
            return None
        return tree[0].attrib["id"]
    #Get authors photos based on his name
    #name = name of author, count = max photos you want to download
    def get_author_photos(self, name, count=20):
        author_id = self.get_author_id(name)
        if not(author_id):
            return None
        url = self.prefix +"flickr.people.getPhotos&api_key=" + self.api_key + "&user_id="+ author_id + "&extras=url_o&format=rest"
        return self._feed_from_url(url,count)
    #get profile photo of autor
    #name = autor name
    def get_author_profile_photo(self, name):
        author_id = self.get_author_id(name)
        if not(author_id):
            return None
        url = self.prefix + "flickr.people.getInfo&api_key=" + self.api_key + "&user_id=" + author_id
        tree = ET.fromstring(urllib.urlopen(url).read());
        if tree.attrib["stat"] <> "ok":
            return None
        farm = tree[0].attrib["iconfarm"]
        server = tree[0].attrib["iconserver"]
        nsid = tree[0].attrib["nsid"]
        if (farm != 0 and server != 0):
            url = "http://farm" + farm + ".staticflickr.com/" + server + "/buddyicons/" + nsid + ".jpg"
        else:
            url = "https://www.flickr.com/images/buddyicon.jpg"
        local_url = self.path + self.service + "/profiles/" + name + ".jpg"
        if not(os.path.isfile(local_url)):
            urllib.urlretrieve(url, local_url)
        return local_url

    #get photos based on tags
    #tags = array of string tags, match = choice all of tags, any of tags, count= max number of photos  
    def get_by_tags(self, tags=[], match="any", count=20):
        tags = ",".join(tags)
        url = self.prefix + "flickr.photos.search&api_key="+self.api_key+"&tags="+tags+"&extras=url_o&format=rest"
        return self._feed_from_url(url,count)
    #Based on api url returns array of photos
    #url = flickr api url, count = max of photos you want to download
    def _feed_from_url(self, url, count= 20):
        result=[]
        tree = ET.fromstring(urllib.urlopen(url).read());
        #If error in respond
        if tree.attrib["stat"] <> "ok":
            return None
        counter = 0
        #If none photos there
        if len(tree[0])  == 0:
            return None
        for photo in tree[0]:
            #flickr returns even non big pictures, so I need to check if img has url_o (original img url)
            if 'url_o' in photo.keys():
                counter+=1
                url_o = photo.attrib["url_o"]
                url_s = "https://farm"+photo.attrib["farm"]+".staticflickr.com/"+photo.attrib["server"]+"/"+photo.attrib["id"]+"_"+photo.attrib["secret"]+"_q.jpg"
                size = [photo.attrib["height_o"],photo.attrib["width_o"]]
                title = photo.attrib["title"]
                result.append([url_s,url_o , title, size])
            if counter == count:
                break
        return result
    #get local url of photo
    #if not existing, downloads photo
    #photo = photo array
    def get_local_url(self, photo):
        if photo == None:
            return None
        url = photo[1]
        if url == "":
            return None
            
        local_url = self.path + self.service + "/" + url.split("/")[-1]
        #checking of overwriting
        if not(os.path.isfile(local_url)):
            urllib.urlretrieve(url, local_url)
        return local_url

    #download all photos of array
    #photos = photos array (typpicaly from _feed_from_url)
    def store_photos(self, photos):
        for photo in photos:
            print self.get_local_url(photo)

    #search groups by name
    #text = search pattern
        #returns an array of strings like "name:id"
    def search_groups(self, text):
        text = urllib.quote_plus(text) #escaping non url chars
        url = self.prefix+"flickr.groups.search&api_key=" + self.api_key + "&text=" + text + "&format=rest"
        tree = ET.fromstring(urllib.urlopen(url).read());
        result = [];
        for node in tree[0]:
            result.append(node.attrib.get("name") + ":" + node.attrib.get("nsid"))  
        return result
    def get_group_profile_photo(self, id):
        url = self.prefix + "flickr.groups.getInfo&api_key="+self.api_key+"&group_id="+id+"&format=rest"
        tree = ET.fromstring(urllib.urlopen(url).read());
        if tree.attrib["stat"] <> "ok":
            return None
        farm = tree[0].attrib["iconfarm"]
        server = tree[0].attrib["iconserver"]
        if (farm != 0 and server != 0):
            url = "http://farm" + farm + ".staticflickr.com/" + server + "/buddyicons/" + id + ".jpg"
        else:
            url = "https://www.flickr.com/images/buddyicon.jpg"
        local_url = self.path + self.service + "/profiles/" + id + ".jpg"
        if not(os.path.isfile(local_url)):
            urllib.urlretrieve(url, local_url)
        return local_url
        ##Get group feed photos
        # group_id = id of group, count = max number of photos to be downloaded
    def get_group_photos(self, group_id, count=20):
        url = self.prefix +"flickr.groups.pools.getPhotos&api_key=" + self.api_key + "&group_id="+ group_id + "&extras=url_o&format=rest"
        return self._feed_from_url(url,count)
    #creating a json output from array of photos
    #photos = photos array (typpicaly from _feed_from_url)
    #in progress, no function now!
    '''
    def get_json_output(self, photos):
        delimiter = False
        result = '{\n\t"photos": {\n'
        result += '\t\t"photo": [\n'
        for photo in photos:
            if delimiter:
                result+=',\n'
            result += '\t\t\t{\n'
            result += '\t\t\t\t"url_s": "'+ photo[0] + '",\n'
            result += '\t\t\t\t"url_o": "'+ photo[1] + '",\n'
            result += '\t\t\t\t"title": "'+ photo[2] + '",\n'
            result += '\t\t\t\t"sizes": \n'
            result += '\t\t\t\t\t\t{\n'
            result += '\t\t\t\t\t\t\t"height": ' + photo[3][0] + ',\n'
            result += '\t\t\t\t\t\t\t"width": ' + photo[3][1] + '\n'
            result += '\t\t\t\t\t\t}\n'
            result += '\t\t\t}'
            delimiter = True
        result += '\n\t\t]\n'
        result += '\t}\n}'
        return result
    '''

if __name__ == '__main__':
        flickr = flickr_api()
        # "Parse" args
        # Here is place for add browsing by tags support, etc.
        method = sys.argv[1] #can add tags support
        if method == "author":
            if sys.argv[2] == "photos":
                flickr.store_photos(flickr.get_author_photos(sys.argv[3]))
            elif sys.argv[2] == "profile":
                print flickr.get_author_profile_photo(sys.argv[3])
        elif method == "tags":
            if len(sys.argv) < 4:
                match_type = "any"
            else:
                match_type = sys.argv[3]
            flickr.store_photos(flickr.get_by_tags(sys.argv[2].split(" "), match_type))
        elif method == "group":
            if sys.argv[2] == "search":
                for group in flickr.search_groups(sys.argv[3]):
                    print group
            elif sys.argv[2] == "profile":
                print flickr.get_group_profile_photo(sys.argv[3])
            elif sys.argv[2] == "photos":
                flickr.store_photos(flickr.get_group_photos(sys.argv[3]))
