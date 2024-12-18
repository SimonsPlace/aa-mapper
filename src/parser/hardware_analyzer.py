import os
import re
import logging

class HardwareAnalyzer:
    """
    Analyzes a React Native project for hardware-specific dependencies.
    """

    def __init__(self):
        self.hardware_patterns = {
            "FaceID": r"\bFaceID\b",
            "TouchID": r"\bTouchID\b",
            "Biometric": r"react-native-(fingerprint-scanner|biometrics|face-id)",
            "Camera": r"react-native-camera|expo-camera",
            "Sensor": r"react-native-sensors",
            "GPS": r"Geolocation|react-native-geolocation-service",
            "Bluetooth": r"react-native-(bluetooth-classic|ble-plx|bluetooth-serial)",
            "NFC": r"react-native-nfc-manager",
            "Network Communication": r"(socket\.io|websockets|fetch|axios).*SAT_PIN|CASH_DRAWER",
            "Printers": r"zebra|react-native-zebra",
        }

        self.hardware_recommendations = {
            "FaceID": "Use react-native-biometrics for cross-platform biometric authentication.",
            "TouchID": "Use react-native-biometrics for cross-platform biometric authentication.",
            "Biometric": "Use react-native-biometrics or Expo Local Authentication.",
            "Camera": "Use react-native-camera or Expo Camera for cross-platform camera functionality.",
            "Sensor": "Use react-native-sensors for cross-platform sensor access.",
            "GPS": "Use react-native-geolocation-service for cross-platform GPS access.",
            "Bluetooth": "Use react-native-ble-plx for modern Bluetooth connections.",
            "NFC": "Use react-native-nfc-manager for NFC integration.",
            "Network Communication": "Ensure SAT PIN terminals and cash drawers support secure communication protocols.",
            "Printers": "Use react-native-zebra for Zebra printer integration or alternatives compatible with Android.",
        }

    def analyze(self, project_path):
        """
        Analyzes the project for hardware dependencies.
        """
        hardware_issues = []

        for root, _, files in os.walk(project_path):
            for file in files:
                if file.endswith(".js") or file.endswith(".tsx"):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            content = f.read()

                            for hardware, pattern in self.hardware_patterns.items():
                                matches = re.finditer(pattern, content)
                                for match in matches:
                                    line_number = content[:match.start()].count("\n") + 1
                                    hardware_issues.append({
                                        "file_path": file_path,
                                        "line_number": line_number,
                                        "hardware_type": hardware,
                                        "recommendation": self.hardware_recommendations.get(hardware, "No recommendation available."),
                                        "platform_specific": "Compatible with Android" if hardware != "FaceID" else "iOS Specific",
                                    })
                    except Exception as e:
                        logging.error(f"Error reading file {file_path}: {e}")

        return hardware_issues
