#!/usr/bin/env
# -*- coding:utf-8 -*-
# Source from https://github.com/noomrevlis/trilateration
from __future__ import division
import json
import math
import utm

from json import encoder
encoder.FLOAT_REPR = lambda o: format(o, '.2f')

class base_station(object):
    def __init__(self, lat, lon, dist):
        self.lat = lat
        self.lon = lon
        self.dist = dist

class point(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y

class circle(object):
    def __init__(self, point, radius):
        self.center = point
        self.radius = radius

class json_data(object):
    def __init__(self, circles, inner_points, center):
        self.circles = circles
        self.inner_points = inner_points
        self.center = center
    
def serialize_instance(obj):
    d = {}
    d.update(vars(obj))
    return d

def get_two_points_distance(p1, p2):
    return math.sqrt(pow((p1.x - p2.x), 2) + pow((p1.y - p2.y), 2))

def get_two_circles_intersecting_points(c1, c2):
    p1 = c1.center 
    p2 = c2.center
    r1 = c1.radius
    r2 = c2.radius

    d = get_two_points_distance(p1, p2)
    # if to far away, or self contained - can't be done
    if d >= (r1 + r2) or d <= math.fabs(r1 -r2):
        return None

    a = (pow(r1, 2) - pow(r2, 2) + pow(d, 2)) / (2*d)
    h  = math.sqrt(pow(r1, 2) - pow(a, 2))
    x0 = p1.x + a*(p2.x - p1.x)/d 
    y0 = p1.y + a*(p2.y - p1.y)/d
    rx = -(p2.y - p1.y) * (h/d)
    ry = -(p2.x - p1.x) * (h / d)
    return [point(x0+rx, y0-ry), point(x0-rx, y0+ry)]

def get_all_intersecting_points(circles):
    points = []
    num = len(circles)
    for i in range(num):
        j = i + 1
        for k in range(j, num):
            res = get_two_circles_intersecting_points(circles[i], circles[k])
            if res:
                points.extend(res)
    return points

def is_contained_in_circles(point, circles):
    for i in range(len(circles)):
        if (get_two_points_distance(point, circles[i].center) >= (circles[i].radius)):
            return False
    return True

def get_polygon_center(points):
    center = point(0, 0)
    num = len(points)
    for i in range(num):
        center.x += points[i].x
        center.y += points[i].y
    center.x /= num
    center.y /= num
    return center

def convertToDecimalDegress(metreDistance):
    return metreDistance/111320

def convertLatLngToUTM(lat, lng):
    (x, y, _, _) =utm.from_latlon(lat, lng)
    return x, y

def createUTMPoint(lat, lng):
    x, y = convertLatLngToUTM(lat, lng)
    print(x, y)
    return point(x,y)




if __name__ == '__main__' :

    p1 = createUTMPoint(55.94444938963575,-3.1869836524128914) #f17f
    p2 = createUTMPoint(55.94449107087541,-3.186941407620907) # fd81
    p3 = createUTMPoint(55.944432116316044,-3.186904862523079) # f155

    c1 = circle(p1, 6.12)
    c2 = circle(p2, 2.54)
    c3 = circle(p3, 500.26)

    circle_list = [c1, c2, c3]
    """, c3"""

    inner_points = []
    for p in get_all_intersecting_points(circle_list):
        if is_contained_in_circles(p, circle_list):
            print(p)
            inner_points.append(p) 

    print(inner_points)
    center = get_polygon_center(inner_points)
    (lat, lng) = utm.to_latlon(center.x, center.y, 30, 'U')
    print("Center is x: " + str(lat) + " y: " + str(lng))
