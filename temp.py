from instabot import Bot


class request_bot:

    def __init__(
                    self,username,password
                ):
        self.username = username
        self.password = password
        self.session = None

    def do_login(self):
        # print("[+] Trying to login with username -> "+self.username)
        self.session = requests.session()
        url = "https://i.instagram.com/accounts/login/ajax/"
        loginuseragent = "Mozilla/5.0 (iPhone; CPU iPhone OS 12_3_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 Instagram 105.0.0.11.118 (iPhone11,8; iOS 12_3_1; en_US; en-US; scale=2.00; 828x1792; 165586599)"
        self.session.headers = {'user-agent': loginuseragent}
        self.session.headers.update({'Referer': 'https://i.instagram.com/'})

        sreq = self.session.get("https://i.instagram.com")

        self.session.headers.update({'X-CSRFToken': sreq.cookies['csrftoken']})
        data = {"username": self.username, "password": self.password}
        loginreq = self.session.post(url, data=data, allow_redirects=True)
        editcookie = sreq.cookies['csrftoken']
        # if proxy!="None":
        headers = {
            "method": "post",
            "scheme": "https",
            "accept": "*/*",
            "authority": "www.instagram.com",
            "referer": "https://www.instagram.com/accounts/edit/",
            "x-requested-with": "XMLHttpRequest",
            "path": "/accounts/edit/",
            "content-type": "application/x-www-form-urlencoded",
            "x-csrftoken": editcookie,
            "user-agent": loginuseragent}
        self.session.headers.update(headers)
        res = loginreq.json()
        if loginreq.text.find("userId") >= 0:
            # print("[++] Logged in on account :" + username)
            return True
        elif loginreq.text.find("/challenge") >= 0:
            print("[++] Found challenge, while login.")
            return False
        else:
            print(loginreq.text)
            print("[++] Wrong Username / Password.")
            return False
    
    def load_session(self):
        if not self.session:self.do_login()

    def get_user_info(self,target_user):
        self.load_session()
        print_me("[+] Getting User '{}' Info...".format(target_user))
        r = self.session.get("https://www.instagram.com/{}?__a=1".format(target_user))
        return r.json()

    def get_user_followers(self,target_username,total=None):
        self.load_session()
        print_me("[+] Getting User {} followers.".format(target_username))
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

