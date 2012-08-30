## What changed from version 0.0.3 to 0.0.4?

 * The `tiffcp` dependency has been removed.
    We used `tiffcp` to merge individual tif files into a multipage one.
    Sunil Sheoran pointed out that it could be replaced by ImageMagick's 
    `convert` command: 
    `$ convert *.tif multipage.tif`

## What changed from version 0.0.2 to 0.0.3?
### Improvements:
* the tif file size has been reduced by 66% changing from RGB mode to greyscale
* the location of the `tiffcp` binary has been moved to `defaults.py` and is now stored
 as an environment variable
    
### Bugfixes:
* The training commands now run if the trainer is initialized with `verbose=False