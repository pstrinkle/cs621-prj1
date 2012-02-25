
import sys


def usage():
  print "%s <database_file> <minimum> <maximum> <output>" % sys.argv[0]

def main():

  if len(sys.argv) != 5:
    usage()
    sys.exit(-1)


  # ---------------------------------------------------------------------------
  # Done.

if __name__ == "__main__":
  main()