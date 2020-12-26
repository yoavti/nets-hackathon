class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def annotate(annotation, message):
    """
    Receives a message and an annotation (taken from bcolors)
    and returns the message annotated by the given annotation
    """
    return annotation + str(message) + bcolors.ENDC


def annotate_error(msg):
    'Annotate `msg` with `bcolors.FAIL`'
    return annotate(bcolors.FAIL, msg)


def annotate_warning(msg):
    'Annotate `msg` with `bcolors.WARNING`'
    return annotate(bcolors.WARNING, msg)


def annotate_variable(msg):
    'Annotate `msg` with `bcolors.OKBLUE`'
    return annotate(bcolors.OKBLUE, msg)


def annotate_name(msg):
    'Annotate `msg` with `bcolors.OKGREEN`'
    return annotate(bcolors.OKGREEN, msg)


def annotate_underline(msg):
    'Annotate `msg` with `bcolors.UNDERLINE`'
    return annotate(bcolors.UNDERLINE, msg)


def print_error(msg):
    'Prints the given message in red'
    print(annotate_error(msg))


def print_warning(msg):
    'Prints the given message in yellow'
    print(annotate_warning(msg))


if __name__ == "__main__":
    # An example for how to use bcolors
    print(f"{bcolors.WARNING}Warning: No active frommets remain. Continue?{bcolors.ENDC}")
