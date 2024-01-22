from init import dbconn
import json, psycopg2, os, sys
from umang import station as umang

class Stations:
    __table = os.getenv("DB1_INDRAIL_STATIONS_TABLE")
    __db = None
    __dbcon = None

    def __init__(self) -> None:
        self.__connectDb()

    def __connectDb(self) -> None:
        self.__db = dbconn.DatabaseConn()
        self.__dbcon = self.__db.conn

    def getStationListApiUmang(self) -> None:
        self.stations_api = umang.ApiSetu_Station().getStationListApi()

    def getStationListDb(self) -> None:
        print("(DB) Initiating list all station query")
        # Create a cursor object to execute SQL queries
        cursor = self.__dbcon.cursor()
        # Select Query
        query = f'SELECT code, name FROM {self.__table};'
        cursor.execute(query)
        # Fetch the results
        results = cursor.fetchall()
        # Commit the transaction
        self.__dbcon.commit()
        cursor.close()

        print(f"(DB) Total no. of stations: {len(results)}")

        self.stations_db = []
        for s in results:
            self.stations_db.append({
                "stationCode" : s[0],
                "stationName" : s[1]
            })

    def updateStationDb(self, sapi: map, sdb: map) -> None:
        if sapi['stationCode'] == sdb['stationCode'] and sapi['stationName'] == sdb['stationName']:
            pass
        elif sapi['stationCode'] == sdb['stationCode'] and sapi['stationName'] != sdb['stationName']:
            # Create a cursor object to execute SQL query
            cursor = self.__dbcon.cursor()

            update_qry = f'UPDATE {self.__table} SET name = %s WHERE code = %s'
            new_value = sapi['stationName']
            condition_value = sapi['stationCode']

            cursor.execute(update_qry, (new_value, condition_value))
            # Commit the transaction
            self.__dbcon.commit()
            print(f"--- UPDATE SUCCESS [{sapi['stationCode']} - {sapi['stationName']}]")
            cursor.close()

    def insertStationDb(self, sapi: map) -> None:
        # Create a cursor object to execute SQL query
        cursor = self.__dbcon.cursor()

        insert_qry = f'INSERT INTO {self.__table} (code, name) VALUES (%s, %s);'
        data_to_insert = (sapi['stationCode'], sapi['stationName'])

        cursor.execute(insert_qry, data_to_insert)
        # Commit the transaction
        self.__dbcon.commit()
        print(f"--- INSERT SUCCESS [{sapi['stationCode']} - {sapi['stationName']}]")
        cursor.close()

    def closeConnDb(self) -> None:
        self.__db.closeConn()


def main():
    stations = Stations()
    if sys.argv[1] == 'umang':
        stations.getStationListApiUmang()
        
    stations.getStationListDb()

    '''
        Iterate through each station to check for any changes in station name.
        1. If unchanged, do nothing
        2. If changed [station name], update station name w.r.t to station code
    '''

    if len(stations.stations_api) == len(stations.stations_db):
        for sapi in stations.stations_api:
            for sdb in stations.stations_db:
                stations.updateStationDb(sapi=sapi, sdb=sdb)

    elif len(stations.stations_api) < len(stations.stations_db):
        # Send mail to admin user(s)
        station_list = []
        for sdb in stations.stations_db:
            check_station = True
            for sapi in stations.stations_api:
                stations.updateStationDb(sapi=sapi, sdb=sdb)
                if sapi['stationCode'] == sdb[1]:
                    check_station = False
                    break
            if check_station:
                station_list.append(f"{sdb[1]} - {sdb[2]}")
        
        print("<---Rail Stations in DB--->")
        for i in range(len(station_list)):
            print(f'{i}. {station_list[i]}')

    elif len(stations.stations_api) > len(stations.stations_db):
        for sapi in stations.stations_api:
            check_station = True
            for sdb in stations.stations_db:
                stations.updateStationDb(sapi=sapi, sdb=sdb)
                if sapi['stationCode'] == sdb[1]:
                    check_station = False
                    break
            if check_station:
                stations.insertStationDb(sapi=sapi)

    stations.closeConnDb()


if __name__ == "__main__":
    if len(sys.argv) == 2:
        main()





