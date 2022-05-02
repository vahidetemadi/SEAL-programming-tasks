from unittest import result
import requests
import argparse
import json
import os
import subprocess


# This program is assumed to take the GitHub repo name,
# (i) returns its general stat
# (ii) counts # of LOC for each PL used in the program
# Author
#       Vahid Etemadi(vetemadi87@gmail.com)

BASE_URL="https://api.github.com"


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
    response = requests.get("{base_url}/repos/{username}/{repo}/commits?per_page=1000".format(base_url=BASE_URL, username=user, repo=repo))
    
    commits = json.loads(response.text)

    return len(commits)

def get_branches_num(user, repo):
    response = requests.get("{base_url}/repos/{username}/{repo}/branches".format(base_url=BASE_URL, username=user, repo=repo))
    
    branches = json.loads(response.text)

    return len(branches)

def get_tags_num(user, repo):
    response = requests.get("{base_url}/repos/{username}/{repo}/tags".format(base_url=BASE_URL, username=user, repo=repo))
    
    tags = json.loads(response.text)

    return len(tags)

def get_releases_num(user, repo):
    response = requests.get("{base_url}/repos/{username}/{repo}/releases".format(base_url=BASE_URL, username=user, repo=repo))
    
    releases = json.loads(response.text)

    return len(releases)

def get_evns_num(user, repo):
    response = requests.get("{base_url}/repos/{username}/{repo}/environments".format(base_url=BASE_URL, username=user, repo=repo))
    
    environments = json.loads(response.text)

    return len(environments)

#TODO take care of closed issues

def get_closed_issues_num(user, repo):
    response = requests.get("{base_url}/search/issues?q=repo:{username}/{repo}+type:issues+state:closed")

    return json.loads(response.text)['total_counts']

def fill_repo_stat(user, repos):

    repo_objects = {}
    for repo in repos:
        print(repo)
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
        repo_objects[repo['name']] = repo_obj
    
    return repo_objects

def compute_stats_median(repo_objs):
    repos_stats_median = {}
    for key, value in repo_objs.items():
        repos_stats_median['commits_median'] = "TBC"


def get_list_of_repos(user):
    response = requests.get("{base_url}/users/{username}/repos".format(base_url=BASE_URL, username=user))

    #log the resopnse status code
    print("Status-->" + str(response.status_code))

    repos = json.loads(response.text)

    return repos


def analyze_cloc_output(message):
    """Add information LOC, total files, blank and commented lines using CLOC for the entire repository
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
        #os.system('cloc {repo}/'.format(repo=repo['name']))



def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', "--user", action='store')
    parser.add_argument('-a', '--action', choices=['stat', 'LOC'])

    args = parser.parse_args()

    repos = get_list_of_repos(args.user)

    if args.action == 'stat':
        repos_stats = fill_repo_stat(repos, args.user)
        compute_stats_median(repos_stats)
    elif args.action =='LOC':
        return_repo_LOC(repos, args.user)




if __name__ == "__main__":
    main()