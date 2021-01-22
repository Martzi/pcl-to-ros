#!/usr/bin/env python

import numpy as np
import zmq
import sys

import rospy
import sensor_msgs.msg as sensor_msgs
import std_msgs.msg as std_msgs
from sensor_msgs.msg import PointCloud2


def recv_array_and_str(socket, flags=0, copy=True, track=False):
    md = socket.recv_json(flags=flags)
    msg = socket.recv(flags=flags, copy=copy, track=track)

    buf = buffer(msg)

    pts = np.frombuffer(buf, dtype=md['dtype'])

    return pts.reshape(md['shape'])


# format message to pointcloud2
def point_cloud_msg(points, parent_frame='base_link'):

    ros_dtype = sensor_msgs.PointField.FLOAT32 #
    dtype = np.float32
    itemsize = np.dtype(dtype).itemsize

    data = points.astype(dtype).tobytes()

    fields = [sensor_msgs.PointField(
        name=n, offset=i*itemsize, datatype=ros_dtype, count=1)
        for i, n in enumerate('rgbxyzi')]

    header = std_msgs.Header(frame_id=parent_frame, stamp=rospy.Time.now())

    return sensor_msgs.PointCloud2(
        header=header,
        height=points.shape[0],
        width=points.shape[1],
        is_dense=True,
        is_bigendian=False,
        fields=fields,
        point_step=points.dtype.itemsize,
        row_step=points.dtype.itemsize * points.shape[0],
        data=data                               
    )

# publish pointcloud2 data to ROS topic
def pc2pub():

    port = "5555"

    pub = rospy.Publisher('/pointcloud', PointCloud2, queue_size=10)
    rospy.init_node('pcl_publisher', anonymous=True)

    while not rospy.is_shutdown():

        socket.setsockopt(zmq.SUBSCRIBE, b"")
        if len(sys.argv) > 2:
            socket.connect("tcp://localhost:%s" %port)

        socket.connect("tcp://localhost:%s" % port)

        pub.publish(point_cloud_msg(recv_array_and_str(socket)))


if __name__ == '__main__':

    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    socket.setsockopt(zmq.SUBSCRIBE, b"")

    try:
        pc2pub()
    except rospy.ROSInterruptException:
        rospy.loginfo("error")
        pass
