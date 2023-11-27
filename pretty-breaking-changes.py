#! /usr/bin/python3

import git
# import mistune
# import re

repo_path = "/home/yo/src/liferay-portal"
template_path = "/home/yo/projects/pretty-breaking-changes"

# markdown = mistune.create_markdown(renderer='ast')

def get_end_of_block(lines, start_index, pattern):
    if start_index >= len(lines):
        return start_index
    
    end_of_block_index = start_index
    
    while end_of_block_index < len(lines):
        if not lines[end_of_block_index].startswith(pattern):
            end_of_block_index += 1
        else:
            break
    
    # print(end_of_block_index)
    return end_of_block_index
            

def dissect_commit_message(raw_commit_message):
    breaking_changes_info = []
    
    lines = raw_commit_message.split('\n')
    
    raw_jira_info_block_line_index = get_end_of_block(lines, 1, '# breaking')
    
    i = 0
    while i < raw_jira_info_block_line_index:
        if lines[i] != "":
            jira_ticket, _, jira_ticket_title = lines[i].partition(' ')
            break
        i += 1
    
    previous_line_index = raw_jira_info_block_line_index
    
    while previous_line_index < len(lines):
        # print(str(previous_line_index) + " " + str(len(lines)))
        next_line_index = get_end_of_block(lines, previous_line_index, '----')
        # print(next_line_index)
        if next_line_index - previous_line_index > 1:
            info = extract_breaking_change_info(lines[previous_line_index:next_line_index])
            
            if info:
                breaking_changes_info.append(info)
                breaking_changes_info[-1]['jira_ticket'] = jira_ticket
                breaking_changes_info[-1]['jira_ticket_title'] = jira_ticket_title
            else:
                print("unprocessable")
                print(lines[previous_line_index:next_line_index])
                
        previous_line_index = next_line_index + 1
        
    return breaking_changes_info
    

def extract_breaking_change_info(lines):
    # print(lines)
    breaking_change_info = {}
    
    try:
        what_line_index = get_end_of_block(lines, 1, "## What")
        raw_what_header = lines[what_line_index]
        _, _, breaking_change_info['affected_file_path'] = raw_what_header.partition('## What ')
        print(breaking_change_info['affected_file_path'])
        
        why_line_index = get_end_of_block(lines, what_line_index + 1, "## Why")

        breaking_change_info['what_info'] = "\n".join(lines[what_line_index + 1:why_line_index])

        alternatives_line_index = get_end_of_block(lines, why_line_index + 1, "## Alternatives")

        breaking_change_info['why_info'] = "\n".join(lines[why_line_index + 1: alternatives_line_index])
        
        if len(lines) >= alternatives_line_index:
            breaking_change_info['alternatives'] = "\n".join(lines[alternatives_line_index + 1: len(lines)])
                    
    except Exception as e:
        print(e)
        # print(raw_commit_message)
        # print("--")
        return None
    
    return breaking_change_info


repo = git.Repo(repo_path)

print("Retrieving git info ...")

of_interest = repo.git.log("--grep", "breaking_change_report", "--pretty=format:%H")

print("Processing git info ...")

individual_commit_hashes = of_interest.split('\n')

breaking_changes_info_raw = {h:result for h in individual_commit_hashes if (result := dissect_commit_message(repo.commit(h).message))}

affected_file_paths_and_hashes = {}

for hash in breaking_changes_info_raw:
    # print(hash)
    # print(breaking_changes_info_raw[hash]['affected_file_path'])
    
    for change in breaking_changes_info_raw[hash]:
        affected_file_path = change['affected_file_path']
        print(affected_file_path)
        first_level_path, _, remaining = affected_file_path.partition('/')
        
        if len(first_level_path) == 0:
            first_level_path, _, remaining = remaining.partition('/')
            
        if len(remaining) == 0:
            first_level_path = 'other'
            
        if not first_level_path in affected_file_paths_and_hashes:
            affected_file_paths_and_hashes[first_level_path] = {}
        
        if affected_file_path in affected_file_paths_and_hashes[first_level_path]:
            affected_file_paths_and_hashes[first_level_path][affected_file_path].append(hash)
        else:
            affected_file_paths_and_hashes[first_level_path][affected_file_path] = [hash]

print("Generating output ...")

header_fh = open(template_path + '/pretty-breaking-changes_header.html', 'r')
entire_header = header_fh.read()
header_fh.close()

footer_fh = open(template_path + '/pretty-breaking-changes_footer.html', 'r')
entire_footer = footer_fh.read()
footer_fh.close()

entire_output = entire_header

for first_level_path in affected_file_paths_and_hashes:
    this_block = f'''
    <div class="list-group mb-2">
        <div class="list-group-header collapsible" role="button" tabindex="0">
            <div class="list-group-header-title">{first_level_path}</div><span>&#8595;</span>
        </div>
    
        <ul class="list-group-item list-unstyled collapsed">
    '''
    
    for affected_file_path in affected_file_paths_and_hashes[first_level_path]:
        this_block += f'''
            <li class="mb-3">
                <h4 class="file-path list-group-header bg-light h5">
                    <span class="text-truncate">{affected_file_path}</span>
                </h4>
                
                <ul>
        '''
        
        for hash in affected_file_paths_and_hashes[first_level_path][affected_file_path]:
            for change in breaking_changes_info_raw[hash]:
                this_block += '''
                    <li class="list-group-item mb-3">
                        <div class="what-section">
                            <div class="what-section-title">What has changed?</div>
                            <small>{what_info}</small>
                        </div>
                        <div class="why-section">
                            <div class="why-section-title">Why has it changed?</div>
                            <small>{why_info}</small>
                        </div>
                        <div class="see-more-section">
                            <div class="see-more-section-title">Where can I find more?</div>
                            <small>
                                See <a href="https://liferay.atlassian.net/browse/{jira_ticket}">{jira_ticket}</a> {jira_ticket_title}
                            </small>
                        </div>
                    </li>
                '''.format(**change)

            
        this_block += '''
                </ul>
            </li>
        '''
            
    this_block += '''
    </ul>
    '''
    
    entire_output += this_block

entire_output += entire_footer

entire_output_fh = open('report.html', 'w')

entire_output_fh.write(entire_output)

entire_output_fh.close()




