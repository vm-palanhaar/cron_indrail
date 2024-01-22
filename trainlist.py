from init import dbconn
import json, psycopg2, os, sys
from umang import train as umang

class Trains:
    __table = os.getenv("DB1_INDRAIL_TRAINS_TABLE")
    __db = None
    __dbconn = None

    def __init__(self) -> None:
        self.__connectDb()

    def __connectDb(self) -> None:
        self.__db = dbconn.DatabaseConn()
        self.__dbcon = self.__db.conn

    def getTrainListApiUmang(self) -> None:
        self.trains_api = umang.ApiSetu_Train().getTrainListApi()

    def getTrainListDb(self) -> None:
        print("(DB) Initiating list all station query")
        # Create a cursor object to execute SQL queries
        cursor = self.__dbcon.cursor()
        # Select Query
        query = f'SELECT train_no, train_name FROM {self.__table};'
        cursor.execute(query)
        # Fetch the results
        results = cursor.fetchall()
        # Commit the transaction
        self.__dbcon.commit()
        cursor.close

        print(f"(DB) Total no. of trains: {len(results)}")
        self.trains_db = []
        for t in results:
            self.trains_db.append({
                "trainNo" : t[0],
                "trainName" : t[1]
            })

    def updateTrainDb(self, tapi: map, tdb: map) -> None:
        if tapi["trainNo"] == tdb["trainNo"] and tapi["trainName"] == tdb["trainName"]:
            pass
        elif tapi["trainNo"] == tdb["trainNo"] and tapi["trainName"] != tdb["trainName"]:
            # Create a cursor object to execute SQL query
            cursor = self.__dbcon.cursor()

            update_qry = f'UPDATE {self.__table} SET train_name = %s WHERE train_no = %s'
            new_value = tapi["trainName"]
            condition_value = tapi["trainNo"]

            cursor.execute(update_qry, (new_value, condition_value))
            # Commit the transaction
            self.__dbcon.commit()
            print(f'--- UPDATE SUCCESS [{tapi["trainNo"]} - {tapi["trainName"]}]')
            cursor.close()

    def insertTrainDb(self, tapi: map) -> None:
        # Create a cursor object to execute SQL query
        cursor = self.__dbcon.cursor()

        insert_qry = f'INSERT INTO {self.__table} ({self.__cl1}, {self.__cl2}) VALUES (%s, %s);'
        data_to_insert = (tapi["trainNo"], tapi["trainName"])

        try:
            cursor.execute(insert_qry, data_to_insert)
            print(f'--- INSERT SUCCESS [{tapi["trainNo"]} - {tapi["trainName"]}]')
            cursor.close()
        except (Exception, psycopg2.Error) as error:
            print(error)

    def closeConnDb(self) -> None:
        self.__db.closeConn()


def main():
    trains = Trains()
    if sys.argv[1] == 'umang':
        trains.getTrainListApiUmang()
        
    trains.getTrainListDb()

    '''
        Iterate through each train to check for any changes in train name.
        1. If unchanged, do nothing
        2. If changed [train name], update train name w.r.t to train no
    '''

    if len(trains.trains_api) == len(trains.trains_db):
        for tapi in trains.trains_api:
            for tdb in trains.trains_db:
                trains.updateTrainDb(tapi=tapi, tdb=tdb)

    elif len(trains.trains_api) < len(trains.trains_db):
        # Send mail to admin user(s)
        train_list = []
        for tdb in trains.trains_db:
            check_train = True
            for tapi in trains.trains_api:
                trains.updateTrainDb(tapi=tapi, tdb=tdb)
                if tapi['trainNo'] == tdb['trainNo']:
                    check_train = False
                    break
            if check_train:
                train_list.append(f"{tdb['trainNo']} - {tdb['trainName']}")
        
        print("<---Trains in DB--->")
        for i in range(len(train_list)):
            print(f'{i}. {train_list[i]}')

    elif len(trains.trains_api) > len(trains.trains_db):
        for tapi in trains.trains_api:
            check_train = True
            for tdb in trains.trains_db:
                trains.updateTrainDb(tapi=tapi, tdb=tdb)
                if tapi['trainNo'] == tdb['trainNo']:
                    check_train = False
                    break
            if check_train:
                trains.insertTrainDb(tapi=tapi)

    trains.closeConnDb()


if __name__ == "__main__":
    if len(sys.argv) == 2:
        main()