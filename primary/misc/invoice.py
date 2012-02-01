#! /usr/bin/python

__author__ = 'tri1@umbc.edu'

# Patrick Trinkle
# Spring 2012
#
# Given a CSV, it'll build a .tex file for the invoice.
#

import sys

class Expense:
  """
  Container for holding an expense.
  """
  def __init__(self, details):
    self.name = details[0].replace("#", "\#")
    self.date = details[1]
    self.cat = details[2]
    self.total = details[3].replace("$", "").strip()
    self.effective = details[4].replace("$", "").strip()
  
  def __str__(self):
    return "%s & %s & %s &  %s & %s" % (self.name, self.date, self.cat, self.total, self.effective)

def usage():
  sys.stderr.write("usage: %s <input.csv> number <output.tex>\n" % sys.argv[0])

def main():

  if len(sys.argv) != 4:
    usage()
    sys.exit(-1)

  input_file = sys.argv[1]  
  num_val = int(sys.argv[2])
  output_file = sys.argv[3]
  
  # ---------------------------------------------------------------------------
  
  # (num_val)
  header = \
  """
\\documentclass[11pt]{article}
\\usepackage{amssymb,amsmath}
\\usepackage{dsfont}
\\usepackage{times}
\\usepackage[left=1in, right=1in, top=1in, bottom=0.5in, includefoot]{geometry}
\\setlength\\parindent{0.25in}
\\setlength\\parskip{1mm}

% This package is for including our graph
\\usepackage{graphicx}
  """
  
  inv = \
  """
\\title{Invoice \#%d}
\\author{Patrick Trinkle}
\\date{\\today}

\\begin{document}

\\maketitle

\\section{Introduction}
  """
  
  # fill with (shared, house, bills)
  intro = \
  """
This invoice covers the following expenses. In this table, ``shared'' expenses at %d\\%% and ``house'' at %d\\%% and ``bills'' at %d\\%%.
  """
  
  table_top = \
  """
\section{Expenses}

% Items  Date  Type  Value  Net Value
\\begin{tabular}{| l | r | l | r | r |}
\\hline
\\textbf{Item} & \\textbf{Date} & \\textbf{Type} & \\textbf{Value (\$)} & \\textbf{Net Value (\$)}\\\\
\\hline
"""
  
  # (expense, date, total_cost, percentage_cost)
  item = """%s\\\\ \n"""
  
  # (sum)
  bottom = \
  """
\\hline
\\multicolumn{4}{|l|}{\\textbf{Total:}} & %s \\\\
\\hline
\\end{tabular}
\\end{document}
  """

  # ---------------------------------------------------------------------------
  
  # Pull invoice entries from csv file.
  with open(input_file, "r") as f:
    entries = f.readlines()

  # ---------------------------------------------------------------------------
  
  expenses = []

  for entry in entries:
    expenses.append(Expense(entry.strip().split(",")))
  
  shared = 12
  house = 50
  bills = 40
  
  output = header
  output += inv % num_val
  output += intro % (shared, house, bills)
  output += table_top
  
  total = 0.0
  
  for exp in expenses:
    output += item % exp
    total += float(exp.effective)
  
  output += bottom % total
  
  with open(output_file, "w") as f:
    f.write(output)

if __name__ == "__main__":
  main()
