# 🎣 Fishing Automation Script (Computer Vision + Threading)

A Python-based automation project showcasing **real-time color tracking**, **template matching**, and **multi-threaded control** using computer vision and keyboard simulation.  
Built for educational purposes to explore automation, image processing, and concurrency techniques in Python.

---

## 🚀 Features

- Real-time **color detection and tracking** using OpenCV  
- **Template matching** for object recognition within defined regions  
- **Multi-threaded architecture** (parallel monitoring and control)  
- Automated mouse and keyboard actions with **pyautogui** and **pynput**  
- Dynamic time-based event triggering with randomized intervals  
- Window activation and control using **pygetwindow**

---

## 🧠 Technologies

- **Python 3.x**
- `OpenCV`
- `numpy`
- `pyautogui`
- `mss`
- `pynput`
- `threading`, `time`, `random`, `cv2`, `pygetwindow`

---

## ⚙️ How It Works

1. The script continuously captures a specific region of the screen (`mss` + `OpenCV`).
2. Detects specific color patterns (e.g., tracked object or event indicator).
3. Executes automated mouse and keyboard actions when conditions are met.
4. Performs additional actions periodically, using separate threads for:
   - Color monitoring  
   - Timed input actions  
   - Screen scanning and template matching  

> ⚠️ **Note:** This project is for educational and testing purposes (automation and computer vision exploration).

---

## 📦 Example Project Structure

```
.
├── fishing_v3_GIT.py # Main automation script
├── templates/ # Folder with reference images for template matching
└── README.md # Documentation
```

---

## 🧑‍💻 Author

Developed by **Kamil Drzewiecki**  
Focus areas: Data Science • Automation • Computer Vision • Machine Learning  
📧 [[LinkedIn](https://www.linkedin.com/in/kamil-drzewiecki-ds/) / [GitHub link here](https://github.com/Drzewkam)]
