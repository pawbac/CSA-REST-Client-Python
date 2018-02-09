import requests
import json
import yaml
import textwrap

# Default values
# TODO make them local
remotes = []#['http://localhost:3000/api/broadcasts.json', 'https://csa-heroku-pab37.herokuapp.com/api/broadcasts.json']
api_url = ""
console_width = 60
login = ""
password = ""

class CsaRestClient:
    def run(self):
        self.__initialise()
        self.__menu_loop()
        self.__save_config()

    def __initialise(self):
        global api_url, login, password

        self.__read_config()
        
        api_url = remotes[0] # default API

        login = ""
        password = ""

    def __menu_loop(self):
        global login

        while True:
            print("-" * console_width)
            print("CSA REST CLIENT".center(console_width))
            print()
            print("Remote: {}".format(api_url).center(console_width))
            print()
            print("1. List existing broadcasts\n"
                  "2. Create a new broadcast\n"
                  "3. Change remote server")
            if login:
                print("4. Logout")
            print("Q. Quit")

            ans = input().upper()
            # Weird switch implementation
            if ans == '1':
                self.__list_broadcasts()
            elif ans == '2':
                self.__create_broadcast()
            elif ans == '3':
                self.__change_remote()
            elif ans == '4':
                self.__logout()
            elif ans == 'Q':
                break
            else:
                print("Wrong answear, try again")

    def __logout(self):
        global login, password

        login = ""
        password = ""
        print("Logged out")

    def __change_remote(self):
        global api_url, remotes

        print("\nChose remote server:")
        for index, remote in enumerate(remotes):
            print("{}. {}".format(index, remote))
        print("\nN. Add new remote")
        print("Q. Back")

        answ = input().upper()
        if answ.isdigit() and int(answ) < len(remotes):
            api_url = remotes[int(answ)]
        elif answ == "N":
            api_url = input("URL: ")
            remotes.append(api_url)
        elif answ == "Q":
            return
        else:
            print("\nWrong answear, try again.")

    def __list_broadcasts(self):
        print("BROADCASTS".center(console_width))
        print()

        response = self.__send_request('get')

        if not response:
            return

        broadcasts = response.json()
        if len(broadcasts):
            for broadcast in broadcasts:
                print("-" * console_width)

                # User / Date
                print(broadcast["created_at"].center(console_width))
                print("{} {} (ID: {})".format(broadcast["user"]["firstname"],
                                              broadcast["user"]["surname"], 
                                              broadcast["user"]["id"]
                                              ).center(console_width))
                print("{}".format(broadcast["url"]).center(console_width))

                # Feeds
                feeds = []
                for feed in broadcast["feeds"]:
                    feeds.append(feed["name"])

                print(','.join(feeds).center(console_width))
                print()

                # Message
                print(textwrap.fill(broadcast["content"], width = console_width))
                print()
        else:
            print("There are no existing broadcasts".center(console_width))

    def __create_broadcast(self):
        request = {}
        feeds = {}

        request['broadcast'] = {'content': input("Message: ")}
        if not request['broadcast']['content']:
            print("Message cannot be empty, try again")
            return

        print("Select feeds:")
        if input("Email [n]: ").upper() == 'Y':
            feeds['email'] = 1
        if input("Facebook [n]: ").upper() == 'Y':
            feeds['facebook'] = 1
        if input("RSS [n]: ").upper() == 'Y':
            feeds['RSS'] = 1
        if input("Atom [n]: ").upper() == 'Y':
            feeds['atom'] = 1
        if input("Twitter [n]: ").upper() == 'Y':
            feeds['twitter'] = 1
            request['shorten_url'] = input("Shorten URL: ")
        if input("Notification feed [n]: ").upper() == 'Y':
            feeds['notification_feed'] = 1

        if len(feeds):
            request['feeds'] = feeds
        else:
            print("You did not chose any feeds, try again")
            return

        self.__send_request('post', request)

    def __send_request(self, method, request = {}):
        global login, password
        if not login:
            print("Please, enter your credentials:")
            login = input("Login: ")
            password = input("Password: ")

        try:
            if method == 'get':
                return requests.get(api_url, auth=(login, password))
            elif method == 'post':
                return requests.post(api_url, json=request, auth=(login, password))
        except Exception as exception:
            login = ""
            password = ""

            print("Wrong password or remote server down")
            print("Error: {}".format(exception))
            print()
                
    def __read_config(self):
        global console_width
        global remotes

        try:
            config = yaml.load(open('config/config.yml')) # Why open() needed?
            console_width = config["console_width"]
            remotes = config["remotes"]
        except:
            # If no config file found or file corrupted - set default values
            print("File does not exists, loading default values")
            console_width = 60
            remotes = ['http://localhost:3000/api/broadcasts.json', 'https://csa-heroku-pab37.herokuapp.com/api/broadcasts.json']

    def __save_config(self):
        try:
            config = yaml.load(open('config/config.yml')) # Is it even needed?
            config["console_width"] = console_width
            config["remotes"] = remotes
            with open('config/config.yml', 'w') as f:
                yaml.dump(config, f, default_flow_style=False)  # Human-friendly format
        except Exception as exception:
            print(exception)
            print("Changes will not be saved - config file not found or corrupted")

if __name__ == "__main__":
    csa_rest_client = CsaRestClient()
    csa_rest_client.run()