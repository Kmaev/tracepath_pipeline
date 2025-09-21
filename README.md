# TracePath Framework

## General

**TracePath Framework** is a pipeline setup (currently in development 😅).  
The idea is to create a **starter kit** with clean practices, useful tools, and just enough flexibility to grow with your projects.

It runs on [Rez](https://github.com/AcademySoftwareFoundation/rez) — an open-source package and environment manager designed for VFX, animation, and game development pipelines.

---

## Current Features

### Trace Project Index
- Tool to generate a **project folder structure**
- Define **assets, sequences, shots, tasks, and required software**
- Currently supports a **Houdini folder structure template**

### TracePath Framework
- Full **terminal context navigation** between tasks
- **Houdini tools** for:
  - Scene versioning  
  - USD HDAs (e.g., save and load USD scenes for collaboration)
- Prototype **publishing system** (JSON-based) with:
  - Automated versioning of USD files with **comment tracking**

---

## Roadmap

- **At this stage of development the main focus was put more towards**  
  - Project creation  
  - Environment setup and navigation  
  - Versioning for Houdini scene files and USD files  

- **Next steps**  
  - Expanded **USD workflows inside Houdini**

---

## Installation

1. **Clone this repository**  
   Make sure you have the repo downloaded locally.

2. **Set environment variables**  
   Add the following to your shell config (`.bashrc`, `.zshrc`, etc.):

   ```bash
   # Project Path — where your projects live
   export PR_PROJECTS_PATH="/Users/kmaev/Documents/hou_dev/houdini_scenes/Projects"

   # Tracepath Framework Root — root folder of this repo
   # (TODO: add screenshot of folder structure)
   export PR_TRACEPATH_FRAMEWORK="/Users/kmaev/Documents/hou_dev/tracepath_pipeline/"

   # Rez in PATH (don’t modify this line)
   export PATH="$PR_TRACEPATH_FRAMEWORK/rez/bin/rez:$PATH"

   # Rez package locations
   export REZ_LOCAL_PACKAGES_PATH="/Users/kmaev/Documents/hou_dev/local_rez_packages"
   export REZ_RELEASE_PACKAGES_PATH="/Users/kmaev/Documents/hou_dev/rez_packages"

   # Combined Rez packages path (don’t modify this line)
   export REZ_PACKAGES_PATH=$REZ_LOCAL_PACKAGES_PATH:$REZ_RELEASE_PACKAGES_PATH

  <img width="643" height="187" alt="image" src="https://github.com/user-attachments/assets/9e92130f-6ada-4900-8556-5d8b7a65f684" />

  **Note:** Linux users may need to perform these additional steps to properly build and run the USD package, depending on their distribution.
  **Install CMake**
  ```bash
  sudo apt update
  sudo apt install -y cmake
  ```

  **Verify installation**
  ```bash
  cmake --version
  ```
  **Install X11 libraries (needed for GUI/OpenGL support, e.g., MaterialX and UsdView)**
  ```bash
  sudo apt install -y \
  libx11-dev \
  libxext-dev \
  libxrender-dev \
  libxrandr-dev \
  libxi-dev \
  libxt-dev
  ```
3. **Install Python 3.11**
Rez and TracePath expect Python 3.11.

4. **Bootstrap Rez**
```bash
python $PR_TRACEPATH_FRAMEWORK/setup/bootstrap.py
```
5. **Deploy USD + Rez packages**
```bash
python $PR_TRACEPATH_FRAMEWORK/setup/automated_deploy.py
```
6. ## Houdini HDAs and Toolbar are stored in:

`tracepath_pipeline/modules/tracepath/resources/`  

- **HDAs** → copy into your Houdini `otls/` folder  
- **Houdini shelves** → copy into your Houdini `toolbar/` folder

**That’s it!**

At this point, you should see packages created under your $REZ_LOCAL_PACKAGES_PATH.

- arch  
- os  
- platform  
- python  
- PySide6  
- PySide6_Addons  
- PySide6_Essentials  
- shiboken6  
- PyOpenGL  
- PyOpenGL_accelerate  
- houdini  
- usd  
- project_index  
- tracepath  
- tracepath_terminal  

<img width="881" height="327" alt="image" src="https://github.com/user-attachments/assets/201587c0-ffdd-440e-a4ac-f4f9cf39bdde" />

## How to Use

Inside `tracepath_pipeline/exec` you’ll find an executable for macOS.  
Or just launch directly from the terminal:

```bash
rez env project_index usd -- trace_project
```
This opens the Project Index UI so you can create your first project.

<img width="898" height="724" alt="image" src="https://github.com/user-attachments/assets/f0caf92f-c7d8-463f-915e-08dc6604dbe5" />

## Project Workflow

Once a project exists, you can use the **TracePath Terminal** either from the executable or by running:

```bash
rez env tracepath_terminal
```

Common commands inside TracePath Terminal
Load a project
```bash
load <your_project_name>
load MyProjectExample
```
Jump into your task directory
```bash
cdtask
cdtask seq1 sh0010 fx_destruction
```
Run Houdini
```bash
houdini
```
<img width="569" height="230" alt="image" src="https://github.com/user-attachments/assets/3c621ebc-014c-49c3-a796-ad20059b27e6" />

## Explanation

In the TracePath framework:  
- `seq1` is a **group**  
- `sh0010` is an **item**  
- `fx_destruction` is the **task**
  
These environment variables were introduced to avoid a hard split between shots and assets.

In practice:  
- `seq1`, `seq2`, or `assets` act as **groups**  
- `sh0010`, `sh0020`, or `building_01`, `building_02` act as **items** within those groups
- `task` is the **task** 🙃 (e.g., `fx`, `env`, `fx_destruction`, `grooming`, `lookdev`)

Please check the example project for more details and a visual explanation of how projects are structured.  

If the task doesn’t exist, TracePath will offer to create it on the fly — no need to reopen the Project Index UI.
Add Software Folders to a Task:
```bash
add houdini
```
The `show_context` command will display your current context:
```bash
show_context
```
<img width="569" height="46" alt="image" src="https://github.com/user-attachments/assets/1db516c6-761d-4346-9761-54330f4137f9" />

## Tips

- All software templates live in:  
  `tracepath_pipeline/config/applications_templates.json`  
  Add new software there if needed.

- Your project data (sequences, shots, assets, tasks) is stored in:  
  `tracepath_pipeline/config/trace_project_index.json`

## Houdini Tools:
**Houdini Scene File Versioning System**
<img width="945" height="253" alt="image" src="https://github.com/user-attachments/assets/1a1e4734-c0f1-4ebc-b168-320b6192637a" />
<img width="945" height="249" alt="image" src="https://github.com/user-attachments/assets/18dd06d1-8c44-412d-b369-aa9b6da37017" />

**Scene Browser to open and manage saved scenes in the context of each task.**
<img width="801" height="523" alt="image" src="https://github.com/user-attachments/assets/17af35f0-75e4-43c4-92ea-c5a1d4af694f" />

**Houdini HDAs**

**Note:** Both HDAs are still in the prototype stage

**TracePath Load USD Stage** – an HDA for loading published USD task edits, designed to simplify collaboration between artists.
Handles time-sampled data and provide built-in stitching of per-frame USD files, simplifying the setup and editing of animated assets.

<img width="747" height="370" alt="image" src="https://github.com/user-attachments/assets/c4125428-a20f-453b-9075-de38c7469397" />

**TracePath USD Write**– an HDA to write USD files with versioning and a publishing system, with the possibility to attach comments to published versions.

<img width="747" height="555" alt="image" src="https://github.com/user-attachments/assets/da0c7360-7830-467e-aa5e-767de508b35d" />

## Important Note!

This project is still under development. If you find bugs, please report them 🙂

Keep in mind this isn’t a bulletproof framework that will handle absolutely everything.
Please use it in the spirit of its original intention and design. 🙂






