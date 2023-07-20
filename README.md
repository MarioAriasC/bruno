# Bruno

[Python 3.10](https://www.python.org/) implementation of
the [Monkey Language](https://monkeylang.org/)

Bruno has many sibling implementations

* Kotlin: [monkey.kt](https://github.com/MarioAriasC/monkey.kt)
* Crystal: [Monyet](https://github.com/MarioAriasC/monyet)
* Scala 3: [Langur](https://github.com/MarioAriasC/langur)
* Ruby 3: [Pepa](https://github.com/MarioAriasC/pepa)

## Status

The book ([Writing An Interpreter In Go](https://interpreterbook.com/)) is fully implemented. Bruno will not have a
compiler implementation

## Commands

Run pip install first 

```shell
python -m pip install -r requirements.txt
```

| Script                                  | Description                                        |
|-----------------------------------------|----------------------------------------------------|
| `pytest`                                | Run tests                                          |
| [`python benchmarks.py`](benchmarks.py) | Run the classic monkey benchmark (`fibonacci(35)`) |
| [`python repl.py`](repl.py)             | Run the Bruno REPL                                 |

## Compiling using [mypyc](https://mypyc.readthedocs.io/en/latest/index.html)

You can compile the benchmarks using mypyc.

```shell
mypyc benchmarks_mypyc.py
```

And then run it with:

```shell
python -c "import benchmarks_mypyc"
```

On my Linux VM:

```
                                                                                                                       
        a8888b.           Host        -  mario@pop-os                                                                   
       d888888b.          Machine     -  VMware, Inc. VMware Virtual Platform None                                      
       8P"YP"Y88          Kernel      -  6.2.6-76060206-generic                                                         
       8|o||o|88          Distro      -  Pop!_OS 22.04 LTS                                                              
       8'    .88          DE          -  Pop:GNOME                                                                      
       8`._.' Y8.         WM          -  GNOME Shell (X11)                                                              
      d/      `8b.        Packages    -  2108 (dpkg), 23 (cargo), 11 (flatpak)                                          
     dP        Y8b.       Terminal    -  tilix                                                                          
    d8:       ::88b.      Shell       -  bash                                                                           
   d8"         'Y88b      Uptime      -  1d 4h 16m                                                                      
  :8P           :888      CPU         -  AMD Ryzen 9 5900HX with Radeon Graphics (8)                                    
   8a.         _a88P      Resolution  -  1280x800, 1280x800, 1280x800, 1280x800, 1280x800, 1280x800, 3440x1440, 1280x800
 ._/"Yaa     .| 88P|      CPU Load    -  4%                                                                             
 \    YP"    `|     `.    Memory      -  7.9 GB/16.4 GB                                                                 
 /     \.___.d|    .'                                                                                                   
 `--..__)     `._.'      
```

The compiled benchmarks took 577.065 seconds against 645.984 seconds, overall a 20% increase on performance