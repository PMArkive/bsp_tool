# bsp_tool
Python library for analysing .bsp files  

`bsp_tool` provides a Command Line Interface for analysing .bsp files  


## Installation
To use the latest **unstable** version, clone with `git`:
```
$ git clone git@github.com:snake-biscuits/bsp_tool.git
```

You can also clone with `pip`:

```
$ pip install git+https://github.com/snake-biscuits/bsp_tool.git
```

Or, use the latest stable release (August 2024 | 0.5.0 | Python 3.8-11):
```
$ pip install bsp_tool
```


## Fair Use
**Please do not use `bsp_tool` to copy or steal another creator's work**  
The primary goal of `bsp_tool` is to extend community mapping tools  


### Always
  - **Ask** the creator's permission before touching their work  
  - **Understand** that by default creator's works are under copyright  
    - [US Law Copyright FAQ](https://www.copyright.gov/help/faq/faq-general.html#mywork)
    - [US Copyright Duration](https://www.copyright.gov/help/faq/faq-duration.html)
      - [Circular 15a](https://www.copyright.gov/circs/circ15a.pdf)  
  - **Contact** the original creator to get their permission  
    - This can get complicated  
    - Some creators don't hold the copyright on their works  
      - often because of Company / Publisher contracts  
  - **Credit** the original creator; once you have permission to share a derivative work  
  - **Support** the official release

**DO NOT** use this tool to steal another creator's work  
**DO** use this tool to understand the `.bsp` format(s) and create more specific tools

> Be aware that this gets even more complicated with commercial projects


## Guides
[Basic Usage](./usage.html) <!-- Split up / include links to the wiki -->
<!-- [BSP format crash course](...) # include branch specific pages -->
[Extensions](./extensions.md)

## Supported Games
  * Arkane Studios
    - [Dark Messiah of Might & Magic Singleplayer](./supported/dark_messiah_sp.html)
    - [Dark Messiah of Might & Magic Multiplayer](./supported/dark_messiah_mp.html)
  * Id Software
    - [Quake](./supported/quake.html)
    - [Quake II](./supported/quake2.html)
    - [Quake III](./supported/quake3.html)
  * Infinity Ward
    - [Call of Duty](./supported/cod.html)
    - [Call of Duty 2](./supported/cod.html)
    - [Call of Duty 4: Modern Warfare](./supported/cod_mw.html)
  * [Nexon](./supported/nexon.html)
  * Respawn Entertainment
    - [Titanfall](./supported/titanfall.html)
    - [Titanfall 2](./supported/titanfall.html)
    - [Apex Legends](./supported/apex.html)
  * Valve Software
    - [GoldSrc](./supported/goldsrc.html)
    - [Source Engine](./supported/source.html)
    - [Left 4 Dead](./supported/left4dead.html)
    - [Alien Swarm](./supported/swarm.html)

## .bsp Format Reference
  [Timeline of "relevant" games](./timeline/games.html)  
  [Game engine bloodline](./timeline/engines.html)

## [Changelog](./CHANGELOG.html)
You can see a list of all changes in the [changelog](./CHANGELOG.html)


## Thanks
 * [Chris Strahl](https://github.com/Chrissstrahl)
   - Preserving **extensive** documentation, mods & source code for Quake 3 & Ubertools games
 * [Ficool2](https://github.com/ficool2)
   - Providing lots of current and detailed info on Source & helping track down some rarer titles
 * [Maxime Dupuis](https://github.com/maxdup)
   - Helping me identify multiple lumps in Source Engine .bsps
 * [REDxEYE](https://github.com/REDxEYE)
   - Being very open and actively collaborating on SourceIO & Titanfall .bsps
 * [Taskinoz](https://github.com/taskinoz)
   - Helping me find people that can actively use my research & tools
 * All of the Wiki Editors
   - Except the uncited `Id Tech 3 -> Treyarch NGL` on CoDWiki, that was a massive pain to verify


## Other tools

### Blender
 * [io_import_rbsp](https://github.com/snake-biscuits/io_import_rbsp)
   - Titanfall / Apex `.bsp` importer
 * [SourceIO](https://github.com/REDxEYE/SourceIO)
   - GoldSrc & Source Engine importer (`.bsp`, `.vmt`, `.vtf`, `.mdl`)
 * [SourceOps](https://github.com/bonjorno7/SourceOps)
   - Source Engine `.mdl` exporter
 * [PyD3DBSP](https://github.com/mauserzjeh/PyD3DBSP) (Archived)
   - Call of Duty 2 `.bsp` importer
 * [blender_io_mesh_bsp](https://github.com/andyp123/blender_io_mesh_bsp)
   - Quake 1 `.bsp` importer
 * [Blender_BSP_Importer](https://github.com/QuakeTools/Blender_BSP_Importer)
   - Quake 3 `.bsp` importer


## Contributing
At present the easiest way to contribute to the project is to add or extend a "branch script" for a game `bsp_tool` doesn't yet fully support  
[Learn More](https://github.com/snake-biscuits/bsp_tool/wiki)
