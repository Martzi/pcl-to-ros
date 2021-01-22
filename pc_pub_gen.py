#!/usr/bin/env python3

import zmq
import numpy as np
import open3d as o3d
from datetime import datetime

port = 5555

context = zmq.Context()
socket = context.socket(zmq.PUB)

socket.bind("tcp://*:%s" %port)

pointcloud = o3d.geometry.PointCloud()

while True:
    dt0 = datetime.now()

    pcd = o3d.geometry.PointCloud()

    # generate pointcloud mesh
    mesh = o3d.geometry.TriangleMesh.create_sphere()
    pcd = mesh.sample_points_poisson_disk(number_of_points=5, init_factor=5)
    
    # read pointcloud from file
    # pcd = o3d.io.read_point_cloud("person.pcd")

    # pyzmq send message && cast float64 to float32:
    pts = np.asarray(pcd.points).astype('float32')
    md = dict(dtype=str(pts.dtype), shape=pts.shape)

    socket.send_json(md, flags=0 | zmq.SNDMORE)
    socket.send(pts, flags=0)

    process_time = datetime.now() - dt0
    print("FPS: "+str(1/process_time.total_seconds()))
