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


# 🚗 Supported ECUs

The current version has been tested on the following **Bosch ME7.5 1MB** software variants:

- 1.8T 20V 150HP
- 1.8T 20V 180HP
- 1.8T 20V 210HP
- 1.8T 20V 225HP

Support for additional ME7.5 variants is continuously being expanded.

---

# 🗺️ Supported Maps

The installer automatically locates the following calibration maps:

* 📍 KFZWMN
* 📍 KFNWEGM
* 📍 KFTVSA
* 📍 KFTVSAKAT


## 🔥 Pops & Bangs Profiles

The installer provides three carefully calibrated Pops & Bangs profiles. Each profile adjusts the ignition retard (`KFZWMN`) to control the intensity of the exhaust pops while keeping the remaining calibration parameters identical. This ensures consistent operation, allowing you to choose the desired sound level without affecting the activation strategy.

### Modified Calibration Maps

#### 📍 KFZWMN – Ignition Retard

Controls the ignition timing during the Pops & Bangs event. Increasing ignition retard shifts combustion later into the exhaust stroke, producing louder and more aggressive crackles and bangs.

| Profile       | KFZWMN (Signed) | Ignition Retard | Effect                            |
| ------------- | --------------: | --------------: | --------------------------------- |
| 🟢 **Low**    |         **-26** |      **-19.5°** | Mild pops and crackles            |
| 🟡 **Medium** |         **-33** |     **-24.75°** | Louder and more frequent pops     |
| 🔴 **High**   |         **-40** |      **-30.0°** | Maximum aggressive pops and bangs |

---

#### 📍 KFNWEGM – Fuel Cut RPM Threshold

Defines the engine speed threshold used by the Pops & Bangs strategy. The installer sets the entire map to **170**, corresponding to **6800 RPM**, allowing the effect to remain active across the full upper RPM range.

**Modified value:** **170** (**6800 RPM**)

---

#### 📍 KFTVSA – Ignition Retard Duration

Defines the duration of the ignition retard after throttle lift-off. The installer sets the map to **255** (**2.55 seconds**), ensuring a consistent and predictable Pops & Bangs effect.

**Modified value:** **255** (**2.55 seconds**)

---

#### 📍 KFTVSAKAT – Catalyst Protection Delay

Defines the catalyst protection delay associated with the ignition retard strategy. The installer sets the map to **255** (**10.2 seconds**), matching the behavior of the original application.

**Modified value:** **255** (**10.2 seconds**)

---

### Summary

All profiles use the same supporting calibration values:

* ✅ **Single Ignition Strategy**
* ✅ **KFNWEGM:** **170** (**6800 RPM**)
* ✅ **KFTVSA:** **255** (**2.55 seconds**)
* ✅ **KFTVSAKAT:** **255** (**10.2 seconds**)

The **only** parameter that changes between the available profiles is **KFZWMN (Ignition Retard)**, allowing you to select the desired Pops & Bangs intensity while preserving identical activation behavior and timing across all presets.


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
