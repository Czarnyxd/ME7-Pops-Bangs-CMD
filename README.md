# 🔥 Bosch ME7.5 Pops & Bangs Installer

An open-source command-line utility for installing **Pops & Bangs** on **Bosch ME7.5 (1MB)** ECUs.

The application automatically searches for the required calibration maps, applies the selected Pops & Bangs profile, and saves the modified firmware as a new file without overwriting the original BIN.

---

# ✨ Features

* ✅ Automatic map detection
* ✅ Supports Bosch ME7.5 **1MB** ECUs
* ✅ Three available profiles

  * 🟢 Low
  * 🟡 Medium
  * 🔴 High
* ✅ Automatic output file creation
* ✅ Detailed modification log
* ✅ Original BIN is never overwritten
* ✅ Simple command-line interface
* ✅ Open Source

---

# 🗺️ Supported Maps

The installer automatically locates the following calibration maps:

* 📍 KFZWMN
* 📍 KFNWEGM
* 📍 KFTVSA
* 📍 KFTVSAKAT

---

# 🚀 Usage

Run the program from the command line:

```bash
PopsAndBangs_CMD.exe input.bin
```

or

```bash
python PopsAndBangs_CMD.py input.bin
```

After selecting the desired profile, the installer will create a new modified BIN file.

### 📁 Example

```text
Input:
test.bin

Output:
test_POPS_MEDIUM.bin
```

The original firmware file is **never modified**.

---

# 📄 Example Log

```text
Bosch ME7.5 Pops & Bangs Installer v1.0

Input: test.bin
Output: test_POPS_MEDIUM.bin
Profile: Medium

KFZWMN: 0x0174C4
KFNWEGM: 0x0199C0
KFTVSA: 0x0199E8
KFTVSAKAT: 0x019A10

Changed bytes: 103

ADDRESS    OLD  NEW  MAP
0x017524   03   DF   KFZWMN
0x017525   02   DF   KFZWMN
...
0x019A2F   00   FF   KFTVSAKAT
```

Each modified byte includes:

* 📍 Memory address
* 📖 Original value
* ✏️ New value
* 🗺️ Map name

---

# ⚠️ Checksum

**This tool does NOT correct the ECU checksum.**

After generating the modified BIN file, you **must** correct the checksum before flashing the ECU.

Compatible tools include:

* ✔️ me7sum
* ✔️ Other Bosch ME7 checksum utilities

> **Flashing a BIN with an invalid checksum may result in an ECU that does not operate correctly.**

---

# 🛡️ Disclaimer

This software is intended for **educational, research and development purposes**.

The user is solely responsible for any modifications performed on an ECU and for ensuring that the resulting firmware is suitable for the intended application.

💾 Always keep an untouched backup of the original firmware before making any modifications.

---

# 🤝 Contributing

Contributions are welcome!

Feel free to:

* 🐞 Report bugs
* 💡 Suggest improvements
* 🔧 Submit pull requests

---

# 📜 License

This project is released as **Open Source**.
