# AFM_Data_Fusion
Finding tiff and gwy files in folder, extracting time of measurement, assembling  them in gwy file with multible dataframes in a container. Therefore the dataframes can be used for correlation analysis. For this purpose, see other repository [Current_AFM_AutoScript]( https://github.com/TilloStralka/Current_AFM_AutoScript)

# Environment Setup and Issues

This project uses the [Gwyddion API](http://gwyddion.net/documentation.shtml), which requires specific setup for Python and Docker. Follow the steps below to ensure proper installation and usage.

---

## **Docker Installation for macOS**

If you are using macOS 10.15 or earlier:
- Download the appropriate Docker version from this link:
  [Docker for macOS 10.15 and older](https://desktop.docker.com/mac/main/amd64/93002/Docker.dmg)
- After installation, disable Docker's auto-update feature to prevent unintended upgrades to incompatible versions.

---

## **Installing and Using Docker**

### **1. Install Docker**
Download and install Docker or Docker Desktop from [Docker's official site](https://www.docker.com/).


### **2.A The more simple version is to use docker command line interface** 
Not a docker image / container to download yet. 
```bash
docker pull https://github.com/TilloStralka/AFMDataConverter
```

### **2.B The more complex version is to use the docker image from the repository**

The build process has been adjusted in the repo with a .json file, and you need to navigate to the .development folder first.
The process takes quite long because the apt-get process is time-consuming due to the graphical user interface. Subsequent starts will be significantly faster.


### **2. Clone the Repository**
Clone the repository containing the Docker configuration:
```bash
git clone https://github.com/AFM-SPM/gwyddion-python.git
cd gwyddion-python
```

## **3. Build the Docker Image**
Build the image locally using the following command:

```bash
docker build -t gwyddion-python .
```

## **4. Launch and Test Container**
Run the container interactively:
```bash
docker run -it gwyddion-python /bin/bash
```

To verify the container is running:
```bash
docker ps
```



## **5. Test Python and Gwyddion API**
Once inside the container, verify the setup:

```bash
xvfb-run python
import gwy
import gwyutils
print("Gwyddion API setup successful!")
```

## **6. Working with VSCode**
- Install Docker extension for VSCode
- Install the Remote Development extension
- Connect to the container

Open the VS Code Command Palette (Ctrl+Shift+P or Cmd+Shift+P on macOS).
Search for: "Dev Containers: Attach to Running Container" and select it.

To view running containers in a separate terminal (outside the Docker container):
```bash
docker ps
```

## **7. Rebuild and Start with VSCode**
Ensure the extension is installed:
1. Open your project in VS Code
2. Open Command Palette (⇧⌘P / Ctrl+Shift+P)
3. Type "Dev Containers: Rebuild and Reopen in Container" and select it
VS Code will use your devcontainer.json and Dockerfile to create and start the container.

Alternatively:
- Click the green icon in the bottom left corner of the status bar
- Select "Rebuild and Reopen in Container"

## **8. Build Process Notes**
When selecting "Dev Containers: Rebuild and Reopen in Container", the building process might not show visible progress. The initial build can take considerable time (around 30 minutes) due to package updates and dependencies. This is primarily caused by outdated packages and potential connection issues.

**Important:** Always prefix your Python commands with xvfb-run:
```bash
xvfb-run python program_name.py
```



## **Alternative Manual Setup (Not Recommended)**

### **1. Python 2.7 Installation**
Install Python 2.7 in a separate environment (e.g., using [conda](https://docs.conda.io/)) to avoid conflicts with modern Python installations.

### **2. Install PyGTK**
- **On macOS**, use Homebrew:
  ```bash
  brew install gtk+ pygtk
  ```

### **3. Add PyGwy to the PATH**
Locate the pygwy files (e.g., /usr/share/gwyddion/pygwy) and add them to your Python script:

```python
import sys
sys.path.append('<path_to_pygwy>')
```

## **Additional Resources**
- Gwyddion Documentation
  [http://gwyddion.net/documentation.shtml](http://gwyddion.net/documentation.shtml)
- Gwyddion Python Bindings
  [http://gwyddion.net/documentation.shtml#pygwy](http://gwyddion.net/documentation.shtml#pygwy)
