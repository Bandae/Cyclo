import sys, os
import sqlite3
import pandas as pd

# Function to determine if we're running as a PyInstaller bundle
def is_frozen():
    return getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS')

# Function to get the correct base directory
def get_base_dir():
    if is_frozen():
        # If the application is run as a bundle, the PyInstaller bootloader
        # extends the sys module by a flag frozen=True and sets the app 
        # path into variable _MEIPASS.
        return sys._MEIPASS
    else:
        # If it's run in a normal Python environment, return the directory
        # containing this file.
        return os.path.dirname(os.path.abspath(__file__))

base_dir = get_base_dir()

config_path = os.path.join(base_dir, '..', '..', 'config.py')
config_dir = os.path.dirname(config_path)

# Add the config directory to sys.path if not already added
if config_dir not in sys.path:
    sys.path.append(config_dir)

from config import DATA_PATH, DATA_DIR_NAME, dependencies_path

class DbCreator:
    '''
    This class creates a database of components which data
    is used in the application.
    '''
    def __init__(self): 
        self._create_database()
        self._create_tables()

    def _create_database(self):
        # Set the destination directory absoulte path where csv and database files should be stored
        if not os.path.exists(DATA_PATH):
            sys.stderr.write(f"Error: {DATA_PATH} does not exist.\n")
            sys.exit(1)

        # Set the absoulte path of the created database
        self._database_abs_path = dependencies_path(f'{DATA_DIR_NAME}//components.db')

        # If database already exists, remove it
        if os.path.exists(self._database_abs_path):
            os.remove(self._database_abs_path)

        # Create new database
        conn = sqlite3.connect(self._database_abs_path)
        conn.close

    def _create_tables(self):
        conn = sqlite3.connect(self._database_abs_path)
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Materials (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                r_m TEXT NOT NULL,
                r_e INTEGER NOT NULL,
                z_gj INTEGER NOT NULL,
                z_go INTEGER NOT NULL,
                z_sj INTEGER NOT NULL,
                z_so INTEGER NOT NULL,
                e INTEGER NOT NULL,
                g INTEGER NOT NULL,
                ro INTEGER NOT NULL
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS MountingTypes (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS RollingElementTypes (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS BearingTypes (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                rolling_element_type_id INTEGER,
                mounting_type_id INTEGER,
                FOREIGN KEY (rolling_element_type_id) REFERENCES RollingElementTypes(id)
                FOREIGN KEY (mounting_type_id) REFERENCES MountingTypes(id)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS RollingElements (
                id INTEGER PRIMARY KEY,
                d REAL NOT NULL,
                rolling_element_type_id INTEGER,
                FOREIGN KEY (rolling_element_type_id) REFERENCES RollingElementTypes(id)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Bearings (
                id INTEGER PRIMARY KEY,
                designation TEXT NOT NULL,
                d_in REAL NOT NULL,
                d_out REAL NOT NULL,
                e REAL,
                b REAL NOT NULL,
                c REAL NOT NULL,
                c_0 REAL NOT NULL,
                n_max REAL NOT NULL,
                bearing_type_id INTEGER,
                rolling_element_type_id INTEGER,
                FOREIGN KEY (bearing_type_id) REFERENCES BearingTypes(id),
                FOREIGN KEY (rolling_element_type_id) REFERENCES RollingElementTypes(id)
            )
        ''')

        conn.commit()
        conn.close()

    def add_materials(self, file):
        conn = sqlite3.connect(self._database_abs_path)
        df = pd.read_csv(file, skiprows=[1], delimiter=';', decimal=',')
        df.index.name = 'id'
        df.to_sql('Materials', conn, if_exists='replace', index=True)

        conn.commit()
        conn.close()

    def add_mounting_types(self):
        conn = sqlite3.connect(self._database_abs_path)
        cursor = conn.cursor()

        mounting_types = [
            ('podporowe',),
            ('centralne',)
        ]

        cursor.executemany('''
            INSERT INTO MountingTypes (name)
            VALUES (?)
        ''', mounting_types)

        conn.commit()
        conn.close()
    
    def add_rolling_element_types(self):
        conn = sqlite3.connect(self._database_abs_path)
        cursor = conn.cursor()

        rolling_element_types = [
            ('kulki',),
            ('wałeczki',),
            ('igiełki',)
        ]

        cursor.executemany('''
            INSERT INTO RollingElementTypes (name)
            VALUES (?)
        ''', rolling_element_types)

        conn.commit()
        conn.close()

    def add_bearing_types(self):
        conn = sqlite3.connect(self._database_abs_path)
        cursor = conn.cursor()

        bearing_types = [
            ('kulkowe', 1, 1), # kulki, podporowe
            ('walcowe', 2, 1), # wałeczki, podporowe
            ('walcowe', 2, 2), # wałeczki, centralne
            ('igiełkowe', 3, 2)  # igiełki, centralne
        ]

        cursor.executemany('''
        INSERT INTO BearingTypes (name, rolling_element_type_id, mounting_type_id)
        VALUES (?, ?, ?)
        ''', bearing_types)
        
        conn.commit()
        conn.close()

    def add_rolling_elements(self, file, rolling_element_type):
        conn = sqlite3.connect(self._database_abs_path)
        cursor = conn.cursor()

        df = pd.read_csv(file, skiprows=[1], delimiter=';', decimal=',')

        df['rolling_element_type_id'] = rolling_element_type

        insert_query = '''
            INSERT INTO RollingElements (d, rolling_element_type_id)
            VALUES (?, ?)
        '''
        
        for _, row in df.iterrows():
            cursor.execute(insert_query, (row['d'], row['rolling_element_type_id']))

        conn.commit()
        conn.close()

    def add_bearings(self, file, bearing_type, rolling_element_type, e=False):
        conn = sqlite3.connect(self._database_abs_path)
        cursor = conn.cursor()

        df = pd.read_csv(file, skiprows=[1], delimiter=';', decimal=',')

        df['bearing_type_id'] = bearing_type
        df['rolling_element_type_id'] = rolling_element_type

        if not e:
            df['e'] = None

        insert_query = '''
            INSERT INTO Bearings (designation, d_in, d_out, e, b, c, c_0, n_max, bearing_type_id, rolling_element_type_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        
        for _, row in df.iterrows():
            cursor.execute(insert_query, (
                row['designation'],
                row['d_in'],
                row['d_out'],
                row['e'],
                row['b'],
                row['c'],
                row['c_0'],
                row['n_max'],
                row['bearing_type_id'],
                row['rolling_element_type_id']
            ))

        conn.commit()
        conn.close()

db_creator = DbCreator()

db_creator.add_materials('data/wal_czynny-materialy.csv')
db_creator.add_mounting_types()
db_creator.add_bearing_types()
db_creator.add_rolling_element_types()
db_creator.add_rolling_elements('data/wal_czynny-elementy_toczne-kulki.csv', 1)
db_creator.add_rolling_elements('data/wal_czynny-elementy_toczne-waleczki.csv', 2)
db_creator.add_rolling_elements('data/wal_czynny-elementy_toczne-igielki.csv', 3)
db_creator.add_bearings('data/wal_czynny-lozyska-podporowe-kulkowe.csv', 1, 1)
db_creator.add_bearings('data/wal_czynny-lozyska-podporowe-walcowe.csv', 2, 2)
db_creator.add_bearings('data/wal_czynny-lozyska-centralne-walcowe.csv', 3, 2, True)
db_creator.add_bearings('data/wal_czynny-lozyska-centralne-igielkowe.csv', 4, 3, True)