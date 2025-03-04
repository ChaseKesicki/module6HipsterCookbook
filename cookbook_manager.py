import sqlite3
from sqlite3 import Error

# function to create a connection to the database
def create_connection():
    """Create a database connection"""
    conn = None
    try:
        conn = sqlite3.connect('hipster_cookbooks.db')
        print(f"Successfully connected to SQLite {sqlite3.version} ")
        return conn
    except Error as e:
        print(f"Error establishing connection with the void: {e}")
        return None
# function to create a table to store the cookbooks
def create_table(conn):
    """Create a table structure"""
    try:
        sql_create_cookbooks_table = """
        CREATE TABLE IF NOT EXISTS cookbooks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            year_published INTEGER,
            aesthetic_rating INTEGER,
            instagram_worthy BOOLEAN,
            cover_color TEXT
        );"""
        
        sql_create_tags_table = """
        CREATE TABLE IF NOT EXISTS tags (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        );"""
        
        sql_create_cookbook_tags_table = """
        CREATE TABLE IF NOT EXISTS cookbook_tags (
            cookbook_id INTEGER NOT NULL,
            tag_id INTEGER NOT NULL,
            FOREIGN KEY (cookbook_id) REFERENCES cookbooks(id),
            FOREIGN KEY (tag_id) REFERENCES tags(id),
            PRIMARY KEY (cookbook_id, tag_id)
        );"""

        # Calling the constructor for the cursor object to create a new cursor
        # That lets us work with the database
        cursor = conn.cursor()
        cursor.execute(sql_create_cookbooks_table)
        print("Successfully created a database structure")
    except Error as e:
        print(f"Error creating table: {e}")

def insert_cookbook(conn, cookbook):
    """Add a new cookbook to your shelf )"""
    # Adding validation to make sure that no entry is empty or wrong
    title, author, year_published, aethsetic_rating, instagram_worthy, cover_color = cookbook

    # Validation
    if not title or not author:
        print("Error: Title and author cannot be empty.")
        return None
    if not isinstance(year_published, int) or year_published < 0:
        print("Error: Year must be a positive integer.")
        return None
    if not (1 <= aesthetic_rating <= 5):
        print("Error: Aesthetic rating must be between 1 and 5.")
        return None
    if not isinstance(instagram_worthy, bool):
        print("Error: Instagram-worthy must be either True or False.")
        return None

    
    sql = '''INSERT INTO cookbooks(title, author, year_published, aesthetic_rating, instagram_worthy, cover_color)
             VALUES(?,?,?,?,?,?)'''
    try:
        cursor = conn.cursor()
        cursor.execute(sql, cookbook)
        conn.commit()
        print(f"Successfully curated cookbook with id: {cursor.lastrowid}")
        return cursor.lastrowid
    except Error as e:
        print(f"Error adding to collection: {e}")
        return None

def get_all_cookbooks(conn):
    """Browse your entire collection """
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM cookbooks")
        books = cursor.fetchall()
        # Validation
        if not books:
            print("No cookbooks found in the database.")
            return []

        for book in books:
            print(f"ID: {book[0]}")
            print(f"Title: {book[1]}")
            print(f"Author: {book[2]}")
            print(f"Published: {book[3]} (vintage is better)")
            print(f"Aesthetic Rating: {'✨' * book[4]}")
            print(f"Instagram Worthy: {'📸 Yes' if book[5] else 'Not aesthetic enough'}")
            print(f"Cover Color: {book[6]}")
            print("---")
        return books
    except Error as e:
        print(f"Error retrieving collection: {e}")
        return []
    
def add_recipe_tags(conn, cookbook_id, tags):
    """Add tags to a cookbook (e.g., 'gluten-free', 'plant-based', 'artisanal')"""
    # Create a new tags table with many-to-many relationship
    # Implement tag addition functionality
    # Return success/failure status
    try:
        cursor = conn.cursor()
        
        for tag in tags:
            # Insert tag if it doesn't already exist
            cursor.execute("INSERT OR IGNORE INTO tags (name) VALUES (?)", (tag,))
            
            # Retrieve the tag ID
            cursor.execute("SELECT id FROM tags WHERE name = ?", (tag,))
            tag_id = cursor.fetchone()[0]
            
            # Associate cookbook with the tag
            cursor.execute("INSERT OR IGNORE INTO cookbook_tags (cookbook_id, tag_id) VALUES (?, ?)", 
                           (cookbook_id, tag_id))
        
        conn.commit()
        print(f"Tags {tags} successfully added to cookbook ID {cookbook_id}")
    except Error as e:
        print(f"Error tagging cookbook: {e}")

def rotate_seasonal_collection(conn, season):
    """Update display recommendations based on season"""
    seasonal_tags = {
        "Winter": ["comfort food", "soups", "baking", "hearty"],
        "Spring": ["fresh", "greens", "fermented", "light meals"],
        "Summer": ["grilling", "salads", "cold drinks", "beach"],
        "Autumn": ["pumpkin", "harvest", "spices", "warming foods"]
    }
    
    if season not in seasonal_tags:
        print(f"Season '{season}' is not recognized. Try Winter, Spring, Summer, or Autumn.")
        return
    
    try:
        cursor = conn.cursor()
        
        # Reset instagram_worthy for all books
        cursor.execute("UPDATE cookbooks SET instagram_worthy = 0")
        
        # Find cookbooks that match the season’s tags
        query = """
            UPDATE cookbooks 
            SET instagram_worthy = 1
            WHERE id IN (
                SELECT cookbook_id FROM cookbook_tags 
                JOIN tags ON cookbook_tags.tag_id = tags.id
                WHERE tags.name IN ({})
            )
        """.format(','.join('?' * len(seasonal_tags[season])))
        
        cursor.execute(query, seasonal_tags[season])
        conn.commit()
        #Validation
        affected_rows = cursor.rowcount
        if affected_rows == 0:
            print(f"No cookbooks matched the seasonal tags for {season}.")
        else:
            print(f"Updated {affected_rows} cookbooks for {season}.")
    
    except Error as e:
        print(f"Error updating seasonal collection: {e}")

def main():
    # Establish connection to our artisanal database
    conn = create_connection()
    
    if conn is not None:
        # Create our free-range table
        create_table(conn)
        
        # Insert some carefully curated sample cookbooks
        cookbooks = [
            ('Foraged & Found: A Guide to Pretending You Know About Mushrooms', 
             'Oak Wavelength', 2023, 5, True, 'Forest Green'),
            ('Small Batch: 50 Recipes You will Never Actually Make', 
             'Sage Moonbeam', 2022, 4, True, 'Raw Linen'),
            ('The Artistic Toast: Advanced Avocado Techniques', 
             'River Wildflower', 2023, 5, True, 'Recycled Brown'),
            ('Fermented Everything', 
             'Jim Kombucha', 2021, 3, True, 'Denim'),
            ('The Deconstructed Sandwich: Making Simple Things Complicated', 
             'Juniper Vinegar-Smith', 2023, 5, True, 'Beige')
        ]
        
        print("\nCurating your cookbook collection...")
        for cookbook in cookbooks:
            insert_cookbook(conn, cookbook)
        
        print("\nYour carefully curated collection:")
        get_all_cookbooks(conn)
        
        conn.close()
        print("\nDatabase connection closed")
    else:
        print("Error! The universe is not aligned for database connections right now.")

if __name__ == '__main__':
    main()