InSTiL:
-

#### An *In*credibly *S*imple *Ti*me *L*ogger  


InSTiL is a simple command-line utility which you can use to log time. It makes it easy to track how much time you spend on each of your several projects.

###Task paths:

Tasks in InSTiL are categorized hierarchically. For example, you might have a broad category of tasks called "homework" and subcategories for "calculus," "physics," "chemistry," etc. These subcategories may even have their own subcategories.

To identify a task in InSTiL, you assign it a **path**. A path is simply a string of categories, ordered from least-specific to most-specific, which identifies the task as uniquely as you would like.

An example path to identify a specific task would be:

    homework chemistry lab.report
    
This would logically refer to a task "lab.report" in the category "chemistry," which is a subcategory of "homework."

###Usage:

To log time spent on a task, you must notify InStil when you are starting your work and when you are stopping it.

To start a task:

    instil start <path ...>
    
For example,
    
    instil start homework chemistry lab.report

Then, to stop and log the time:

    instil stop

If you have accidentally started a task that you do not want to log, use this command:

    instil cancel

Note that you do not need to specify the task you are stopping or canceling. It is assumed that only one task can be active at a time, so there is no ambiguity.
    
If you have already started or stopped a task but forgot to notify InSTiL, you can specify a time or offset when you invoke InSTiL:

    instil start <path ...> --at "3:19 PM"
    instil stop --at "5 minutes ago"

You can check if any task is active by simply invoking instil without any arguments.

To display a summary logged time, you invoke InSTiL with a parameter corresponding to the amount of time you want to summarize:

    instil show -t      # show time logged today
    instil show -y      # show time logged yesterday
    instil show -w      # show time logged this week
    instil show -l      # show time logged last week
    instil show -m      # show time logged this month
    instil show -L      # show time logged last month

You can combine as many of these parameters as you want to display multiple subsets of data at once. You can also specify the '-d' parameter to show a detailed view. The detailed view will list the time intervals spent on each task, for each day in the requested view.

### Other info

InSTiL keeps its data file in ~/.instil/. The directory will be created if it does not exist. If you want to delete your logged time, delete this directory.