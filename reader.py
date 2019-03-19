
# coding: utf-8

# ### RS
# subreddit | author | hidden | link_flair_css_class | id | is_self | edited | selftext | score | retrieved_on | domain | brand_safe | contest_mode | media | secure_media_embed | created_utc | archived | distinguished | secure_media | locked | thumbnail | url | link_flair_text | over_18 | author_flair_text | suggested_sort | quarantine | subreddit_id | spoiler | stickied | hide_score | author_flair_css_class | permalink | media_embed | title | gilded | num_comments | 
# 
# ### RC
# author | gilded | subreddit | created_utc | edited | controversiality | author_flair_text | parent_id | score | link_id | id | author_flair_css_class | distinguished | stickied | subreddit_id | body | retrieved_on |

# #### API: Fullname Prefix
# 
# - t1_	Comment
# - t2_	Account
# - t3_	Link
# - t4_	Message
# - t5_	Subreddit
# - t6_	Award

# In[14]:


import bz2, json, os, re, random, argparse
from collections import namedtuple, defaultdict


# In[15]:


parser = argparse.ArgumentParser()
parser.add_argument('--file_tag', help='YYYY-MM format identifier for reddit dump file')
parser.add_argument('--output_folder', help='where to put the dialogues.txt file')
parser.add_argument('--n_posts', help='how many posts to gather?')


# In[16]:


# args = parser.parse_args('--file_tag 2011-03 --output_folder sample_data/train --n_posts 100'.split())
args = parser.parse_args()
print(args)


# In[17]:


file_tag = args.file_tag
output_folder = args.output_folder
n_posts = int(args.n_posts)


# In[18]:


allowed_comment_vars = ['author', 'body', 'score', 'parent_id', 'id', 'link_id']
CommentStruct = namedtuple('CommentStruct', ' '.join(allowed_comment_vars))

# Remove newlines and return carraiges from texts
def prep(s):
    s = s.strip()
    s = s.replace('\n', ' ')
    s = s.replace('\r', ' ')
    s = re.sub('[ ]+', ' ', s)
    return s

class Post:
    def __init__(self, **kwargs):
        self.url = kwargs['url']
        self.author = kwargs['author']
        self.subreddit = kwargs['subreddit']
        self.score = kwargs['score']
        self.selftext = kwargs['selftext']
        self.score = kwargs['score']
        self.id = kwargs['id']
        self.num_comments = kwargs['num_comments']
        self.title = kwargs['title']
        self.comments = {}
        
        self.title = prep(self.title)
        self.selftext = prep(self.selftext)
        
    # Maintain a tree structure for comments
    # Root-to-leaf paths using a DFS traversal 
    #  would give data samples for individual conversations
    def add_comment(self, **kwargs):
        kwargs['body'] = prep(kwargs['body'])
        c = CommentStruct(**{key:var for key, var in kwargs.items() if key in allowed_comment_vars})
        self.comments[c.id] = c
    
    def __str__(self):
        s = ""
        for key, val in self.__dict__.items():
            if key != 'comments':
                s += f"{key}:\t{val}\n"
            else:
                s += "\nComments: \n"
                for k,c in val.items():
                    s += f"{c}\n\n"
        return s
        
    def __repr__(self):
        return self.__str__()
    
    def __len__(self):
        return len(self.comments)
    
    def get_dialogues(self):
        # Build the tree
        node_dict = self.comments
        visited = {key: False for key,_ in node_dict.items()}
        visited[self.id] = False

        adj_list = defaultdict(list)
        for t1_id, c in node_dict.items():
            adj_list[c.parent_id].append(t1_id)
        
        # DFS
        # Traverse and return the convs from 
        dialogues = []
        stack = [self.id]
        while len(stack) > 0:
            top = stack[-1]
            
            if top in adj_list:
                push_flag = False
                for neighbor in adj_list[top]:
                    if not visited[neighbor]:
                        stack.append(neighbor)
                        push_flag = True
                        break
                if not push_flag:
                    visited[top] = True
                    stack.pop()
            else:
                # Leaf Node
                visited[top] = True
                # print(stack)
                d = f"{self.title} __eou__"
                for t1_id in stack[1:]:
                    d += f" {self.comments[t1_id].body} __eou__"
                dialogues.append(d)
                # print(d, '\n')
                stack.pop()
        return dialogues


# In[19]:


# accepted_subreddits = ['AskReddit', 'gifts', 'depression']
accepted_subreddits = ['AskReddit', 'gifts', 'depression']


# In[20]:


posts = {}
completion_count = 0
with bz2.BZ2File('./data/RS_%s.bz2' % file_tag, 'r') as fp:
    for i, line in enumerate(fp):
        if len(posts) >= n_posts:
            print(f'Gathered {n_posts} reddit posts for processing. Parsed {i} lines in RS file.')
            break
        curr_post = json.loads(line)
        if 'subreddit' in curr_post:
            if (curr_post['subreddit'] == 'AskReddit') and (curr_post['num_comments'] >= 3):
                print(f'{i}', end='\r')
                # posts.append(curr_post)
                curr_post['id'] = 't3_' + curr_post['id']
                posts[curr_post['id']] = Post(**curr_post)


# In[28]:


with bz2.BZ2File('./data/RC_%s.bz2' % file_tag, 'r') as fp:
    for i, line in enumerate(fp):
        if (i >= 1000*n_posts) or (completion_count == len(posts)):
            print(f'Obtained the comment threads for gathered reddit posts. Parsed {i} lines in RC file. Completion count: {completion_count}')
            break
        print(f'{i:6} | Complete: {completion_count}', end='\r')
        curr_comment = json.loads(line)
        if (curr_comment['subreddit'] == 'AskReddit'):
            curr_comment['id'] = 't1_' + curr_comment['id']
            if curr_comment['link_id'] in posts:
                posts[curr_comment['link_id']].add_comment(**curr_comment)
                if len(posts[curr_comment['link_id']]) == posts[curr_comment['link_id']].num_comments:
                    completion_count += 1
        if completion_count == len(posts):
            print("Stopping code: All comments for posts have been mined.")
            break
        # link = f'https://www.reddit.com/r/{curr_comment["subreddit"]}/comments/{curr_comment["link_id"].split("_")[1]}'        


# In[22]:


print(f'\nNumber of complete discussion-tree found: {completion_count}')


# In[23]:


print(f'\nTotal number of reddit page collected: {len(posts)}')


# In[24]:


matched_ids = [p.id for t3_id, p in posts.items() if len(p.comments) > 0]


# In[32]:


try:
    pk = matched_ids[random.randint(0, len(matched_ids) - 1)]

    p = posts[pk]
    print('\nSample Data:\n')
    print(p.url + '\n')
    for d in p.get_dialogues():
        print(d)
        print()
except ValueError as ve:
    print('\n#########################################')
    print('NO MATCH FOUND. PLEASE INCREASE n_posts.')
    print('#########################################\n')
    raise(ve)


# In[13]:


if not os.path.isdir(output_folder):
    os.makedirs(output_folder)
with open(os.path.join(output_folder, 'dialogues.txt'), 'w') as wf:
    for t3_id, p in posts.items():
        for d in p.get_dialogues():
            wf.write(d + '\n')

