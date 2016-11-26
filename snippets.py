import logging
import argparse
import psycopg2

#set the log output file, and the log level
logging.basicConfig(filename="snippets.log", level=logging.DEBUG)

logging.debug("Connecting to PostgreSQL")
connection = psycopg2.connect(database="snippets")
logging.debug("Database connection established")

def put(hide, name, snippet):
    """
    Store a snippet with an associated name
    Returns the name and the snippet
    """
    logging.info("Storing snippet {!r}: {!r}".format(name, snippet))
  
    with connection, connection.cursor() as cursor:
        try:
            cursor.execute("insert into snippets values (%s, %s, %s)", (name, snippet, hide))
        except psycopg2.IntegrityError as e:
            connection.rollback()
            cursor.execute("update snippets set message=%s, hidden=%s where keyword=%s", (snippet, hide, name))
    logging.debug("Snippet stored successfully")
    return hide, name, snippet
    
def catalog():
    """
    Display a list of keywords 
    currently available in the database
    """
    logging.info("Retrieved keywords")
    with connection, connection.cursor() as cursor:
        cursor.execute("select keyword from snippets where not hidden order by keyword")
        rows = cursor.fetchall()
    logging.debug("Keywords retrieved successfully")
    return rows
    
def search(terms):
    """
    Search for a snippet based on a given string and
    return a list of possible snippet matches
    """
    logging.info("Retrieved possible snippet matches")
    print(terms)
    with connection, connection.cursor() as cursor:
        cursor.execute("select * from snippets where not hidden and message like %s", (terms,))
        rows = cursor.fetchall()
    logging.debug("Snippets retrieved successfully")
    return rows

def get(name):
    """
    Retrieve the snippet with a given name.
    If no such snippet, return '404: Snippet Not Found'.
    Returns the snippet.
    """
    logging.info("Retrieved snippet {!r}".format(name))
    with connection, connection.cursor() as cursor:
        cursor.execute("select * from snippets where keyword=%s", (name,))
        row = cursor.fetchone()
    logging.debug("Snippet retrieved successfully")
    if not row:
        return "Snippet not found"
    return row[1]
    
    
def main():
    """
    Main function
    """
    logging.info("Constructing parser")
    parser = argparse.ArgumentParser(description="Store and retrieve snippets of text")
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    #subparser for the put command
    logging.debug("Constructing put subparser")
    put_parser = subparsers.add_parser("put", help="Store a snippet")
    put_parser.add_argument("--hide", help="Hide this snippet text from search and catalog", action="store_true")
    put_parser.add_argument("name", help="Name of the snippet")
    put_parser.add_argument("snippet", help="Snippet text")
    
    
    #subparser for the catalog command
    logging.debug("Constructing catalog subparser")
    catalog_parser = subparsers.add_parser("catalog", help="Retrieve list of keywords")
    
    #subparser for the search command
    logging.debug("Constructing search subparser")
    search_parser = subparsers.add_parser("search", help="Retrieve list of possible snippet matches")
    search_parser.add_argument("terms", help="A string of search terms")
    
    #subparser for the get command
    logging.debug("Constructing get subparser")
    get_parser = subparsers.add_parser("get", help="Retrieve a snippet")
    get_parser.add_argument("name", help="Name of the snippet")
    
    
    arguments = parser.parse_args()
    #convert parsed arguments from Namespace to dictionary
    arguments = vars(arguments)
    command = arguments.pop("command")
    
    if command == "put":
        hide, name, snippet = put(**arguments)
        print("Stored {!r} as {!r}".format(snippet, name))
    elif command == "catalog":
        names =  catalog(**arguments)
        print("Retrieved keywords: {!r}".format(names))
    elif command == "search":
        terms = search(**arguments)
        print("Retrieved possible snippet matches: {!r}".format(terms))
    elif command == "get":
        snippet = get(**arguments)
        print("Retrieved snippet: {!r}".format(snippet))
    
if __name__ == "__main__":
    main()
    

 
 