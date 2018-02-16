1. Clone the bare public Github repository to local workspace and push a mirror to the private repository
```bash
git clone --bare git@github.com:TRIP-Lab/itinerum-admin.git
cd itinerum-admin.git
git push --mirror git@gitlab.com:itinerum/itinerum-admin.git
cd ..
rm -rf itinerum-admin.git
```

2. Create a private repository on GitLab and clone to the local workspace.
```bash
git clone git@gitlab.com:itinerum/itinerum-admin.git
cd itinerum-admin
```

Make a small edit to test workflow and push to the private master branch.
```
git commit
git push origin master
```

3. Pull new changes from the public Github repository to the local clone and push updates to GitLab private repository.
```
cd itinerum-admin
git remote add public git@github.com:TRIP-Lab/itinerum-admin.git
git pull public master
git push origin master
```

4. TO DO WHEN UPDATING TO GITHUB MASTER: Create a pull request branch on the public Github repository that the private GitLab branch can push to. This will be a special branch internal to TRIP Lab for allowing easier pushes to open-source code. Other contributors will have to submit pull requests from their own public forks.
```bash
git clone git@github.com:TRIP-Lab/itinerum-admin.git
cd itinerum-admin
git remote add gitlab_private git@gitlab.com:itinerum/itinerum-admin.git
git checkout -b pull_from_gitlab
git pull gitlab_private master
git push origin pull_from_gitlab
```
