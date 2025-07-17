import random
import pkg_resources

FILENAME = pkg_resources.resource_filename(__name__, "data/table-names.txt")

tables = open(FILENAME).read().strip().split("\n")


def pinball_table():
    return "The pinball table you should play is: " + random.choice(tables)


if __name__ == '__main__':
    print(pinball_table())
