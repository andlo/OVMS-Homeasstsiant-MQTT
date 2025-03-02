import json
import time

import paho.mqtt.client as mqtt

# MQTT broker details
# for now needs to be filed out here. Should be in configflow.

BROKER = "XXXX"
PORT = 1883
USERNAME = "XXXX"
PASSWORD = "XXXX"

# Base topic for Home Assistant discovery
DISCOVERY_TOPIC = "homeassistant/sensor"


# Function to delete autodiscovery message
def delete_discovery(sensor_id):
    topic = f"{DISCOVERY_TOPIC}/{sensor_id}/config"
    client.publish(topic, "", qos=1, retain=True)


# Function to publish autodiscovery message
def publish_discovery(
    sensor_id,
    name,
    unique_id,
    state_topic,
    unit_of_measurement,
    device_class,
    icon,
    availability_topic,
    payload_available,
    payload_not_available,
):
    payload = {
        "name": name,
        "unique_id": unique_id,
        "state_topic": state_topic,
        "unit_of_measurement": unit_of_measurement,
        "device_class": device_class,
        "icon": icon,
        "availability_topic": availability_topic,
        "payload_available": payload_available,
        "payload_not_available": payload_not_available,
        "device": {
            "identifiers": ["ovms_device"],
            "name": "OVMS Device",
            "model": "OVMS",
            "manufacturer": "Open Vehicle Monitoring System",
        },
    }
    topic = f"{DISCOVERY_TOPIC}/{sensor_id}/config"
    client.publish(topic, json.dumps(payload), qos=1, retain=True)


# MQTT on_connect callback
def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    client.subscribe("ovms/e-up/#")


# Determine device class and icon based on topic
def determine_device_class_and_icon(topic):
    if "soc" in topic or "soh" in topic or "12v" in topic:
        return "battery", "mdi:battery"
    elif "range" in topic or "odometer" in topic:
        return "distance", "mdi:map-marker-distance"
    elif "latitude" in topic or "longitude" in topic:
        return "None", "mdi:map-marker"
    else:
        return "None", "mdi:map-marker"


# MQTT on_message callback
def on_message(client, userdata, msg):
    topic = msg.topic
    sensor_id = topic.replace("/", "_")
    name = f"ovms-e-up-{topic}-" + \
        topic.split("/")[-1].replace("_", " ").title()
    unique_id = f"ovms_{topic}_{sensor_id}"
    unit_of_measurement = (
        "%"
        if "soc" in topic or "soh" in topic
        else (
            "V"
            if "12v" in topic
            else ("km" if "range" in topic or "odometer" in topic else "")
        )
    )
    device_class, icon = determine_device_class_and_icon(topic)
    availability_topic = (
        "ovms/e-up/metric/s/v3/connected"
        if "e-up" in topic
        else "ovms/w-eup/metric/s/v3/connected"
    )
    payload_available = "yes"
    payload_not_available = "no"

    # Delete existing discovery topic
    # delete_discovery(sensor_id)

    # Publish new discovery message
    publish_discovery(
        sensor_id,
        name,
        unique_id,
        topic,
        unit_of_measurement,
        device_class,
        icon,
        availability_topic,
        payload_available,
        payload_not_available,
    )


# Initialize MQTT client
client = mqtt.Client()
client.username_pw_set(USERNAME, PASSWORD)
client.on_connect = on_connect
client.on_message = on_message

client.connect(BROKER, PORT, 60)
client.loop_start()

# Keep the script running
while True:
    time.sleep(1)
