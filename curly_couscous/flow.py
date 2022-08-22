from gitlab import Gitlab
from slugify import slugify

"""
r = repo(url, token)

r.milestone(m).open()

r.milestone(m).close()

r.milestone(m).shift(ONE_STEP | ALL)

"""

from secrets import private_token

class Project:

    def __init__(self, name, id=None):
        self.name = name
        self.p = None

    def is_created(self):
        return self.p is not None

    def create(self):
        # p = gitlab.projects.create
        # self.p = p
        pass

    def delete(self):
        # p = gitlab.projects.get(self.p).delete()
        # self.p = None

    def commit(self, p):
        data = {
            'branch': 'main',
            'commit_message': 'blah blah blah',
            'actions': [
                {
                    'action': 'create',
                    'file_path': 'README.rst',
                    'content': b'yolo',
                },
                {
                    # Binary files need to be base64 encoded
            'action': 'create',
                    'file_path': 'logo.png',
                    'content': base64.b64encode('x0x0x0x0x0yolo'),
                    'encoding': 'base64',
                }
            ]
        }
        commit = p.commits.create(data)

    def issue(self, name, desc):
        pass

    def branch(self, name, issue=None):
        pass

    def mr(self, name, desc, issue=None, branch=None):
        pass

class Flow(Gitlab):
    def __init__(self):
        super().__init__(private_token=private_token)
        self.cache = {}

    def list_projects(self):
        m = {}
        self.cache["projects"] = m
        for p in self.projects.list(visibility="private", all=True):
            m[p.id] = p
            print(p)

    def running_branches(self):
        """Ordered list of branches"""
        return ["dev", "preprod", "prod"]

    def feature_branch_marker(self, marker="feat-"):
        return marker

    def open(self, p, m, prefix="Draft: "):
        p = self.projects.get(p)
        print(f"using {p=}")
        for issue in p.milestones.get(m).issues():
            branch_name = f"{issue.iid}-{slugify(issue.title)}"
            print(f"{branch_name=}")
            branch = p.branches.create({"branch": branch_name, "ref": "main"})
            mr_title = f"{prefix}merge {branch_name}"
            print(f"{mr_title=} created for {branch=}")
            mr = p.mergerequests.create(
                {
                    "source_branch": branch_name,
                    "target_branch": "main",
                    "title": mr_title,
                    "labels": ["flow"],
                }
            )
            print(f"trying to link #{issue.iid} to !{mr.iid}")
            issue.description = f"!{mr.iid}"
            issue.save()

    def clean_branches(self, p, exclude=["main"]):
        for b in p.branches.list():
            if b.name not in exclude:
                b.delete()
                print(f"{b=} deleted")

    def clean_mr(self, p):
        for m in p.mergerequests.list():
            m.delete()
            print(f"{m=} deleted")

    def close(self, p, m):
        """
        p / m -> issues -> mr -> foreach mr.close
        """
        for i in p.issues.list():
            m, *rs = i.related_merge_requets()
            if m:
                mr = p.mergerequests.get(m["iid"])
                if not mr.has_conflicts:
                    mr.close()

    def shift(self, m, fully=False):
        rb = self.running_branches()
        runs = rb if fully else rb[:1]
        for b in runs:
            b.checkout()
            b.merge(m.last_merge_commit)


def main():
    g = Flow()
    P = g.projects.get(38763378)
    M = P.milestones.get(2744050)
    g.open(P.id, M.id)
