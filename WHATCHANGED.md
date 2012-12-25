## 0.0.4 → 0.1 (25-12-2012)
* Both a python API and a command line tool (tesstrain) are provided
* The 'font_properties' parameter is now required (it use to have a default path, which makes
    no sense as TesseractTrainer is now installable via pip/easy_install)
* The v0.1 is available on PyPI
* The test suite is no longer bundled, as it's pretty messy and monolithic, due to the creation of training files
  as the training process progresses
* Filename modification: __main__.py → tesstrain
* The horrid 'lib' directory was finally removed

## 0.0.3 → 0.0.4

 * The `tiffcp` dependency has been removed.
    We used `tiffcp` to merge individual tif files into a multipage one.
    Sunil Sheoran pointed out that it could be replaced by ImageMagick's
    `convert` command:
    `$ convert *.tif multipage.tif`

## 0.0.2 → 0.0.3
### Improvements:
* the tif file size has been reduced by 66% changing from RGB mode to greyscale
* the location of the `tiffcp` binary has been moved to `defaults.py` and is now stored
 as an environment variable

### Bugfixes:
* The training commands now run if the trainer is initialized with `verbose=False