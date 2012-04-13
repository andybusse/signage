#!/usr/bin/env python

import argparse, tempfile
import sys, os, subprocess, shutil

TEMPLATE_NAME = 'Mr Bee'

class Badge(object):
    def __init__(self, name, template_svg='templates/name_badge.svg'):
        self.name = name
        self.template_svg = template_svg

    def generate_SVG(self, output_file, template=None):
        """
        Generates a SVG by performing substitutions on the given `template`,
        writing it to `output`.
        """

        if template is None:
            template = self.template_svg

        # read template SVG
        with open(template, 'r') as f:
            template_str = f.read()

        # perform substitutions
        subs = [(TEMPLATE_NAME,  self.name)]

        for replace, replace_with in subs:
            template_str = template_str.replace(replace, unicode(replace_with))

        # write output SVG
        with open(output_file, 'w') as f:
            encoded = template_str.encode('UTF-8')
            f.write(encoded)

    def _inkscape(self, in_file, out_file, type):
        """Run inkscape to convert the SVG to something else"""

        format_options = {'pdf': ['-A'], 'ps': ['-T', '-P']}[type.lower()]
        out_err = os.tmpfile()
        if subprocess.check_call(['inkscape'] + format_options + [out_file, in_file],
                                 stdout=out_err, stderr=out_err):
            raise OSError("Unable to convert SVG to {0}".format(type))
        out_err.close()

    def _inkscape_generate(self, fname, type, template=None):
        tmp_fd, tmp_fname = tempfile.mkstemp()
        self.generate_SVG(tmp_fname, template)
        self._inkscape(tmp_fname, fname, type)
        os.close(tmp_fd)
        os.remove(tmp_fname)


    def generate_PDF(self, fname, template=None):
        """Generate a PDF and save it as `fname`"""
        self._inkscape_generate(fname, 'pdf', template)


    def generate_PS(self, fname, template=None):
        """Generate a PS and save it as `fname`"""
        self._inkscape_generate(fname, 'ps', template)


def merge_ps_files(output_fname, input_fnames):
    """
    Given a series of input ps files, merge them into a single
    ps file, 3up, on A4 paper, and save it as `output_fname`.
    """

    if len(input_fnames) == 0:
        raise ValueError("Input files needed")

    cmd_format = ("psmerge {files} | "
                  "psnup -r"
                  " -W{ticket_width}"
                  " -H{ticket_height}"
                  " -m{margin}"
                  " -p{paper_size}"
                  " -{n} -s1 "
                  "> {output}")

    call_dict = {'files':        "'" + "' '".join(input_fnames) + "'",
                 'ticket_width':  '114.89mm',
                 'ticket_height': '77.89mm',
                 'margin':        '0cm',
                 'paper_size':    'a4',
                 'n':             '4',
                 'output':        output_fname}

    subprocess.check_call(cmd_format.format(**call_dict), shell=True)


def ps2pdf(input_fname, output_fname):
    """Call ps2pdf on a ps file and save it somewhere."""

    cmd_format = "ps2pdf -dPDFX '{input}' '{output}'"
    subprocess.check_call(cmd_format.format(input=input_fname,
                                            output=output_fname), shell=True)

def generate_and_merge_ps(output_fname, names):
    """
    Given a list of names, create a postscript bagde for each username
    and merge them all onto
    3up arangement.  The output is a postscript file.
    """

    files = []
    tmp_dir = tempfile.mkdtemp()

    for name in names:
        b = Badge(name)

        path = os.path.join(tmp_dir, "{0}.ps".format(name))
        files.append(path)
        b.generate_PS(path)

    merge_ps_files(output_fname, files)
    shutil.rmtree(tmp_dir)


def pdf_for_users(output_fname, names):
    """
    Generates a PDF with name badges for all users in `usernames`.
    """

    merged_fd, merged_ps_file = tempfile.mkstemp()
    generate_and_merge_ps(merged_ps_file, names)
    ps2pdf(merged_ps_file, output_fname)
    os.close(merged_fd)
    os.remove(merged_ps_file)

def main():

    if len(sys.argv) != 2:
        print 'Usage: badges-gen.py NAMES_FILE'
        print ' Creates a names.pdf containing name labels suitable for use with'
        print ' the badge holders that SR uses (54 x 90mm).'
        exit(1)

    input_file = sys.argv[1]
    names = []
    with open(input_file) as f:
        names = f.readlines()

    if len(names) == 0:
        print "No names found in '{0}'.".format(input_file)
        exit(1)

    names = [n.strip() for n in names]

    pdf_for_users('badges.pdf', names)

if __name__ == '__main__':
    main()
