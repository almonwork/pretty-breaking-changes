A simple script that searches for commits with a keyword to identify breaking changes, generating a html report.

The html report is made of a header, the important information, and the footer (that also includes some javascript logic).

The title of the report can be defined in the header.

To use the script, you need to configure a few internal variables (to be improved soon)

`repo_path = "/home/yo/src/liferay-portal-ee"`: the path to your repository. Whatever branch the repo is in, will be used.

`start_hash = "cc606f7664a2dab29e08312a225899f140233088"`: the start of the range of commits to consider

`end_hash = "f63d698232b7b620536bb32f854286b132fcc07a"`: the end of the range of commits to consider

`template_path = "/home/yo/projects/pretty-breaking-changes"`: the path where the header and the footer can be found (only needed by the html flavour)
