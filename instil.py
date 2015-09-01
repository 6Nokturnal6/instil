__all__ = ["instil", "timelog"]

import pickle, os, sys
from datetime import datetime, timedelta
from utils.argparse_utils import *

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
        
        def cancel_task(self):
                if self._active != None:
                        print("Canceled task active since %s: '%s'" % (self._active))
                self._active = None
        
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
        
        def save(self, to_file):
                pickle.dump(self, open(to_file, 'w'))
        
        @staticmethod
        def load(from_file):
                return pickle.load(open(from_file))
                        
        @staticmethod
        def _print_tree(root, depth=0, since=datetime.fromtimestamp(0)):
                for proj, t in root.items():
                        s = sum([x[1] for x in t['time'] if x[0] >= since], timedelta()).total_seconds()
                        if s > 0:
                                print("%s%s: %f" % ("  "*depth, proj, s/ (60 * 60)))
                                timelog._print_tree(t['children'], depth=depth+1, since=since)

class instil (object):

        default_state = "~/.instil/timelog.pickle"

        def __init__(self):
                self.timelog = None
        
        def load(self, no_new=False):
                try:
                        self.timelog = timelog.load(os.path.expanduser(instil.default_state))
                except IOError as e:
                        if no_new:
                                raise e
                        else:
                                self.timelog = timelog()
                                print("A new time log has been created.")
        
        def show(self, args):
        
                if all([getattr(args, x) == False for x in ['lastmonth', 'lastweek', 'month', 'week', 'yesterday', 'today', 'status']]):
                        args.status = True
                
                
        
        def start(self, args):
                pass
        
        def stop(self, args):
                pass
        
        def main(self):
                parser = ArgumentParser(add_help=False)
                parser.add_argument("-h, --help", action=ArgumentParserExceptionAction)
                subparsers = parser.add_subparsers(dest="command")
                
                start = subparsers.add_parser('start')
                start.add_argument(
                        "-a, --at",
                        dest="at",
                        default=datetime.now(),
                        action=ArgumentParserParseDateTimeAction,
                        help="specify the time that the task started",
                        metavar="time"
                )
                start.add_argument(
                        "path",
                        nargs="+",
                        type=str,
                        help="a word or sequence which identifies the category and/or task",
                        metavar="task_id"
                )
                start.add_argument(
                        "-y, --yes",
                        dest="yes",
                        action='store_true',
                        help="automatically agree to any prompts"
                )
                
                stop = subparsers.add_parser('stop')
                stop.add_argument(
                        "-a, --at",
                        dest="at",
                        default=datetime.now(),
                        action=ArgumentParserParseDateTimeAction,
                        help="specify the time that the task stopped",
                        metavar="time"
                )
                
                show = subparsers.add_parser('show')
                show.add_argument(
                        "-w, --week",
                        dest="week",
                        action='store_true',
                        help="select the current week for display"
                )
                show.add_argument(
                        "-l, --lastweek",
                        dest="lastweek",
                        action='store_true',
                        help="select the previous week for display"
                )
                show.add_argument(
                        "-m, --month",
                        dest="month",
                        action='store_true',
                        help="select the current month for display"
                )
                show.add_argument(
                        "-L, --lastmonth",
                        dest="lastmonth",
                        action='store_true',
                        help="select the previous month for display"
                )
                show.add_argument(
                        "-d, --detail",
                        dest="detail",
                        action='store_true',
                        help="show a detailed timetable instead of a summary"
                )
                show.add_argument(
                        "-t, --today",
                        dest="today",
                        action='store_true',
                        help="show detailed information for today"
                )
                show.add_argument(
                        "-y, --yesterday",
                        dest="yesterday",
                        action='store_true',
                        help="show detailed information for yesterday"
                )
                show.add_argument(
                        "-s, --status",
                        dest="status",
                        action='store_true',
                        help="display only the status of the current task (default)"
                )
                        
                parser.set_default_subparser('show')

                try:
                        args = parser.parse_args()
                except ArgumentParserException:
                        print("usage: %s <command> [<args>]" % (sys.argv[0]))
                        print("")
                        print("The available commands are: ")
                        print("  start   Begin a new task")
                        print("  stop    Stop the current task")
                        print("  show    Display information (default)")
                        print("")
                        print("Use '%s <command> -h' for help on a specific command." % sys.argv[0])
                        return
                        
                if args.command == "show":
                        self.show(args)
                elif args.command == "start":
                        self.start(args)
                elif args.command == "stop":
                        self.stop(args)
                else:
                        raise Exception("Unknown command: %s" % args.command)
