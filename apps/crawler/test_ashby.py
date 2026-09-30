import requests
import json

url2 = "https://jobs.ashbyhq.com/api/non-user-graphql?op=ApiJobBoardWithTeams"
payload = {
    "operationName": "ApiJobBoardWithTeams",
    "variables": {"organizationHostedJobsPageName": "reddit"},
    "query": "query ApiJobBoardWithTeams($organizationHostedJobsPageName: String!) { jobBoard: jobBoardWithTeams(organizationHostedJobsPageName: $organizationHostedJobsPageName) { teams { id name } jobPostings { id title locationName employmentType teamId isRemote secondaryLocations { locationName } } } }"
}
resp = requests.post(url2, json=payload)
print(resp.json())
