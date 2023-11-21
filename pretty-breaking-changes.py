#! /usr/bin/python3

import git
import mistune
import re

repo_path = "/home/yo/src/liferay-portal"
template_path = "/home/yo/projects/pretty-breaking-changes"

markdown = mistune.create_markdown(renderer='ast')

def dissect_commit_message(raw_commit_message):
    breaking_change_info = {}
    
    try:
        aprcm = markdown(raw_commit_message)
    
        raw_jira_info = aprcm[0]['children'][0]['text']
        breaking_change_info['jira_ticket'], _, breaking_change_info['jira_ticket_title'] = raw_jira_info.partition(' ')
    
        raw_what_header = aprcm[2]['children'][0]['text']
        _, _, breaking_change_info['affected_file_path'] = raw_what_header.partition(' ')
    
        breaking_change_info['what_info'] = aprcm[3]['children'][0]['text']
    
        breaking_change_info['why_info'] = aprcm[5]['children'][0]['text']
    except:
        # print(raw_commit_message)
        # print("--")
        return None
    
    return breaking_change_info


repo = git.Repo(repo_path)

of_interest = repo.git.log("--grep", "breaking_change_report", "--pretty=format:%H")

individual_commit_hashes = of_interest.split('\n')

breaking_changes_info_raw = {h:result for h in individual_commit_hashes if (result := dissect_commit_message(repo.commit(h).message))}

affected_file_paths_and_hashes = {}

for hash in breaking_changes_info_raw:
    # print(hash)
    # print(breaking_changes_info_raw[hash]['affected_file_path'])
    
    first_level_path, _, remaining = breaking_changes_info_raw[hash]['affected_file_path'].partition('/')
    
    if len(first_level_path) == 0:
        first_level_path, _, remaining = remaining.partition('/')
        
    if len(remaining) == 0:
        first_level_path = 'Other'
        
    if not first_level_path in affected_file_paths_and_hashes:
        affected_file_paths_and_hashes[first_level_path] = {}
    
    if breaking_changes_info_raw[hash]['affected_file_path'] in affected_file_paths_and_hashes[first_level_path]:
        affected_file_paths_and_hashes[first_level_path][breaking_changes_info_raw[hash]['affected_file_path']].append(hash)
    else:
        affected_file_paths_and_hashes[first_level_path][breaking_changes_info_raw[hash]['affected_file_path']] = [hash]

header_fh = open(template_path + '/pretty-breaking-changes_header.html', 'r')
entire_header = header_fh.read()
header_fh.close()

footer_fh = open(template_path + '/pretty-breaking-changes_footer.html', 'r')
entire_footer = footer_fh.read()
footer_fh.close()

entire_output = entire_header

for first_level_path in affected_file_paths_and_hashes:
    this_block = f'''
    <h3>{first_level_path}</h3>
    
    <ul>
    '''
    
    for affected_file_path in affected_file_paths_and_hashes[first_level_path]:
        this_block += f'''
            <li>
                <h4 class="file-path">{affected_file_path}</h4>
        '''
        
        for hash in affected_file_paths_and_hashes[first_level_path][affected_file_path]:
            # print(affected_file_paths_and_hashes[first_level_path][affected_file_path])
            # print(breaking_changes_info_raw[hash])
            info = breaking_changes_info_raw[hash]
        
            this_block += '''
                <div class="what-section">
                    <h5 class="what-section-title">What has changed?</h5>
                    {what_info}
                </div>
                <div class="why-section">
                    <h5 class="why-section-title">Why has it changed?</h5>
                    {why_info}
                </div>
                <div class="see-more-section">
                    <h5 class="see-more-section-title">Where can I find more?</h5>
                    See <a href="https://liferay.atlassian.net/browse/{jira_ticket}">{jira_ticket}</a> {jira_ticket_title}
                </div>
        '''.format(**info)
    
    this_block += '''
        </li>
    </ul>
    
    '''
    
    entire_output += this_block

entire_output += entire_footer

entire_output_fh = open('report.html', 'w')

entire_output_fh.write(entire_output)

entire_output_fh.close()




