import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from std_msgs.msg import String
from cv_bridge import CvBridge
import cv2

class QRNode(Node):
    def __init__(self):
        super().__init__('qr_node')

        self.subscription = self.create_subscription(
            Image,
            '/camera/image_raw',
            self.process_frame,
            10
        )

        self.publisher_ = self.create_publisher(String, '/qr_data', 10)
        self.bridge = CvBridge()
        self.detector = cv2.QRCodeDetector()

    def process_frame(self, msg):
        frame = self.bridge.imgmsg_to_cv2(msg, 'bgr8')
        data, bbox, _ = self.detector.detectAndDecode(frame)

        if bbox is not None and data:
            self.get_logger().info(f"QR Detected: {data}")
            self.publisher_.publish(String(data=data))

def main(args=None):
    rclpy.init(args=args)
    node = QRNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
