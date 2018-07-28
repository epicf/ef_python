import sys

def production_assert(should_be, message):
    if not should_be:
        print("Error: ", message)
        sys.exit(-1)
