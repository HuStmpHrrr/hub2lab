## Smooth migration to Gitlab (or any other Git hosts)

This script is written so that migration from Github to any other places can go
smoothly.

### Steps

1. Create a Gitlab account. Inside of Gitlab project creation, you can choose to
   import projects from Github, which will import all branches from your original
   projects hosted on Github.
   
1. Modify `decs.json`, the fields of which should be comprehensive. You will just need
   to enumerate the name of the projects.
   
1. `./run.py decs.json /tmp` will wipe your the history of master branches of all
   projects on Github, and forcibly replace the project with a README file that
   contains a url pointing to the new addresses.

