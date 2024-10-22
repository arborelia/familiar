import random
import pkg_resources

FILENAME = pkg_resources.resource_filename(__name__, "data/table-names.txt")

tables = open(FILENAME).read().strip().split("\n")

# this is for actual table names now
table_names = {
    "nudgy": "Nudgy (1947)",
    "humpty": "Humpty Dumpty (1947)",
    "alice": "Alice in Wonderland (1948)",
    "joker": "Joker (1950)",
    "knockout": "Knock-Out (1950)",
    "spark": "Spark Plugs (1951)"
}


def pinball_table():
    return "The pinball table you should play is: " + random.choice(tables)


if __name__ == '__main__':
    print(pinball_table())
