from statistics import median
from unittest import result
import requests
import argparse
import json
import os
import subprocess
import statistics


# This program is assumed to take the GitHub repo name,
# (i) returns its general stat
# (ii) counts # of LOC for each PL used in the program
# Author
#       Vahid Etemadi(vetemadi87@gmail.com)

BASE_URL="https://api.github.com"
REPO_STATS_LIST = {}
TOKEN = ""


class Repo:
    """This the class that is intended to act as a model hold repos's stat
    """
    name = ""
    commits = 0
    stars = 0
    pulls = 0
    forks = 0
    contributors = 0
    branches = 0
    tags = 0
    releases = 0
    closed_issues = 0
    environments = 0


def get_commits_num(user, repo):
    """Counts number of commits for a repo of choice
    """
    response = requests.get("{base_url}/repos/{username}/{repo}/commits?per_page=1000".format(base_url=BASE_URL, username=user, repo=repo), auth=(user, TOKEN))
    
    commits = json.loads(response.text)

    return len(commits)

def get_branches_num(user, repo):
    """Counts number of branches for a repo of choice
    """
    response = requests.get("{base_url}/repos/{username}/{repo}/branches".format(base_url=BASE_URL, username=user, repo=repo), auth=(user, TOKEN))
    
    branches = json.loads(response.text)

    return len(branches)

def get_tags_num(user, repo):
    """Counts number of tags for a repo of choice
    """
    response = requests.get("{base_url}/repos/{username}/{repo}/tags".format(base_url=BASE_URL, username=user, repo=repo), auth=(user, TOKEN))
    
    tags = json.loads(response.text)

    return len(tags)

def get_releases_num(user, repo):
    """Counts number of releases for a repo of choice
    """
    response = requests.get("{base_url}/repos/{username}/{repo}/releases".format(base_url=BASE_URL, username=user, repo=repo), auth=(user, TOKEN))
    
    releases = json.loads(response.text)

    return len(releases)

def get_evns_num(user, repo):
    """Counts number of environments for a repo of choice
    """
    response = requests.get("{base_url}/repos/{username}/{repo}/environments".format(base_url=BASE_URL, username=user, repo=repo), auth=(user, TOKEN))
    
    environments = json.loads(response.text)

    return len(environments)

def get_closed_issues_num(user, repo):
    """Counts number of closed issues for a repo of choice
    """
    response = requests.get("{base_url}/search/issues?q=repo:{username}/{repo}+type:issue+state:closed".format(base_url=BASE_URL,
                            username=user, repo=repo))

    return json.loads(response.text)['total_count']


def fill_repo_stat(user, repos):
    """Assigns value for each stat of each repo
    """
    repo_objects = {}
    for repo in repos:
        repo_name = repo['name']
        repo_obj = Repo()
        repo_obj.name = repo_name
        repo_obj.stars = repo['stargazers_count']
        repo_obj.forks = repo['forks_count']
        repo_obj.commits = get_commits_num(user, repo_name)
        repo_obj.branches = get_branches_num(user, repo_name)
        repo_obj.releases = get_releases_num(user, repo_name)
        repo_obj.tags = get_tags_num(user, repo_name)
        repo_obj.environments = get_evns_num(user, repo_name)
        repo_obj.closed_issues = get_closed_issues_num(user, repo_name)
        print(json.dumps(repo_obj.__dict__))
        repo_objects[repo['name']] = repo_obj.__dict__
    
    return repo_objects

def compute_stats_median(repo_objs):
    """ Takes the dicts of all repos stats, merges values for each stat over all repos,
        and offers the median per each stat over all repos
    """
    repos_stats_median = {}
    for key, value in repo_objs.items():
        #check if total stat dict(which holds list of values for each stat) is empty
        #and if it is, then it sould be initialized
        if REPO_STATS_LIST.__sizeof__ == 0:
            for _key, _value in value.items():
                REPO_STATS_LIST[_key] = [] 
            print(REPO_STATS_LIST)
        for _key, _value in value.items():
            REPO_STATS_LIST[_key].append(value)

    for key, value in REPO_STATS_LIST.items():
        print("The median of stat {stat} is : {median}".format(stat=key, median=str(median(value))))


def get_list_of_repos(user):
    """ Gets list of all repos for a particular username (given as the program param)
    :param user: input github user name
    :return: list of all repos
    """
    response = requests.get("{base_url}/users/{username}/repos".format(base_url=BASE_URL, username=user), auth=(user, TOKEN))
    repos = json.loads(response.text)

    return repos


def analyze_cloc_output(message):
    """Adds information LOC, total files, blank and commented lines using CLOC for the entire repository
    :param message: message from standard output after execution of cloc
    :returns result: dict of the results of the analysis over a repository
    """
    results = {}
    flag = False

    for line in message.strip().split("\n"):
        if flag:
            if line.lower().startswith("sum"):
                break
            elif not line.startswith("-----"):
                digested_split = line.split()
                langauge, files_info = digested_split[:-4], digested_split[-4:]
                language = " ".join(langauge)
                total_files, blank_lines, commented_lines, loc = map(int, files_info)
                language_result = {
                    "total_files": total_files,
                    "blanks": blank_lines,
                    "comments": commented_lines,
                    "loc": loc
                }
                results[language] = language_result

        if line.lower().startswith("language"):
            flag = True

    return results


def compute_LOC_median(repo_name, repo_LOC_dict):
    """ Takes care of computing median for LOCs of all the PLs for a particular repo
    """
    LOCs = []
    for key, value in repo_LOC_dict.items():
        LOCs.append(value['loc'])

    print("Median of LOCs for {repo_name} -----> {meidan}}".format(repo_name=repo_name, median=str(median(LOCs))))


def return_repo_LOC(repos, user):
    """ Takes the repo names, clones those projects and
    calls the cloc to count the LOC by that link
    """
    #create local dir named git_repos
    os.system('mkdir -p git_repos')
    #clone the project to local dir
    for repo in repos:
        os.system('cd git_repos && git clone https://github.com/{user}/{repo}.git'.format(user=user, repo=repo['name']))
        #call cloc for that
        try:
            cloc_command = ['cloc', "git_repos/{repo}".format(repo=repo['name']), '--diff-timeout', '60']
            message = subprocess.check_output(cloc_command).decode("utf-8")
        except subprocess.CalledProcessError as e:
            e.output.decode('utf-8')
        finally:
            subprocess._cleanup()
        print("Repo name-----------> {repo}".format(repo=repo['name']))
        print(message)
        results = analyze_cloc_output(message)
        print(results)
        compute_LOC_median(repo['name'], results)
        #os.system('cloc {repo}/'.format(repo=repo['name']))



def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', "--user", action='store')
    parser.add_argument('-a', '--action', choices=['stat', 'LOC'])
    parser.add_argument('-t', '--token')

    args = parser.parse_args()

    TOKEN = args.token

    repos = get_list_of_repos(args.user)

    if args.action == 'stat':
        repos_stats = fill_repo_stat(args.user, repos)
        compute_stats_median(repos_stats)
    elif args.action =='LOC':
        return_repo_LOC(repos, args.user)




if __name__ == "__main__":
    main()