__all__ = ["instil", "timelog"]

import argparse
from datetime import datetime, timedelta

class timelog (object):
        
        def __init__(self):
                self._active = None
                self._projects = {}
        
        def task_exists(self, path):
                path = path[:]
                srch = self._projects
                
                if len(path) == 0:
                        return False
                        
                while len(path) > 0:
                        if path[0] in srch:
                                srch = srch[path[0]]['children']
                                path = path[1:]
                        else:
                                return False
                                
                return True
        
        def current_task(self):
                return self._active
        
        def begin_task(self, path, at=datetime.now()):
                if self._active != None:
                        self.end_task(at)
                if len(path) == 0:
                        return False
                self._active = (path, at)
        
        def end_task(self, at=datetime.now()):
                if self._active != None:
                        path = self._active[0]
                        dura = at - self._active[1]
                        srch = self._projects
                        while len(path) > 0:
                                if not path[0] in srch:
                                        srch[path[0]] = {'children': {}, 'time': []}
                                print("%f hours logged for %s" % (dura.total_seconds() / 3600, path[0]))
                                srch[path[0]]['time'].append((self._active[1], dura))
                                srch = srch[path[0]]['children']
                                path = path[1:]
                        self._active = None
        
        def get_time(self, path=[], since=datetime.fromtimestamp(0)):
        
                if len(path) == 0:
                        return sum([sum([z[1] for z in y['time'] if z[0] >= since], timedelta()) for x, y in self._projects.items()], timedelta())
                        
                srch = self._projects
                try:
                        while len(path) > 1:
                                if path[0] in srch:
                                        srch = srch[path[0]]['children']
                                        path = path[1:]
                        return sum([x[1] for x in srch[path[0]]['time'] if x[0] >= since], timedelta())
                except KeyError:
                        raise Exception("Path not found: %s" % path)

        def print_tree(self, since=datetime.fromtimestamp(0)):
                timelog._print_tree(self._projects, since=since)
                        
        @staticmethod
        def _print_tree(root, depth=0, since=datetime.fromtimestamp(0)):
                for proj, t in root.items():
                        s = sum([x[1] for x in t['time'] if x[0] >= since], timedelta()).total_seconds()
                        if s > 0:
                                print("%s%s: %f" % ("  "*depth, proj, s/ (60 * 60)))
                                timelog._print_tree(t['children'], depth=depth+1, since=since)

class instil (object):

        def __init__(self):
                pass
        
        def main(self):
                my_log = timelog()
                
                path1 = ["foo", "bar", "baz"]
                path2 = ["foo"]
                path3 = ["foo", "bar"]
                path4 = ["foo", "bing"]
                path5 = ["fizz", "buzz"]
                
                n = datetime.now()
                
                my_log.begin_task(path1, at=n - timedelta(hours=1, minutes=15))
                my_log.begin_task(path2, at=n - timedelta(hours=1, minutes=10))
                my_log.begin_task(path3, at=n - timedelta(hours=0, minutes=55))
                my_log.begin_task(path4, at=n - timedelta(hours=0, minutes=45))
                my_log.begin_task(path5, at=n - timedelta(hours=0, minutes=15))
                my_log.end_task()
                
                since = n - timedelta(minutes=45)
                
                print("total time: %f" % (my_log.get_time(since=since).total_seconds() / 3600))
                
                my_log.print_tree(since=since)
                        
