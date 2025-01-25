import sys
import os

import sqlite3
import pandas as pd

from config import DATA_PATH, DATA_DIR_NAME, dependencies_path

class DbHandler:
    def __init__(self) -> None:
        self._database_abs_path = dependencies_path(f'{DATA_DIR_NAME}//components.db')

        self._check_if_database_exists()
    
    def _check_if_database_exists(self):
         # Check if destination folder where database file should be, exists
        if not os.path.exists(DATA_PATH):
            sys.stderr.write(f"Error: Directory {DATA_PATH} does not exist.\n")
            sys.exit(1)
        # Check if database file exists
        if not os.path.exists(self._database_abs_path):
            sys.stderr.write(f"Error: Database file {self._database_abs_path} does not exist.\n")
            sys.exit(1)
        # Check the connection with the database
        try:
            conn = sqlite3.connect(self._database_abs_path)
            conn.close()
        except sqlite3.Error as e:
            sys.stderr.write(f"Connection failed with error: {e}")
    
    def fetch_bearings(self, support_type, bearing_type, min_d_in=None, min_C=None):
        conn = sqlite3.connect(self._database_abs_path)

        query = '''
        SELECT designation, d_in, d_out, {} b, c, c_0, n_max FROM Bearings
        JOIN BearingTypes ON Bearings.bearing_type_id = BearingTypes.id
        JOIN MountingTypes ON BearingTypes.mounting_type_id = MountingTypes.id
        WHERE BearingTypes.name = ? AND MountingTypes.name = ?
        '''

        # Modify the query and headers depending on the support type
        if support_type == 'centralne':
            additional_column = 'e,'
            headers = ['kod', 'D<sub>w</sub>', 'D<sub>z</sub>', 'E', 'B', 'C', 'C<sub>0</sub>', 'n<sub>max</sub>']
            units = ['-', 'mm', 'mm', 'mm', 'mm', 'MPa', 'MPa', 'obr/min']
        else:
            additional_column = ''
            headers = ['kod', 'D<sub>w</sub>', 'D<sub>z</sub>', 'B', 'C', 'C<sub>0</sub>', 'n<sub>max</sub>']
            units = ['-', 'mm', 'mm', 'mm', 'MPa', 'MPa', 'obr/min']

        # Format the query with the additional column if needed
        query = query.format(additional_column)

        # Add constraints for min_d_in and min_C if provided
        constraints = []
        params = [bearing_type, support_type]

        if min_d_in is not None:
            constraints.append('d_in >= ?')
            params.append(min_d_in)

        if min_C is not None:
            constraints.append('c >= ?')
            params.append(min_C)

        if constraints:
            query += ' AND ' + ' AND '.join(constraints)

            # Add limit to ensure only 5 results are returned
            query += ' ORDER BY d_in, c_0 LIMIT 5'

        df = pd.read_sql_query(query, conn, params=params)
        
        conn.close()

        # Combine headers with units for display
        headers = [header + f'<br><small>[{unit}]</small>' for header, unit in zip(headers, units)]
        keys = df.columns.tolist()
        data = df.values.tolist()

        return headers, keys, data

    def fetch_bearing_types(self, mount_type):
        conn = sqlite3.connect(self._database_abs_path)

        query = '''
        SELECT BearingTypes.name FROM BearingTypes 
        JOIN RollingElementTypes ON BearingTypes.rolling_element_type_id = RollingElementTypes.id
        JOIN MountingTypes ON BearingTypes.mounting_type_id = MountingTypes.id
        WHERE MountingTypes.name = ?
        '''

        df = pd.read_sql_query(query, conn, params=(mount_type,))
        
        conn.close()

        headers = ['Rodzaj łożyska']
        keys = df.columns.tolist() 
        data = df.values.tolist()

        return headers, keys, data

    def fetch_rolling_elements(self, bearing_type, d_min=None):
        conn = sqlite3.connect(self._database_abs_path)

        if d_min is None:
            # If d is None, list all results
            query = '''
                SELECT RollingElements.d FROM BearingTypes
                JOIN RollingElements ON BearingTypes.rolling_element_type_id = RollingElements.rolling_element_type_id
                WHERE BearingTypes.name = ?
                ORDER BY d
            '''
            df = pd.read_sql_query(query, conn, params=(bearing_type,))
        else:
            # Query to check if an exact match exists
            query_exact = '''
                SELECT RollingElements.d FROM BearingTypes
                JOIN RollingElements ON BearingTypes.rolling_element_type_id = RollingElements.rolling_element_type_id
                WHERE BearingTypes.name = ? AND RollingElements.d = ?
            '''
            df_exact = pd.read_sql_query(query_exact, conn, params=(bearing_type, d_min))
            
            if not df_exact.empty:
                # Exact match found, return it
                df = df_exact
            else:
                # Exact match not found, find closest lower and greater values
                query_smaller = '''
                    SELECT RollingElements.d FROM BearingTypes
                    JOIN RollingElements ON BearingTypes.rolling_element_type_id = RollingElements.rolling_element_type_id
                    WHERE BearingTypes.name = ? AND RollingElements.d < ?
                    ORDER BY RollingElements.d DESC
                    LIMIT 1
                '''
                query_greater = '''
                    SELECT RollingElements.d FROM BearingTypes
                    JOIN RollingElements ON BearingTypes.rolling_element_type_id = RollingElements.rolling_element_type_id
                    WHERE BearingTypes.name = ? AND RollingElements.d > ?
                    ORDER BY RollingElements.d ASC
                    LIMIT 1
                '''
                df_smaller = pd.read_sql_query(query_smaller, conn, params=(bearing_type, d_min))
                df_greater = pd.read_sql_query(query_greater, conn, params=(bearing_type, d_min))
                df = pd.concat([df_smaller, df_greater]).sort_values(by='d').reset_index(drop=True)

        headers = ['D']
        units = ['mm']

        headers = [header + f'<br><small>[{unit}]</small>' for header, unit in zip(headers, units)]
        keys = df.columns.tolist()
        data = df.values.tolist()

        return headers, keys, data
        
    def fetch_materials(self):
        conn = sqlite3.connect(self._database_abs_path)

        query = '''
        SELECT  name, r_m, r_e, z_gj, z_go, z_sj, z_so, e, g, ro FROM Materials
        '''

        df = pd.read_sql_query(query, conn)
        
        conn.close()

        headers = ['kod', 'R<sub>m</sub>', 'R<sub>e</sub>', 'Z<sub>gj</sub>', 'Z<sub>go</sub>', 'Z<sub>sj</sub>', 'Z<sub>so</sub>', 'E', 'G', 'ρ']
        units = ['-', 'MPa', 'MPa', 'MPa', 'MPa', 'MPa', 'MPa', 'MPa', 'MPa', 'kg/m<sup>3</sup>']
        
        headers = [ header + f'<br><small>[{unit}]</small>' for header, unit in zip(headers, units)]
        keys = df.columns.tolist()
        data = df.values.tolist()

        return headers, keys, data
