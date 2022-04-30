import requests
import argparse
import os
import re


# This script intends to take the dir name, locate the URL links, and summarize their status
# Author
#       Vahid Etemadi(vetemadi87@gmail.com)

total_link_status = {"Success links": 0, "Redirection links": 0, "Client error links": 0, "Server error links": 0, "Total links": 0,  "Valid links": 0}

def lookup_link(dir_name):
    #iterate over the files inside the dir
    for file in os.listdir(dir_name):
        with open("{dirname}/{filename}".format(dirname=dir_name, filename=file), 'r') as f:
            #look for the link in the files--> via a regex pattern
            for line in f:
                urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', f.read())
                # for each reconized link, call analyise, it will return the status code 
                analyise_link(urls)


def analyise_link(the_links):
    #once been found, making a call, take response, extract reponse code and categrize it as one of the items in the predefind dic!
    #write a switch case to categozie base on the retun code

    total_link_status['Total links'] = total_link_status['Total links'] + len(the_links)
    total_link_status['Valid links'] = total_link_status['Valid links'] + len(the_links)

    for url in the_links:
        try: 
            response = requests.get(url)
            
            resp_status = str(response.status_code)

            resp_status_start = resp_status[0]

            if resp_status_start == '2':
                total_link_status['Success links'] = total_link_status['Success links'] + 1
            elif resp_status_start == '3':
                total_link_status['Redirection links'] = total_link_status['Redirection links'] + 1
            elif resp_status_start == '4':
                total_link_status['Client error links'] = total_link_status['Client error links'] + 1
            elif resp_status_start == '5':
                total_link_status['Server error links'] = total_link_status['Server error links'] + 1
        except:
            total_link_status['Valid links'] = total_link_status['Valid links'] - 1
    
    #an alternative to above if then else block that need python >= 3.10
    #match resp_status_start:
    #    case '4':
    #        status['401-499'] = status['401-499'] + 1


def output_the_states():
    print(total_link_status)
    print("Total link's validity: {value}%".format(value="{:.2f}".format(total_link_status['Valid links']/total_link_status['Total links'] * 100)))

#main method
def main():
    
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', "--directory", action='store')

    args = parser.parse_args()

    #look up and make the requests to link to get the response code
    lookup_link(args.directory)

    #output the stats
    output_the_states()



if __name__ == "__main__":
    main()

    



