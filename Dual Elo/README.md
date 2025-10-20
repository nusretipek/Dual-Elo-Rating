# Dual Elo Rating

This folder contains the source code, headers, and pre-compiled binaries for the Dual Elo rating. The contents are organized as follows:

## Folder Structure

### 1. src/

The `src` folder contains the structured C++ source code for the Dual Elo rating. These files implement the core functionality of the rating.

### 2. include/

The `include` folder contains the header files necessary for compiling the Dual Elo rating.  
These headers define the interfaces and structures used throughout the source code.

## Executables

### 1. `DualEloRating`

- **Linux**: `DualEloRating` is built on Debian GNU/Linux 11 (g++ (Debian 10.2.1-6) 10.2.1 20210110) with:

  ```bash
  g++ src/*.cpp -o DualEloRating -ldlib -lpthread -Iinclude -std=c++17 -O2 -Wall
  ```

- **macOS**: `DualEloRating_macos` is compiled with Apple Clang 17.0.  
- **Windows**: `DualEloRating.exe` is compiled with MSVC (Visual Studio 2022).

## Building from Source

We include a cross-platform CMake project that downloads the appropriate version of `dlib` on first configure (CMake ≥ 3.16 recommended).

### Linux

```bash
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build --config Release
```

### macOS

```bash
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build --config Release
```

### Windows (MSVC)

```powershell
cmake -S . -B build -G "Visual Studio 17 2022" -A x64
cmake --build build --config Release
```

## Notes

1. **Preferred Environment**: For best performance and reproducibility, compile and run the Linux version (natively or under WSL/Docker).
2. **Modifying Runtime Parameters**: Configuration constants live in the headers under `include/`.
3. **Usage Information**: To view the CLI usage, run:

    ```bash
    ./DualEloRating -h
    ```

    This will output the usage information in a standard format, providing details on how to run the program and adjust its parameters.
