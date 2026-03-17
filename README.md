# 2025_Capstone_Design
2025_Capstone_Design_01-08
# Vision-based Distributed Swarm Robot Control System

본 프로젝트는 Vision 기반 온디바이스 AI를 활용하여  
GPS 및 중앙 서버 없이도 다수의 로봇이 협력적으로 움직일 수 있는  
분산 자율 제어 시스템을 구현하는 것을 목표로 합니다.

기존의 중앙집중형 제어 시스템은  
- 서버 병목 문제  
- GPS 의존성  
- 통신 지연 및 장애 취약성  

과 같은 한계를 가지며, 특히 실내 환경이나 GNSS-denied 환경에서  
안정적인 운용이 어렵습니다.

이를 해결하기 위해 본 프로젝트에서는  
각 로봇이 독립적으로 객체를 인식하고, 거리 및 방향을 추정하여  
통신 기반의 Consensus 알고리즘을 통해 협력적으로 행동하는  
분산 제어 구조를 설계하였습니다.

## 🚀 Key Idea

- 각 로봇에 Raspberry Pi 5 + Camera + RoboMaster S1을 탑재
- YOLOv8 기반 객체 탐지를 온디바이스에서 수행
- Bounding Box 기반 거리 추정 및 방향 계산
- Local 좌표계 기반 객체 위치 추정
- UDP Broadcast 기반 최소 정보 통신 (object count)
- Consensus 알고리즘을 통해 군집 이동 방향 결정

## ⚠️ Problem Definition

- GPS가 없는 환경에서 로봇의 위치 및 방향을 어떻게 추정할 것인가?
- 중앙 서버 없이 다수 로봇의 이동 방향을 어떻게 결정할 것인가?
- 저사양 임베디드 환경에서 실시간 인지-판단-제어를 어떻게 구현할 것인가?

## 💡 Proposed Solution

본 시스템은 다음 3단계 파이프라인으로 구성됩니다.

1. Perception (인지)
   - YOLOv8 기반 객체 탐지
   - Bounding Box → 거리 추정
   - Aspect Ratio → 객체 방향 추정

2. Estimation (판단)
   - Gimbal yaw + 거리 기반 Local 좌표 계산
   - Temporal Buffer를 통한 노이즈 보정
   - Local Object Map 생성

3. Control (제어)
   - Weighted Consensus 기반 이동 벡터 계산
   - Mecanum Wheel 변환을 통한 실제 이동
   - 장애물 회피 및 군집 이동 수행

## 🔑 Key Features

- GPS-Free / Server-Free 구조
- Vision 기반 위치 인식
- Distributed Consensus Control
- Cooperative Obstacle Avoidance
- Real-time On-device AI Inference

## 🏗️ System Architecture

- Hardware
  - RoboMaster S1
  - Raspberry Pi 5
  - Camera & Gimbal

- Software
  - YOLOv8 (ONNX)
  - OpenCV DNN
  - Python 기반 제어 시스템

- Communication
  - UDP Broadcast 기반 최소 데이터 통신

## 📊 Performance

- Inference Speed: 10~15 fps
- Distance Estimation Error: ±20~30 cm
- Consensus Convergence Time: 평균 15초 이내

## 🎯 Contribution

- 중앙 서버 없이도 협력 가능한 분산 로봇 시스템 구현
- 단일 카메라 기반 거리 및 방향 추정 알고리즘 개발
- 저사양 임베디드 환경에서 실시간 AI 추론 최적화
- 통신 부하를 최소화한 Consensus 알고리즘 설계