__all__ = ["instil", "timelog"]

import pickle, os, sys, calendar, time
from datetime import datetime, timedelta
from utils.argparse_utils import *
from utils.input_utils import *
from utils.table_utils import *

class timelog (object):

        format_str = "%I:%M %p, %a %b %d"
        time_fmt_s = "%I:%M %p"
        
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
                print("Task %s started at %s." % (".".join(path), at.strftime(timelog.format_str)))
        
        def cancel_task(self):
                if self._active != None:
                        print("Canceled task %s, active since %s." % (".".join(self._active[0]), self._active[1].strftime(timelog.format_str)))
                else:
                        print("No active task to cancel.")
                self._active = None
        
        def end_task(self, at=datetime.now()):
                if self._active != None:
                        path = self._active[0]
                        dura = at - self._active[1]
                        srch = self._projects
                        print("Task %s ended at %s (%f hours)." % (".".join(self._active[0]), at.strftime(timelog.format_str), dura.total_seconds() / 3600))
                        while len(path) > 0:
                                if not path[0] in srch:
                                        srch[path[0]] = {'children': {}, 'time': []}
                                srch[path[0]]['time'].append((self._active[1], dura))
                                srch = srch[path[0]]['children']
                                path = path[1:]
                        self._active = None
        
        def get_time(self, path=[], since=datetime.fromtimestamp(0), until=datetime.now()):
        
                if len(path) == 0:
                        return sum([sum([z[1] for z in y['time'] if z[0] >= since and z[0] <= until], timedelta()) for x, y in self._projects.items()], timedelta())
                        
                srch = self._projects
                try:
                        while len(path) > 1:
                                if path[0] in srch:
                                        srch = srch[path[0]]['children']
                                        path = path[1:]
                        return sum([x[1] for x in srch[path[0]]['time'] if x[0] >= since and x[0] <= until], timedelta())
                except KeyError:
                        raise Exception("Path not found: %s" % path)
        
        def _crawl(self, node, specs, since, until, history=[]):
                for x, y in node.items():
                        for z in y['time']:
                                tmp = history[:]
                                tmp.append(x)
                                if z[0] >= since and z[0] <= until:
                                        specs[z] = tmp
                                self._crawl(y['children'], specs, since, until, history=tmp)
                
        def print_details(self, since=datetime.fromtimestamp(0), until=datetime.now()):
                weeks = {}
                specs = {}
                table = []
                self._crawl(self._projects, specs, since, until)
                
                for (start, dur), key in specs.items():
                        start_day_dt = start.replace(hour=0, minute=0, second=0, microsecond=0)
                        start_day  = int(start_day_dt.strftime("%w"))
                        start_week = int((start_day_dt - timedelta(days=start_day)).strftime("%s"))
                        if not start_week in weeks:
                                weeks[start_week] = [[] for x in range(0, 7)]
                        weeks[start_week][start_day].append((key, start, dur))

                for week, x in sorted(weeks.items(), key=lambda(a, b): a):
                        table.append([])
                        for day_i in range(0, 7):
                                day = x[day_i]
                                if len(day) == 0 and (until - since) < timedelta(days=7):
                                        continue
                                t = datetime.fromtimestamp(week) + timedelta(days = (day_i))
                                table[-1].append([t.strftime("%b %-d")])
                                total = timedelta()
                                for task, start, dur in sorted(day, key=lambda x: x[1]):
                                        table[-1][-1].append(" ")
                                        table[-1][-1].append("%s - %s" % (start.strftime(timelog.time_fmt_s), (start + dur).strftime(timelog.time_fmt_s)))
                                        table[-1][-1].append("%s" % "/".join(task))
                                        total += dur
                                table[-1][-1].append(" ")
                                table[-1][-1].append("\x08Total: %.2f hours\x07" % (total.total_seconds() / 3600))
                                table[-1][-1] = "\t\t\t\t\x00".join(table[-1][-1])
                print(Table(table, 21))

        def print_tree(self, since=datetime.fromtimestamp(0), until=datetime.now()):
                timelog._print_tree(self._projects, since=since, until=until)
        
        def print_var(self, verbose=False, since=datetime.fromtimestamp(0), until=datetime.now()):
                if verbose:
                        self.print_details(since, until)
                else:
                        self.print_tree(since, until)
                        print("Total: %f hours" % (self.get_time(since=since, until=until).total_seconds() / 3600))
        
        def save(self, to_file):
                pickle.dump(self, open(to_file, 'w'))
        
        @staticmethod
        def load(from_file):
                return pickle.load(open(from_file))
                        
        @staticmethod
        def _print_tree(root, depth=0, since=datetime.fromtimestamp(0), until=datetime.now()):
                for proj, t in root.items():
                        s = sum([x[1] for x in t['time'] if x[0] >= since and x[0] <= until], timedelta()).total_seconds()
                        if s > 0:
                                print("%s%s: %f" % ("  "*depth, proj, s/ (60 * 60)))
                                timelog._print_tree(t['children'], depth=depth+1, since=since, until=until)

class instil (object):

        default_state = "~/.instil/timelog.pickle"

        def __init__(self):
                self.timelog = None
                self.statefile = os.path.expanduser(instil.default_state)
        
        def load(self, no_new=False):
                try:
                        self.timelog = timelog.load(self.statefile)
                except IOError as e:
                        if no_new:
                                raise e
                        else:
                                self.timelog = timelog()
                                print("A new time log has been created.")
                        
        def save(self):
                if not os.path.exists(os.path.dirname(self.statefile)):
                        os.makedirs(os.path.dirname(self.statefile))
                self.timelog.save(self.statefile)
        
        def show(self, args):
                if all([getattr(args, x) == False for x in ['lastmonth', 'lastweek', 'month', 'week', 'yesterday', 'today', 'alltime', 'status']]):
                        args.status = True
                
                try:
                        self.load(True)
                except IOError:
                        print("You don't seem to have any time logged yet.")
                        print("Try '%s -h' to find out how to start using InSTiL." % sys.argv[0])
                        return
                
                if args.status:
                        cur = self.timelog.current_task()
                        if cur == None:
                                print("No task is active.")
                        else:
                                print("Active task is %s, since %s." % (".".join(cur[0]), cur[1].strftime(timelog.format_str)))
                        print("")
                
                if args.alltime:
                        print("%s for all time:" % ("Details" if args.detail else "Summary"))
                        self.timelog.print_var(args.detail)
                        print("")
                
                if args.lastmonth:
                        lmm, lmy = time.localtime().tm_mon, time.localtime().tm_year
                        lmm -= 1
                        if lmm < 1:
                                lmy -= 1
                                lmm += 12
                        mo = timedelta(days=calendar.monthrange(lmy, lmm)[1])
                        begin = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0) - mo
                        end = begin + mo
                        print("%s for %s %d:" % ("Details" if args.detail else "Summary", calendar.month_name[lmm], lmy))
                        self.timelog.print_var(args.detail, since=begin, until=end)
                        print("")
                
                if args.month:
                        lmm, lmy = time.localtime().tm_mon, time.localtime().tm_year
                        begin = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                        mo = timedelta(days=calendar.monthrange(lmy, lmm)[1])
                        end = begin + mo
                        print("%s for %s %d:" % ("Details" if args.detail else "Summary", calendar.month_name[lmm], lmy))
                        self.timelog.print_var(args.detail, since=begin, until=end)
                        print("")
                
                if args.lastweek:
                        dow = int(datetime.now().strftime("%w"))
                        begin = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=dow+7)
                        lmy, lmm, lmd = begin.year, begin.month, begin.day
                        end = begin + timedelta(days=7)
                        print("%s for week of %s %d, %d:" % ("Details" if args.detail else "Summary", calendar.month_name[lmm], lmd, lmy))
                        self.timelog.print_var(args.detail, since=begin, until=end)
                        print("")
                
                if args.week:
                        dow = int(datetime.now().strftime("%w"))
                        begin = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=dow)
                        lmy, lmm, lmd = begin.year, begin.month, begin.day
                        end = begin + timedelta(days=7)
                        print("%s for week of %s %d, %d:" % ("Details" if args.detail else "Summary", calendar.month_name[lmm], lmd, lmy))
                        self.timelog.print_var(args.detail, since=begin, until=end)
                        print("")
                
                if args.yesterday:
                        begin = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days = 1)
                        lmy, lmm, lmd = begin.year, begin.month, begin.day
                        end = begin + timedelta(days=1)
                        print("%s for %s %d, %d:" % ("Details" if args.detail else "Summary", calendar.month_name[lmm], lmd, lmy))
                        self.timelog.print_var(args.detail, since=begin, until=end)
                        print("")
                
                if args.today:
                        begin = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
                        lmy, lmm, lmd = begin.year, begin.month, begin.day
                        end = begin + timedelta(days=1)
                        print("%s for %s %d, %d:" % ("Details" if args.detail else "Summary", calendar.month_name[lmm], lmd, lmy))
                        self.timelog.print_var(args.detail, since=begin, until=end)
                        print("")
                

        def start(self, args):
                try:
                        self.load(not args.yes)
                except IOError:
                        print("No existing InSTiL log was found.")
                        if query_yes_no("Would you like to create a new file?"):
                                self.timelog = timelog()
                                print("")
                        else:
                                print("Cannot continue without creating a data file.")
                                return
                if self.timelog.task_exists(args.path) or args.yes or query_yes_no("This task does not exist. Would you like to create it?"):
                        self.timelog.begin_task(args.path, at=args.at)
                        self.save()
                else:
                        print("No action taken.")
        
        def stop(self, args):
                try:
                        self.load(True)
                except IOError:
                        print("No existing InSTiL log was found.")
                        print("Cannot continue without existence of a data file.")
                self.timelog.end_task(at=args.at)
                self.save()
        
        def cancel(self, args):
                try:
                        self.load(True)
                except IOError:
                        print("No existing InSTiL log was found.")
                        print("Cannot continue without existence of a data file.")
                self.timelog.cancel_task()
                self.save()
        
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
                
                cancel = subparsers.add_parser('cancel')
                
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
                        help="show information for today"
                )
                show.add_argument(
                        "-y, --yesterday",
                        dest="yesterday",
                        action='store_true',
                        help="show information for yesterday"
                )
                show.add_argument(
                        "-a, --alltime",
                        dest="alltime",
                        action='store_true',
                        help="show information for all time"
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
                        print("  cancel  Cancel the current task")
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
                elif args.command == "cancel":
                        self.cancel(args)
                else:
                        raise Exception("Unknown command: %s" % args.command)
