SR SignGen
===========

Generate an SR sign PDF, with or without an image.
The optional image, if used, should be square to prevent distortion.


Usage
-----

    ./signgen [-s SIZE] [-i IMAGE] -m MESSAGE -o OUTPUT

    Options:
        -s SIZE     where SIZE is 'a4' (only A4 paper is supported, currently).
        -i IMAGE    where IMAGE is an image file, either absolute, relative to
                    the current directory or in the images/ directory.
        -m MESSAGE  where MESSAGE is the message you would like to display.
        -o OUTPUT   where OUTPUT is the output PDF filname you want.


Examples
--------

Generateing a sign, with no image, saying *"Toilets"*:

    ./signgen -m Toilets -o toilets.pdf


Generating a sign, with an image, saying *"This event is being filmed"*:

    ./signgen -m "This event is being filmed" -i camera.png -o filming.pdf