# 🧠 Voice-Interactive Chatbot  
A Python-based intelligent assistant that supports **voice commands, text chat, NLP-based responses, GUI interaction, a built-in maze game, calculator, and a Morse code translator** — all in one application.

🏆 **Winner: 2nd Place out of 30 teams** in college hackathon.

---

## ✅ Features

### 🎤 Voice Recognition
- Uses `SpeechRecognition` + Google STT  
- Converts speech → text  
- Handles timeouts & errors gracefully  

### 🔊 Text-to-Speech (TTS)
- Uses `pyttsx3`  
- Smooth non-blocking speech output  
- Implemented using **Threading + Queue**  

### 💬 NLP Chatbot (NLTK)
- Rule-based chatbot using NLTK Chat pairs  
- Regex-based intent detection  
- Replies using both text & voice  
- Handles greetings, queries, jokes, commands  

### 🪟 GUI Interface (Tkinter)
- Full chat interface  
- Input box + send button + voice button  
- Dynamic message rendering  
- Popup windows for mini apps  

### 🌐 Website Automation
Voice commands can open:
- Google  
- YouTube  
- ChatGPT  
- Instagram  
- Facebook  
- Netflix  
- Hotstar  
- And more  

Example:  
**“open youtube” → launches YouTube automatically**

---

## 🎮 Mini Apps (Integrated)

### 🟣 1. Maze Runner Game (Pygame)
- Random maze generation  
- Player movement with arrow keys  
- Timer countdown  
- Win/Lose message  
- Collision detection  

### 🔢 2. Calculator
- Tkinter-based calculator  
- Real-time input  
- Expression evaluation  
- Clear function  

### 🔤 3. Morse Code Translator
- Text → Morse code  
- Morse → Text  
- Tkinter GUI with input/output boxes  
- Error handling included  

---

## ✅ Tech Stack

### **Languages**
- Python 3  

### **Libraries**
- SpeechRecognition  
- PyAudio  
- pyttsx3  
- nltk  
- pygame  
- tkinter (built-in)  
- queue & threading (built-in)  
- webbrowser (built-in)  
- re, random, time, os (built-in)  
- requests (if using weather API)  

---

## ✅ How to Run

### 1️⃣ Clone the repository
```bash
git clone https://github.com/sujala292005/Voice-Interactive-Chatbot
cd Voice-Interactive-Chatbot
