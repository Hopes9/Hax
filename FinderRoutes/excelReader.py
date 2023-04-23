import json
import os
from datetime import datetime
from io import BytesIO

import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd
from geopy import Point, distance

from SqlClear import *


def updateExcel():
    workbook = openpyxl.load_workbook('data.xlsx')

    worksheet = workbook['Сколопендра_ Кейс 1_ дополнени']

    ListRoutes = []

    for row in worksheet.iter_rows(min_row=2):
        values = []
        for cell in row:
            values.append(cell.value)
        ListRoutes.append(values)

    def SumDateTime(routes):
        newListRouts = []
        for i in routes:
            print(i)
            if i[3] is not None:
                dt2 = datetime.combine(i[2].date(), i[3])
            else:
                dt2 = i[2].date()
            newListRouts.append([
                i[0], i[1], dt2, i[4]
            ])
        return newListRouts

    ListRoutes = SumDateTime(ListRoutes)

    df = pd.DataFrame(ListRoutes, columns=['A', 'B', 'time', "type"])

    h = {}
    for i in df['A'].unique():
        coordinates = str(getPosition(i))
        h[i] = coordinates

    datA = []
    datB = []

    for i in df.values:
        if h.get(i[0]):
            f = h.get(i[0])
            datA.append(f)
        else:
            coordinates = str(getPosition(i))
            h[i[0]] = coordinates
            datA.append(coordinates)

        if h.get(i[1]):
            f = h.get(i[1])
            datB.append(f)
        else:
            coordinates = str(getPosition(i))
            h[i[1]] = coordinates
            datB.append(coordinates)

    df["Agps"] = datA
    df["Bgps"] = datB

    try:
        os.remove("my_dataframe.xlsx")
    except:
        pass
    buffer = BytesIO()
    df.to_excel(buffer, index=False)
    buffer.seek(0)
    workbook = openpyxl.load_workbook(buffer)
    worksheet = workbook.active
    workbook.save('5data.xlsx')


# updateExcel()

# clearBySQL()

def getPosListCites(G, pos):
    P = []
    for i in pos:
        st = f"{i[0]} {i[1]}"
        print(st)
        try:
            P.append(db.ChekInCityPos(st)[0][1])
        except:
            pass
    return P


def getPosList(G, pos):
    L = []
    for i in pos:
        if i == "0":
            L.append(G.nodes[pos[0]]["pos"])
        else:
            L.append(G.nodes[i]["pos"])
    return L


def getListOpens(id_):
    row = db.getAtimeList(id_)
    return row


db = dbworker()

getAll_Rouds = db.Get_allRoad()
getAll_Points = db.getCityAll()

G = nx.DiGraph()

for i, point in enumerate(getAll_Points):
    point_ = point[2].split(" ")
    data = getListOpens(str(point[0]))
    G.add_node(str(point[0]), pos=(float(point_[0]), float(point_[1])), attr=data)
for start, end, ag, bg, dataStart, wight in getAll_Rouds:
    ag = list(map(float, ag.split(" ")))
    bg = list(map(float, bg.split(" ")))
    dist = round(distance.distance(Point(latitude=ag[0], longitude=ag[1]), Point(latitude=bg[0], longitude=bg[1])).km,
                 0)
    G.add_edge(start, end, weight=dist, data=[dataStart])

point_ = G.nodes["1"]['pos']
G.add_node("0", pos=(float(point_[0]) + 0.00001, float(point_[1]) + 0.00001))
G.add_edge("1", "0", weight=0, data=[datetime.now()])


def _all_simple_paths_graph(G, source, target, cutoff):
    targets = {target}
    visited = {source: True}
    stack = [iter(G[source])]
    while stack:
        children = stack[-1]
        child = next(children, None)
        if child is None:
            stack.pop()
            visited.popitem()
        elif len(visited) < cutoff:
            if child in visited:
                continue
            if child in targets:
                yield list(visited) + [child]
            visited[child] = True
            if targets - set(visited.keys()):
                try:
                    G.nodes[child]["attr"].pop(0)
                    stack.append(iter(G[child]))
                except:
                    pass

            else:
                visited.popitem()
        else:
            for target in (targets & (set(children) | {child})) - set(visited.keys()):
                yield list(visited) + [target]
            stack.pop()
            visited.popitem()


def _all_simple_paths_graph_fixed_length(G, source, target, length):
    paths = []
    for path in _all_simple_paths_graph(G, source=source, target=target, cutoff=length + 100000):
        if length >= len(path) >= 3:
            weight = 0
            for i in range(len(path) - 1):
                try:
                    weight += G.edges[(path[i], path[i + 1])]['weight']
                    paths.append((path, weight))
                except:
                    pass
    return paths


G.add_node("0", pos=(float(point_[0]), float(point_[1])))

ALL_PATH = []

for i in list(G.nodes):
    edges_to_i = list(G.edges(i))
    for u, v in edges_to_i:
        G.add_edge(u, '0')

    paths = _all_simple_paths_graph_fixed_length(G, i, "0", 9000000)
    if len(paths):
        ALL_PATH.append(paths)
    edges_to_i = list(G.edges('0'))
    G.remove_edges_from(edges_to_i)

pos = nx.get_node_attributes(G, 'pos')
nx.draw(G, pos)
nx.draw_networkx_edge_labels(G, pos, edge_labels=nx.get_edge_attributes(G, 'weight'))
plt.show()

routes = []
for route in ALL_PATH:
    stops, distance = route[0]
    route_info = {'stops': stops, 'distance': distance}
    routes.append(route_info)

sorted_routes = sorted(routes, key=lambda x: (x['distance']))
for i in sorted_routes:
    i["geo"] = getPosList(G, i["stops"])

for i in sorted_routes:
    i["names"] = getPosListCites(G, i["geo"])

print(sorted_routes)
for i, a in enumerate(sorted_routes[:6]):
    print(a)

with(open('test.json', '+w', encoding="UTF-8")) as f:
    f.write(json.dumps(sorted_routes[5:], sort_keys=True, ensure_ascii=False))
