export DEBIAN_FRONTEND=noninteractive
apt update

source /opt/ros/humble/setup.bash
mkdir -p /prebuilt_ws/src && cd /prebuilt_ws/src
git clone --depth 1 -b humble https://github.com/micro-ROS/micro_ros_setup.git
cd /prebuilt_ws && . /opt/ros/humble/setup.sh && rosdep init && rosdep update --rosdistro=humble
rosdep install --from-paths src --ignore-src -y
colcon build
. /prebuilt_ws/install/local_setup.sh
ros2 run micro_ros_setup create_agent_ws.sh
ros2 run micro_ros_setup build_agent.sh
rm -rf log/ build/ src/
