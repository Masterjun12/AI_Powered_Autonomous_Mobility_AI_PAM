# LLM-Enabled Drone GCS
_A Ground Control Station Project with Integrated STT, LLM, and Vision Metadata for Defense Applications_

## Project Overview

This repository details the development of a next-generation Ground Control Station (GCS) for drones, integrating **Speech-to-Text (STT)**, **Large Language Models (LLM)**, and **vision-based metadata processing**. The system is engineered for **defense applications**, prioritizing secure, robust, and intelligent drone operations through natural language commands and automated mission reporting.

## System Architecture

### End-to-End Workflow

```
[Speech Input]
      ↓
[STT Engine]
      ↓
[LLM (Intent Parsing)]
      ↓
[Mission/Event Generation]
      ↓
[GCS/SDK Execution]
      ↓
[Vision Encoder (YOLOv8)]
      ↓
[Metadata Transmission]
      ↓
[LLM Report Generation]
```

## Hardware Platform

### Drone Platform: DJI Matrice 400 (M400)

- **Type:** Enterprise-grade quadcopter
- **Flight Time:** Up to 59 minutes
- **Payload Capacity:** Up to 6 kg
- **Sensors:** LiDAR, mmWave radar, fisheye vision, RTK positioning
- **Video Transmission:** Up to 40 km with O4 Enterprise Enhanced Video Transmission
- **Multi-Payload:** Supports up to 7 simultaneous payloads
- **Obstacle Avoidance:** Advanced, including power-line and terrain detection
- **Use Cases:** Defense, inspection, mapping, search & rescue, exploration[1][2][3]

### Onboard Computing Options

| Model                   | CPU/GPU Specs                                             | AI Performance | Notable Features                |
|-------------------------|----------------------------------------------------------|----------------|----------------------------------|
| NVIDIA Jetson Nano      | Quad-core ARM Cortex-A57, 128-core Maxwell GPU, 4GB RAM  | 472 GFLOPS     | Entry-level, low power           |
| Jetson Xavier NX        | 6-core ARM v8.2, 384-core Volta GPU, 8GB RAM             | 21 TOPS        | Multi-sensor, strong AI support  |
| Jetson Orin Nano        | 6-core Cortex-A78AE, up to 1024-core Ampere GPU, 8GB RAM | 40 TOPS        | High performance, compact        |
| Raspberry Pi 5          | Quad-core Cortex-A76, up to 8GB RAM                      | -              | Affordable, broad community      |
| Khadas Edge2            | 8-core RK3588S, Mali-G610 GPU, up to 16GB RAM            | 6 TOPS         | 8K video, Wi-Fi 6, AI-ready      |[4][5][6][7][8][9][10][11][12][13]

## STT (Speech-to-Text) Component

In this project, three leading STT libraries were benchmarked to find the optimal solution for recognizing voice commands for drone control. The research focused on evaluating accuracy, response time, and offline capabilities.

- **Google Speech Recognition:**
    - **Features:** As a cloud-based service, it demonstrates high accuracy for Korean language recognition but requires a mandatory internet connection. It excels in batch processing, and security considerations are necessary as voice data is sent to external servers.
    - **Experiment Results:** The highest recognition rate was achieved by preprocessing audio with `sounddevice` before sending it to the API, though this slightly increased processing time.

- **Vosk:**
    - **Features:** A fully offline STT engine that runs locally, ensuring fast response times and high security. It is optimized for real-time streaming.
    - **Experiment Results:** The default Korean model showed insufficient performance, resulting in the lowest recognition rate among the three libraries. It is concluded that domain-specific model fine-tuning is necessary.

- **OpenAI Whisper:**
    - **Features:** A state-of-the-art deep learning-based model. The `large-v3` model was used for this experiment, which can achieve high accuracy with GPU acceleration in a local environment.
    - **Experiment Results:** It delivered the best recognition accuracy. However, a significant drawback was the ~20 second delay from voice recording to text output, attributed to its high computational demand. Response speed improvements are needed for real-time control applications.

## LLM Component

The core objective of the LLM component is to **transform natural language user commands into structured JSON format** that the drone can execute. To achieve this, a custom dataset for Tello drone commands was built, and several Korean-language LLMs were fine-tuned using **PEFT (LoRA)** to compare their performance.

### Improvement Goals and Research
- **Build Tello Command Dataset (`tello_dataset.json`):** A dataset consisting of pairs of natural language Korean commands and their corresponding Tello drone commands (in JSON) was created for fine-tuning.
- **Fine-tune and Compare Korean LLMs:** The following models were fine-tuned using LoRA to evaluate their ability to generate correct JSON commands.
    - `beomi/Yi-Ko-6B`
    - `yanolja/KoSOLAR-10.7B-v0.2`
    - `EleutherAI/polyglot-ko-5.8b`
- **Inference Performance Analysis:** A qualitative analysis was performed to see how accurately each fine-tuned model converts complex or varied natural language commands into JSON. Detailed comparison results are available in the notebook (`Tello_FineTuning_and_Inference-다중쿼리.ipynb`).

### Requirements
- **Hardware:** A high-performance GPU such as an NVIDIA A100 with a CUDA environment.
- **Key Libraries:**
    - `torch`, `transformers`, `datasets`
    - `peft` (Parameter-Efficient Fine-Tuning)
    - `trl` (Transformer Reinforcement Learning)
    - `accelerate`

## SITL (Software-in-the-Loop) Component

The SITL component aims to execute the commands translated by the LLM in a realistic drone simulation environment. A user gives a command in natural language, and the system interprets and executes it on a virtual drone in the DroneKit-SITL environment.

### Implementation Goal
- Translate natural language commands into JSON-formatted commands via the LLM interface (`llm_interface.py`).
- The `command_parser.py` module parses the JSON command and invokes the corresponding control function defined in `drone_control.py`.
- The system communicates with the SITL simulator using the DroneKit library to monitor the drone's state and execute commands.

### Execution Guide
1. **Run the SITL Simulator:** Start the virtual drone using Mission Planner or the `dronekit-sitl` command.
   ```bash
   dronekit-sitl copter --home=37.5665,126.9780,0,180
   ```
2. **Connect MAVProxy:** Connect MAVProxy to the SITL instance to act as a GCS.
   ```bash
   mavproxy.py --master tcp:127.0.0.1:5760 --sitl 127.0.0.1:5501 --out 127.0.0.1:14550 --out 127.0.0.1:14551
   ```
3. **Set API Key:** Enter your Google API key in the `SITL/config.py` file.
4. **Run the Main Script:** Execute the main script from the `SITL` directory and enter natural language commands at the prompt.
   ```bash
   python main.py
   ```
   **Example Commands:**
   - `Connect to the drone.`
   - `Arm and take off to 15 meters.`
   - `Move 50 meters north.`
   - `Land and disconnect.`

## Vision Encoder

- **YOLOv8 Integration:**
  Real-time object detection, multi-scale, lightweight, and efficient for edge inference.
  Outputs structured metadata for mission reporting and situational awareness[14][15].

#### Example Metadata Format

```json
{
  "timestamp": "2025-07-14T14:22:00Z",
  "location": {"lat": 37.12345, "lon": 127.12345, "alt": 50},
  "objects": [
    {"type": "person", "confidence": 0.94, "bbox": [120, 80, 180, 200]},
    {"type": "vehicle", "confidence": 0.88, "bbox": [300, 150, 400, 250]}
  ],
  "image_id": "frame_000123"
}
```

## Example Voice Command to SDK Command Mapping

| Example Command                                  | LLM Output (Structured)         | DJI SDK/ROS Command Example              | Description                           |
|--------------------------------------------------|----------------------------------|------------------------------------------|---------------------------------------|
| Take off.                                        | CMD: TAKEOFF                    | `monitoredTakeoff()`                     | Take off                              |
| Recon waypoints A, B, and C.                     | CMD: GOTO_WAYPOINTS A,B,C       | `goToWaypoint('A')`, ...                 | Recon at waypoints A, B, C            |
| Find a person while maintaining 50 meters.       | CMD: HOLD_ALT 50; DETECT PERSON | `holdAltitude(50)`, `detectObject('person')` | Maintain 50m, detect person           |
| Go to the landing point.                         | CMD: GOTO_LANDPOINT             | `goToLandPoint()`                        | Move to landing point                 |
| Patrol the designated area.                      | CMD: PATROL AREA                | `patrolArea(area_id)`                     | Patrol designated area                |
| Track the vehicle.                               | CMD: TRACK VEHICLE              | `trackObject('vehicle')`                  | Track the vehicle                     |

## On-Premises Management Software

The system leverages **DJI FlightHub 2 On-Premises** for secure, scalable fleet management:

| Package Name                                                        | Description                                  |
|---------------------------------------------------------------------|----------------------------------------------|
| FlightHub 2 On-Premises Version Device Expansion (1 Device)         | Add 1 device to on-premises management       |
| FlightHub 2 On-Premises Version Basic Package (1 Device)            | Basic on-premises management for 1 device    |
| FlightHub 2 On-Premises Version Upgraded Validity (1Year/1Device)   | 1-year validity extension for 1 device       |
| FlightHub 2 On-Premises Version Device Expansion (5 Devices)        | Add 5 devices to on-premises management      |

- **Key Features:**
  - OpenAPI for secondary development
  - MQTT Bridge for efficient, secure message delivery
  - Modular frontend components for rapid integration[16]

## Getting Started

1. **Clone the Repository**
   ```bash
   git clone https://github.com/yourorg/llm-drone-gcs.git
   ```

2. **Install Dependencies**
   - See `requirements.txt` in each subdirectory (`STT`, `LLM`, `SITL`).

3. **Configure Models & API Keys**
   - Download/setup Korean models for STT/LLM as needed.
   - Set up your API keys in the configuration files.
   - Ensure ffmpeg is in your PATH for Whisper.

4. **Run Example Code**
   - See `/STT/`, `/LLM/`, `/SITL/` directories for individual component scripts and usage instructions.

## Defense-Oriented Design

- **Mission-Critical Reliability:**
  All modules are validated in operational scenarios for robustness.
- **Offline and Secure Operation:**
  Local execution ensures privacy and compliance.
- **Scalable and Modular:**
  Adaptable for various drone platforms and mission profiles.

## Key References

- [TypeFly: Flying Drones with Large Language Model](https://arxiv.org/abs/2312.14950)
- [LLM-DaaS: LLM-driven Drone-as-a-Service Operations from Text User Requests](https://arxiv.org/abs/2412.11672)
- [ROS-LLM: A ROS framework for embodied AI with task feedback and structured reasoning](https://arxiv.org/abs/2406.19741)
- [LLM-Land: Large Language Models for Context-Aware Drone Landing](https://arxiv.org/abs/2505.06399)
- [UAV-VLA: Vision-Language-Action System for Large Scale Aerial Mission Generation](https://arxiv.org/abs/2501.05014)
- [KIT-19: Korean Instruction Dataset for LLM Fine-Tuning](https://arxiv.org/html/2403.16444v1)

## Contact

For collaboration or questions, please contact the maintainer at `your.email@domain.com`.

[1] https://enterprise.dji.com/matrice-400
[2] https://www.dji.com/media-center/announcements/dji-release-matrice-400
[3] https://hp-drones.com/en/dji-matrice-400-power-precision-and-efficiency-at-the-peak-of-drone-technology/
[4] https://www.nvidia.com/en-us/autonomous-machines/embedded-systems/jetson-nano/product-development/
[5] https://www.waveshare.com/jetson-xavier-nx.htm
[6] https://connecttech.com/product/nvidia-jetson-orin-nano-4gb-module/
[7] https://thepihut.com/products/raspberry-pi-5
[8] https://techexplorations.com/blog/review/khadas-edge2-an-ai-ready-single-board-computer-powerhouse
[9] https://www.macnica.co.jp/en/business/semiconductor/manufacturers/nvidia/products/134045/
[10] https://www.macnica.co.jp/en/business/semiconductor/manufacturers/nvidia/products/134047/
[11] https://crg.co.il/catalog/jetson-orin-nano-series-4gb-8gb/
[12] https://www.waveshare.com/raspberry-pi-5.htm
[13] https://www.khadas.com/edge2
[14] https://encord.com/blog/yolo-object-detection-guide/
[15] https://docs.ultralytics.com/ko/tasks/detect/
[16] https://enterprise-insights.dji.com/blog/dji-flighthub-2-on-premises-officially-released
[17] https://enterprise.dji.com/matrice-400/specs
[18] https://enterprise.dji.com/kr/matrice-400/specs
[19] https://www.youtube.com/watch?v=Cc7UMhmshpI
[20] https://www.heliguy.com/blogs/posts/dji-flighthub-2-on-premises-enhanced-drone-data-security/