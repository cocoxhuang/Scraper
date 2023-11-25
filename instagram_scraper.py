'''
This code implments the following functions:
1. Retrieve an instagram's user's raw json data. The retrived json should 
include but is not limited to:
    - username
    - Category
    - biography
    - number of followers, numbers of followings
    - full name
    - link to profile picture
    - 12 most recent posts with
        - captions
        - locations
        - link to pictures in the posts
2. Download recent 12 posts' captions and pictures of an user.

We can opt to use Smartproxy to avoid blocking by Instagram for all
functions below.
'''

import requests
import random
import json
import os
import urllib.request
from stopit import threading_timeoutable as timeoutable
import numpy as np

def get_user_JSON(username,rootdir, error_keys = ['message', 'require_login', 'status'], if_smartproxy = False, smartproxy_username ="",smartproxy_password =""):
    '''
    Retrieve an instagram's user's raw json data. The retrived json should 
    include but is not limited to:
    - username
    - Category
    - biography
    - number of followers, numbers of followings
    - full name
    - link to profile picture
    - 12 most recent posts with
        - captions
        - locations
        - link to pictures in the posts     

    Parameters:
    --------
    - username : str. Username of the Instagram user whose profile json we are retrieving

    - rootdir : directory. Directory to the folder where we want to store the retrived Json file

    - error_keys : list. If the retrieved json is error_keys, there is an error while retrieving 
    the json file caused by Instagram API. 
        Default : ['message', 'require_login', 'status']

    - if_smartproxy : bool. If we are using smartproxy
        Default : False

    - smartproxy_username : str. Your Smartproxy's username.
        Default : ''

    - smartproxy_password: str. Your Smartproxy's smartproxy_password.
        Default : ''

    Returns
    --------
    bool : if retrieval is successful.
    '''
    
    # if the json file returned is the following, it means the crawl wasn't successful
    # error_keys = ['message', 'require_login', 'status']
    # get online response
    response_json_keys = []
    if_retrival_failed = True
    print(f"Username: {username}")
    url = "https://www.instagram.com/" + username + "/?__a=1&__d=dis"
    # print("url: ", url)
    while if_retrival_failed == True:
        if if_smartproxy:
            proxy = f'http://{smartproxy_username}:{smartproxy_password}@gate.smartproxy.com:7000'
            try:
                response = requests.get(url, proxies={'http': proxy, 'https': proxy},headers = {
                    "user-agent" : random.choice([
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.80 Safari/537.36", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36",
                        "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Safari/537.36", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Safari/537.36",
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.157 Safari/537.36",
                        "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.157 Safari/537.36"
                        ])
                })
            except:
                print("Exceeds maximum tries. Failed retrieving json.")
                return False
        else:
            try:
                response = requests.get(url, headers = {
                    "user-agent" : random.choice([
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.80 Safari/537.36", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36",
                        "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Safari/537.36", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Safari/537.36",
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.157 Safari/537.36",
                        "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.157 Safari/537.36"
                        ])
                })
            except:
                print("Exceeds maximum tries. Failed retrieving json.")
                return False
        if response.status_code != 404:
            # Serializing json
            try:
                response_json = response.json()
                response_json_keys = list(response_json.keys())
                if_retrival_failed = response_json_keys == error_keys
            except:
                if_retrival_failed = True
            if if_retrival_failed == False:
                print("Successflly retrieved json.")
            else:
                print("Failed retrieving json. Try again..")
        else:
            print("Failed retrieving json. User {} doesn't exist.".format(username))
            return False

    json_object = json.dumps(response_json, indent=4)
    my_dir = os.path.join(rootdir, username)
    with open(my_dir, "w") as outfile:
        outfile.write(json_object)
    return True
    
def process_user(username,raw_json,processed_JSON_dir):
    '''
    Retrieve an image using its URL and Smartproxy.

    Parameters:
    --------
    - username: string. Username of the json file.

    - raw_json : json. User's raw dictionary from json file downloaded from Instagram API

    - processed_JSON_dir : directory. Directory to the folder where we want to store the processed json file.

    '''

    # Read from raw Json file
    category = list(np.array(raw_json['seo_category_infos'])[:,0])
    id = raw_json['graphql']['user']['id']
    biography = raw_json['graphql']['user']['biography']
    num_followers  = raw_json['graphql']['user']['edge_followed_by']['count']
    num_followees  = raw_json['graphql']['user']['edge_follow']['count']

    # Create processed user JSON
    user_JSON = {}
    user_JSON['username'] = username
    user_JSON['category'] = category
    user_JSON['id'] = id
    user_JSON['biography'] = biography
    user_JSON['num_followers'] = num_followers
    user_JSON['num_followees'] = num_followees

    # create json object from dictionary
    follower_JSON_path = os.path.join(processed_JSON_dir, username)
    with open(follower_JSON_path, 'w') as fp:
        json.dump(user_JSON, fp, indent = 6)

def local_img_retrieve(imgURL, dir):
    '''
    Retrieve an image using its URL and local IP address.

    Parameters:
    --------
    - imgURL : str. Picture's URL

    - dir : directory. Directory to the folder where we want to store the retrived image file

    Returns
    --------
    bool : if retrieval is successful.
    '''

    try:
        urllib.request.urlretrieve(imgURL, dir)
        return True
    except:
        print("getting pic failed")
        return False

@timeoutable()
def proxy_img_retrieve(imgURL,dir,sp_username = '',sp_password = ''):
    '''
    Retrieve an image using its URL and Smartproxy.

    Parameters:
    --------
    - imgURL : str. Picture's URL

    - dir : directory. Directory to the folder where we want to store the retrived image file

    - sp_username : str. Your Smartproxy's username.
        Default : ''

    - sp_password: str. Your Smartproxy's smartproxy_password.
        Default : ''

    Returns
    --------
    bool : if retrieval is successful.
    '''
    proxy = f'http://{sp_username}:{sp_password}@gate.smartproxy.com:7000'
    try:
        # print(f'Retrieve {imgURL}...')        
        response = requests.get(imgURL, proxies={'http': proxy, 'https': proxy},headers = {
            "user-agent" : random.choice([
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.80 Safari/537.36", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36",
                "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Safari/537.36", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Safari/537.36",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.157 Safari/537.36",
                "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.157 Safari/537.36"
                ])
        })
        
        # print(f'response.status_code: {response.status_code}')
        if response.status_code == 200:
            with open(dir, 'wb') as f:
                f.write(response.content)

        return True
    
    except:
        print("getting pic failed")
        return False
    
def download_posts(username,raw_json,user_pic_dir,user_post_dir,if_smart_proxy = False,smartproxy_username = '',password = ''):
    '''
    Retrieve an image using its URL and Smartproxy.

    Parameters:
    --------
    - username: string. Username of the json file.
    
    - raw_json : json. User's raw dictionary from json file downloaded from Instagram API

    - user_pic_dir : directory. Directory to the folder where we want to store the retrived image file.
        Files will be store in a newly created '../user_pic_dir/username' folder.

    - user_post_dir : directory. Directory to the folder where we want to store the retrived image file
        Files will be store in a newly created '../user_post_dir/username' folder.

    - if_smart_proxy: bool. If you choose to use smartproxy

    - sp_username : str. Your Smartproxy's username.
        Default : ''

    - sp_password: str. Your Smartproxy's smartproxy_password.
        Default : ''

    Returns
    --------
    bool : if retrieval is successful.
    '''

    # user = raw_json['graphql']['user']['username']
    print(f'Downloading user {username}\'s post jsons and related images..')

    # processed pic folder 
    pic_dir = os.path.join(user_pic_dir, username)
    # mode
    mode = 0o666
    # Create the directory
    try:
        os.mkdir(pic_dir, mode)
    except:
        print("Image folder already exists.")

    # processed posts JSON folder 
    post_JSON_dir = os.path.join(user_post_dir, username)
    # mode
    mode = 0o666
    # Create the directory
    try:
        os.mkdir(post_JSON_dir, mode)
        # os.mkdir(post_JSON_dir)
    except:
        print("Post JSON folder already exists.")

    posts_len = len(raw_json['graphql']['user']['edge_owner_to_timeline_media']['edges'])
    # posts_len = 1
    print("We can get {} posts.".format(posts_len))
    for i in range(posts_len):
        post = raw_json['graphql']['user']['edge_owner_to_timeline_media']['edges'][i]['node']

        # post_info
        post_id = post['id']
        print("post_id: ", post_id)
        imgURL = post['display_url']
        is_video = post['is_video']
        edge_media_to_caption = post['edge_media_to_caption']['edges']
        if len(edge_media_to_caption) > 0:
            caption = post['edge_media_to_caption']['edges'][0]['node']['text']
        else:
            caption =''

        # save post JSON
        post_JSON = {}
        post_JSON['imgURL'] = imgURL
        post_JSON['post_id'] = post_id
        post_JSON['is_video'] = is_video
        post_JSON['caption'] = caption
        my_dir = os.path.join(post_JSON_dir, post_id)
        with open(my_dir, 'w') as fp:
            json.dump(post_JSON, fp, indent = 6)

        # save picture
        dir = os.path.join(pic_dir, post_id + ".jpg")
        if not if_smart_proxy:
            if_img_retrieve = local_img_retrieve(imgURL, dir)
        else:
            if_img_retrieve = proxy_img_retrieve(imgURL, dir, smartproxy_username, password, timeout = 5)
            tries = 0
            while if_img_retrieve == False and tries < 10:
                if_img_retrieve = proxy_img_retrieve(imgURL, dir, smartproxy_username, password, timeout = 5)
                tries += 1
        if not if_img_retrieve:
                os.remove(my_dir)