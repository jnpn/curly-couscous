from slugify import slugify
from gitlab import Gitlab

'''
r = repo(url, token)

r.milestone(m).open()

r.milestone(m).close()

r.milestone(m).shift(ONE_STEP | ALL)

'''

from secrets import private_token

class Flow(Gitlab):

    def __init__(self):
        super().__init__(private_token=private_token)
        self.cache = {}

    def list_projects(self):
        m = {}
        self.cache['projects'] = m
        for p in self.projects.list(visibility="private", all=True):
            m[p.id] = p
            print(p)

    def running_branches(self):
        '''Ordered list of branches'''
        return ['dev', 'preprod', 'prod']

    def feature_branch_marker(self, marker='feat-'):
        return marker

    def open(self, p, m, prefix='Draft: '):
        p = self.projects.get(p)
        print(f'{p=} created')
        for issue in p.milestones.get(m).issues():
            name = slugify(issue.title)
            print(f'{issue.iid}-{name=}')
            branch = p.branches.create({'branch': name, 'ref': 'main'})
            mr = f'{prefix}merge {name}'
            print(f'{mr=} created')
            p.mergerequests.create({'source_branch': name,
                                    'target_branch': 'main',
                                    'title': mr,
                                    'labels': ['flow']})

    def clean_branches(self, p, exclude=['main']):
        for b in p.branches.list():
            if b.name not in exclude:
                b.delete()
                print(f'{b=} deleted')

    def clean_mr(self, p):
        for m in p.mergerequests.list():
            m.delete()
            print(f'{m=} deleted')

    def close(self, m):
        for issue in self.milestone(m).issues():
            branch = issue.branch
            mr = branch.merge_request()
            if mr.is_mergeable:
                mr.close()

    def shift(self, m, fully=False):
        rb = self.running_branches()
        runs = rb if fully else rb[:1]
        for b in runs:
            b.checkout()
            b.merge(m.last_merge_commit)

def main(self):
    g = Flow()
    g.list_projects()
