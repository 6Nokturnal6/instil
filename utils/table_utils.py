__all__ = ['Table']

import textwrap

# based on http://stackoverflow.com/questions/28815268
class Table:

    def __init__(self, contents, wrap, colDelim = "|", rowDelim = "-"):

        self.contents = contents
        self.wrap = wrap
        self.colDelim = colDelim
        
        if len(contents) > 0:

                # Extra rowDelim characters where colDelim characters are
                p = len(self.colDelim) * (len(contents[0]) - 1)

                # Line gets too long for one concatenation
                self.rowDelim = self.colDelim
                self.rowDelim += rowDelim * (self.wrap * max([len(i) for i in contents]) + p)
                self.rowDelim += self.colDelim + "\n"

    def __str__(self):
        if len(self.contents) == 0:
                return "(No data)"
        string = self.rowDelim
        l = [[textwrap.wrap(col, self.wrap) for col in row] for row in self.contents]
        for row in l:
            for n in range(max([len(i) for i in row])):
                string += self.colDelim
                for col in row:
                    if n < len(col):
                        string += col[n].ljust(self.wrap)
                    else:
                        string += " " * self.wrap
                    string += self.colDelim
                string += "\n"
            string += self.rowDelim
        return string.replace("\x00"," ")
