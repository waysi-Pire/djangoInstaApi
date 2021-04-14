from django.shortcuts import render
import requests, random, time, uuid
from tqdm import tqdm
from django.http import HttpRequest,JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.conf import settings
import os,ast


def get_cookies(cookie_file_path):
    # cookie_file_path = os.path.join(settings.BASE_DIR,'cookies',username.replace('@','').replace('.','')+"_cookies.json")
    try:
        file = open(cookie_file_path,'r')
        data = file.read()
        file.close()
        return ast.literal_eval(data)
    except:
        open(cookie_file_path,'w').close()
        return {}

def save_cookie(cookie_file_path,cookie):
    file = open(cookie_file_path,'w')
    file.write(str(cookie))
    file.close()

class request_bot:

    def __init__(
                    self,username,password
                ):
        self.username = username
        self.password = password
        self.session = None
        self.user_id = None
        self.ranked_token = "{}_{}"
        self.cookie_file_path = os.path.join(settings.BASE_DIR,'cookies',username.replace('@','').replace('.','')+"_cookies.txt")

    def generate_UUID(self,uuid_type=False):
        generated_uuid = str(uuid.uuid4())
        if uuid_type:
            return generated_uuid
        else:
            return generated_uuid.replace("-", "")

    def do_login(self,old_cookie=None):
        print("[+] Trying to login with username -> "+self.username)
        self.session = requests.session()
        url = "https://i.instagram.com/accounts/login/ajax/"
        loginuseragent = "Mozilla/5.0 (iPhone; CPU iPhone OS 12_3_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 Instagram 105.0.0.11.118 (iPhone11,8; iOS 12_3_1; en_US; en-US; scale=2.00; 828x1792; 165586599)"
        self.session.headers = {'user-agent': loginuseragent}
        self.session.headers.update({'Referer': 'https://i.instagram.com/'})

        if old_cookie:
            print("[+] Using old Cookies")
            self.session.cookies.update(old_cookie)
            sreq = self.session.get("https://i.instagram.com")
            self.session.headers.update({'X-CSRFToken': sreq.cookies['csrftoken']})
        else:
            sreq = self.session.get("https://i.instagram.com")
            self.session.headers.update({'X-CSRFToken': sreq.cookies['csrftoken']})

        data = {"username": self.username, "password": self.password}
        loginreq = self.session.post(url, data=data, allow_redirects=True)

        print(loginreq.text)

        if loginreq.text.find("userId") >= 0:
            new_cookie = self.session.cookies.get_dict()
            print(new_cookie)
            save_cookie(self.cookie_file_path,new_cookie)
            self.user_id = loginreq.json().get('userId')
            uuId = self.generate_UUID(uuid_type=True)
            self.ranked_token = self.ranked_token.format(self.user_id,uuId)
            print("[~] Logged in on account : " + self.username)
            return True
        elif loginreq.text.find("/challenge") >= 0:
            print("[++] Found challenge, while login.")
            return False
        else:
            print("[++] Wrong Username / Password.")
            return False
    
    def load_session(self):
        cookie = get_cookies(self.cookie_file_path)
        if not self.session:
            self.do_login(old_cookie=cookie)

    def get_user_info(self,target_user):
        self.load_session()
        print("[+] Getting User '{}' Info...".format(target_user))
        r = self.session.get("https://www.instagram.com/{}?__a=1".format(target_user))
        return r.json()

    def get_user_followers(self,target_username,total=None):
        self.load_session()
        print("[+] Getting User {} followers.".format(target_username))
        info = self.get_user_info(target_username)
        ID = info.get('graphql').get('user').get('id')
        total_followers_count = info.get('graphql').get('user').get('edge_followed_by').get('count')
        if not total:total = total_followers_count
        all_followers = []
        user_agent = {"User-agent":"Mozilla/5.0 (iPhone; CPU iPhone OS 12_3_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 Instagram 105.0.0.11.118 (iPhone11,8; iOS 12_3_1; en_US; en-US; scale=2.00; 828x1792; 165586599)"}
        endpoint = "https://i.instagram.com/api/v1/friendships/{}/followers/?max_id={}"
        max_id = ""
        pbar = tqdm(total=total)
        while 1:
            url = endpoint.format(ID, max_id)
            self.session.headers = user_agent
            res = self.session.get(url)
            data = res.json()
            users = data.get('users') if bool(data.get('users')) else []
            for user in users:
                all_followers.append((user.get('pk'),user.get('username')))
                pbar.update(n=1)
            max_id = data.get('next_max_id')

            if not max_id:
                break
            if len(all_followers) >= total:
                break
        pbar.close()
        return all_followers

    def get_user_followers_followings_count(self,target_username):
        self.load_session()
        info = self.get_user_info(target_username)
        return info.get('graphql').get('user').get('edge_followed_by').get('count'),info.get('graphql').get('user').get('edge_follow').get('count')

    def get_hashtag_users(self,target_hashtag,total=100):
        target_hashtag = target_hashtag.replace('#','')
        self.load_session()
        print("[+] Fetching Users from hashtag '{}'.".format(target_hashtag))
        all_users = []
        user_agent = {"User-agent":"Mozilla/5.0 (iPhone; CPU iPhone OS 12_3_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 Instagram 105.0.0.11.118 (iPhone11,8; iOS 12_3_1; en_US; en-US; scale=2.00; 828x1792; 165586599)"}
        endpoint = "https://i.instagram.com/api/v1/feed/tag/{}/?max_id={}"
        max_id = ""
        pbar = tqdm(total=total)
        while 1:
            url = endpoint.format(target_hashtag, max_id)
            self.session.headers = user_agent
            res = self.session.get(url)
            data = res.json()
            items = data.get('items')
            for item in items:
                all_users.append((item.get('user').get('pk'),item.get('user').get('username')))
                pbar.update(n=1)
            max_id = data.get('next_max_id')

            if not max_id:
                break
            if len(all_users) >= total:
                break
        pbar.close()
        return all_users

    def get_location_users(self,target_location,total=60):
        
        self.load_session()
        print("[+] Fetching Users from Location '{}'.".format(target_location))
        res = self.session.get("https://i.instagram.com/api/v1/fbsearch/places/?query={}".format(target_location))
        try:
            location_id = res.json()['items'][0]['location']['pk']
        except:
            pass
        all_users = []
        user_agent = {"User-agent":"Mozilla/5.0 (iPhone; CPU iPhone OS 12_3_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 Instagram 105.0.0.11.118 (iPhone11,8; iOS 12_3_1; en_US; en-US; scale=2.00; 828x1792; 165586599)"}
        endpoint = "https://i.instagram.com/api/v1/feed/location/{}/?max_id={}"
        max_id = ""
        pbar = tqdm(total=total)
        while 1:
            url = endpoint.format(location_id, max_id)
            self.session.headers = user_agent
            res = self.session.get(url)
            data = res.json()
            items = data.get('items')
            for item in items:
                all_users.append((item.get('user').get('pk'),item.get('user').get('username')))
                pbar.update(n=1)
            max_id = data.get('next_max_id')

            if not max_id:
                break
            if len(all_users) >= total:
                break
        pbar.close()
        return all_users

    def get_user_recent_medias(self,target_username):
        self.load_session()
        print("[+] Getting recent medias of User {} ".format(target_username))
        info = self.get_user_info(target_username)
        edges = info.get('graphql').get('user').get("edge_owner_to_timeline_media").get('edges')
        return edges

    def get_all_likers(self,media_code,total_likes=None):
        self.load_session()
        all_likers = []
        urlScraping='https://www.instagram.com/graphql/query/?query_hash=d5d763b1e2acf209d62d22d184488e57&variables={"shortcode":"codeSHORT","include_reel":true,"first":50,"after":"max_id"}'
        max_id = ''
        has_next_page = True
        pb = tqdm(total=total_likes if total_likes!=None else 100)
        while has_next_page:
            try:
                url=urlScraping.replace('codeSHORT',media_code).replace('max_id',max_id)
                response=self.session.get(url)
                # response=session.get(url,headers=hd)
                data = response.json()

                edges = data['data']['shortcode_media']['edge_liked_by']['edges']
                for edge in edges:
                    username = edge.get('node').get('username')
                    Id = edge.get('node').get('id')
                    all_likers.append((username,Id))
                    # yield (username,Id)
                    pb.update(n=1)
                
                has_next_page = data['data']['shortcode_media']['edge_liked_by']['page_info']['has_next_page']
                if has_next_page:
                    max_id=data['data']['shortcode_media']['edge_liked_by']['page_info']['end_cursor']
                    max_id=str(max_id).replace('\"','')
                else:
                    break
                
                time.sleep(5)

            except Exception as e:
                print(e)
                time.sleep(10)
        pb.close()
        return all_likers

    def get_recent_post_likers(self,target_username,total_recent_medias=3):
        self.load_session()
        recent_medias = self.get_user_recent_medias(target_username)
        try:
            recent_medias = recent_medias[:total_recent_medias]
        except:
            pass

        MEDIAS_DETAIL = []
        for media in recent_medias:
            media_code = media.get('node').get('shortcode')
            media_likes_count = media.get('node').get('edge_liked_by').get('count')
            all_likers = self.get_all_likers(media_code,total_likes=media_likes_count)
            MEDIAS_DETAIL.append({
                'media_info':media,
                'likers':all_likers
            })
        return MEDIAS_DETAIL

    def get_user_medias(self,target_username,amount):
        self.load_session()
        info = self.get_user_info(target_username)
        target_user_id = info.get('graphql').get('user').get('id')
        max_id = ""
        user_agent = {"User-agent":"Mozilla/5.0 (iPhone; CPU iPhone OS 12_3_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 Instagram 105.0.0.11.118 (iPhone11,8; iOS 12_3_1; en_US; en-US; scale=2.00; 828x1792; 165586599)"}
        endpoint = "https://i.instagram.com/api/v1/feed/user/{}/?max_id={}&rank_token={}&ranked_content=true"
        all_medias = []
        while 1:
            try:
                url = endpoint.format(target_user_id, max_id, self.ranked_token)
                self.session.headers = user_agent
                res = self.session.get(url)
                data = res.json()
                for item in data.get('items'):
                    try:
                        url = item.get('image_versions2').get('candidates')[0].get('url')
                        code = item.get('code')
                        all_medias.append(
                                            {
                                                'url':url,
                                                'code':code
                                            }
                                        )
                    except:
                        pass
                max_id = data.get('next_max_id')
                if not max_id:
                    print("this runned")
                    break
                if len(all_medias)>=amount:
                    break

            except Exception as e:
                print(e)
                break
        return all_medias



@api_view(['POST'])
# @permission_classes([IsAuthenticated])
def getPostsView(request):
    target_username = request.data.get('target_username')

    try:
        amount = int(request.data.get('amount'))
        if amount<1:
            return JsonResponse({"msg":"amount must be greater then 0"})
    except Exception as e:
        return JsonResponse({"msg":"amount must be greater then 0"})
    try:
        insta_account = settings.INSTA_ACCOUNTS[random.randint(0,len(settings.INSTA_ACCOUNTS)-1)]
        bot = request_bot(insta_account.get('username'),insta_account.get('password'))
        medias = bot.get_user_medias(target_username,amount)
        return JsonResponse({'status': "pass",'posts':medias})
    except Exception as e:
        return JsonResponse({'status': "fail",'msg':str(e)})

