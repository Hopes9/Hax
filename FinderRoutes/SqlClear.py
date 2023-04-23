import sqlite3

import openpyxl

from getPosition import getPosition


class dbworker:
    def __init__(self):
        self.connection = sqlite3.connect('main.db')
        self.cursor = self.connection.cursor()

    def insert_route(self, A, B, Agps, Bgps, time, km, type):
        with self.connection:
            self.cursor.execute(
                f"insert into Routes (A, B, Agps, Bgps, time, km, type) values ('{A}', '{B}', '{Agps}', '{Bgps}', '{time}', {km}, '{type}')")

    def insert_city(self, city):
        with self.connection:
            self.cursor.execute(
                f"insert into Cites (city) values ('{city}')")

    def getByGps(self, id_t, gps):
        with self.connection:
            self.cursor.execute(f"SELECT A, Agps FROM Routes WHERE {gps} = '{id_t}'")
            res = self.cursor.fetchall()
            return res

    def GetCitiesSorted(self, char):
        with self.connection:
            self.cursor.execute(
                f"SELECT distinct G.{char}, G.{char}gps, F.{char}gps from (SELECT distinct {char}, {char}gps FROM Routes) as G inner join Routes as F on G.{char}gps = F.{char}gps order by G.{char}gps")
            res = self.cursor.fetchall()
            return res

    def getAll(self):
        with self.connection:
            self.cursor.execute(f"SELECT A, Agps FROM Routes")
            res = self.cursor.fetchall()
            return res

    def getCityAll(self):
        with self.connection:
            self.cursor.execute(f"SELECT * FROM Cites")
            res = self.cursor.fetchall()
            return res

    def updateCity_by_geo(self, gps, city, char):
        with self.connection:
            self.cursor.execute(f"UPDATE Routes SET {char} = ? WHERE {char}gps = ?", (city, gps))
            self.connection.commit()

    def updateCity_by_geo_setID(self, city, id_, char):
        with self.connection:
            self.cursor.execute(f"UPDATE Routes SET {char} = {id_} WHERE {char} = '{city}'")
            self.connection.commit()

    def updateCity_Position(self, city, pos):
        with self.connection:
            self.cursor.execute(f"UPDATE Cites SET Pos = '{pos}' WHERE city = '{city}'")
            self.connection.commit()

    def ChekLen(self):
        with self.connection:
            self.cursor.execute(f"SELECT * FROM Routes")
            res = self.cursor.fetchall()
            return res

    def Get_allRoad(self):
        with self.connection:
            self.cursor.execute(f"SELECT A, B, Agps, Bgps, time, km FROM Routes")
            res = self.cursor.fetchall()
            return res

    def ChekInCity(self, city):
        with self.connection:
            self.cursor.execute(f"SELECT * FROM Cites where city = '{city}'")
            res = self.cursor.fetchall()
            return res

    def ChekInCityPos(self, city):
        with self.connection:
            self.cursor.execute(f"SELECT * FROM Cites where Pos = '{city}'")
            res = self.cursor.fetchall()
            return res

    def get1(self):
        with self.connection:
            self.cursor.execute(f"SELECT distinct A from Routes")
            res = self.cursor.fetchall()
            return res

    def get2(self):
        with self.connection:
            self.cursor.execute(f"SELECT distinct B from Routes")
            res = self.cursor.fetchall()
            return res

    def getAtimeList(self, id_):
        with self.connection:
            self.cursor.execute(f"SELECT distinct time from Routes where A = '{id_}'")
            res = self.cursor.fetchall()
            return res


db = dbworker()


def clearBySQL():
    if len(db.ChekLen()) == 0:
        workbook = openpyxl.load_workbook('5data.xlsx')

        worksheet = workbook['Sheet1']

        ListRoutes = []

        for row in worksheet.iter_rows(min_row=2):
            values = []
            for cell in row:
                values.append(cell.value)
            ListRoutes.append(values)
            db.insert_route(values[0], values[1], values[4], values[5], values[2], "NULL", values[3])

    coord_dictA = {}
    coord_dictB = {}
    for city, coord1, coord2 in db.GetCitiesSorted("A"):
        if coord1 in coord_dictA:
            coord_dictA[coord1].append(city)
        else:
            coord_dictA[coord1] = [city]
        if coord2 in coord_dictA:
            coord_dictA[coord2].append(city)
        else:
            coord_dictA[coord2] = [city]

    for city, coord1, coord2 in db.GetCitiesSorted("B"):
        if coord1 in coord_dictB:
            coord_dictB[coord1].append(city)
        else:
            coord_dictB[coord1] = [city]
        if coord2 in coord_dictB:
            coord_dictB[coord2].append(city)
        else:
            coord_dictB[coord2] = [city]

    for i in coord_dictA:
        db.updateCity_by_geo(i, coord_dictA[i][0], 'A')
    for i in coord_dictB:
        db.updateCity_by_geo(i, coord_dictB[i][0], 'B')

    for i in db.get1():
        if len(db.ChekInCity(i[0])) == 0:
            db.insert_city(i[0])

    for i in db.get2():
        if len(db.ChekInCity(i[0])) == 0:
            db.insert_city(i[0])

    for i in db.getCityAll():
        print(i)
        db.updateCity_by_geo_setID(i[1], i[0], "A")
        db.updateCity_by_geo_setID(i[1], i[0], "B")
        db.updateCity_Position(i[1], getPosition(i[1]))

