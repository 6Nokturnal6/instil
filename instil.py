__all__ = ["instill", "timelog"]

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
                                        srch[path[0]] = {'children': {}, 'time': timedelta()}
                                print("%f hours logged for %s" % (dura.total_seconds() / 3600, path[0]))
                                srch[path[0]]['time'] += dura
                                srch = srch[path[0]]['children']
                                path = path[1:]
                        self._active = None
        
        def get_time(self, path=[]):
        
                if len(path) == 0:
                        return sum([y['time'] for x, y in self._projects.items()], timedelta())
                        
                accu = timedelta()
                while len(path) > 0:
                        if path[0] in srch:
                                accu += srch[path[0]]['time']
                                srch = srch[path[0]]['children']
                                path = path[1:]
                        else:
                                raise Exception("Requested path doesn't exist: %s", ".".join(path))
        @staticmethod
        def print_tree(root, depth=0):
                for proj, t in root.items():
                        print("%s%s: %f" % ("  "*depth, proj, t['time'].total_seconds() / (60 * 60)))
                        timelog.print_tree(t['children'], depth+1)

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
                
                my_log.begin_task(path1, at=datetime.now() - timedelta(hours=1, minutes=15))
                my_log.begin_task(path2, at=datetime.now() - timedelta(hours=1, minutes=10))
                my_log.begin_task(path3, at=datetime.now() - timedelta(hours=0, minutes=55))
                my_log.begin_task(path4, at=datetime.now() - timedelta(hours=0, minutes=45))
                my_log.begin_task(path5, at=datetime.now() - timedelta(hours=0, minutes=15))
                my_log.end_task()
                print("total time: %f" % (my_log.get_time().total_seconds() / 3600))
                
                timelog.print_tree(my_log._projects)
                        
