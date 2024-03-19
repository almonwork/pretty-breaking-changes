A simple script that searches for commits with a keyword to identify breaking changes, generating a markdown report.

To use the script, you need to configure a few internal variables (to be improved soon)

`repo_path = "/home/yo/src/liferay-portal-ee"`: the path to your repository. Whatever branch the repo is in, will be used.

`start_hash = "cc606f7664a2dab29e08312a225899f140233088"`: the start of the range of commits to consider

`end_hash = "f63d698232b7b620536bb32f854286b132fcc07a"`: the end of the range of commits to consider

