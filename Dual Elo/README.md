# Dual Elo Rating

This folder contains the source code, headers, and pre-compiled binaries for the Dual Elo rating. The contents are organized as follows:

## Folder Structure

### 1. src

The `src` folder contains the structured C++ source code for the Dual Elo rating. These files implement the core functionality of the rating.

### 2. include

The `include` folder contains the header files necessary for compiling the Dual Elo rating. 
These headers define the interfaces and structures used throughout the source code.

## Executables

### 1. `DualEloRating`

The `DualEloRating` file is the Linux binary compiled on Debian GNU/Linux 11. The following compilation flags were used:

```bash
g++ src/*.cpp -o DualEloRating -ldlib -lpthread -Iinclude -std=c++17 -O2 -Wall
```

The `DualEloRatingWindows.exe` file is the Windows executable compiled using MinGW-w64 with static linking on Debian GNU/Linux 11. The following compilation flags were used:

```bash
x86_64-w64-mingw32-g++-posix src/*.cpp -o DualEloRatingWindows.exe -L[PATH]/dlib -ldlib -static-libgcc -static-libstdc++ -static -lwinpthread -I[PATH]/dlib -I[PATH]/include -std=c++17 -flto -O2 -Wall
```

**For MacOS, we do not provide executable. Please follow the Linux compilation instructions, ensuring g++ is installed.**

## Notes

1. **Windows Performance**: The Windows executable (`DualEloRatingWindows.exe`) is not optimized due to cross-compilation and linkage limitations. As a result, it runs approximately 10x slower than the Linux binary. If you are using Windows, consider compiling the code natively for better performance. For native compilation, you will first need to compile the [dlib library](http://dlib.net/compile.html) on Windows.
2. **Performance**: For the best performance, it is advised to compile the source code yourself. Even on Windows, you can achieve better performance by compiling the code using the Windows Subsystem for Linux (WSL). To do this, first, compile [dlib in Linux](http://dlib.net/compile.html) within the WSL environment.
3. **Modifying Runtime Parameters**: To modify the runtime parameters of the Dual Elo rating, please refer to the header files in the `include` folder.
4. **Usage Information**: To view the usage information for the Dual Elo rating, you can run the following command:

    ```bash
    ./DualEloRating -h
    ```

    This will output the usage information in a standard format, providing details on how to run the program and adjust its parameters.
