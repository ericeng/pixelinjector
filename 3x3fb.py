#!/usr/bin/python
#
# Inserts a Facebook Pixel and other commands into each HTML page in a directory structur
#
# Author: G. Eric Engstrom
# Copyright (C) 3x3 Insights 2020
# All Rights Reserved
#
# take the file from command line
# rename the file to *.bak
# create a new file that is the original name
#
# add the Facebook section from the company.inf files
#

# command line options
# ev.fb.py original.html <options> company.inf 

import os
import sys
import getopt
import copy
import glob

global html_only_F
global php_only_F
global no_3x3_backups_F
global no_dirs_F
global fb_inf_F
global input_file_F
global output_file_F
global sub_tag_F
global head_tag_G

def file_insert( filename_P, optional_outputfilename_P ) :
  global no_3x3_backups_F
  global fb_inf_F
  global sub_tag_F
  global head_tag_G
  global program_name_G

  if len( sub_tag_F ) > 0 :
    head_tag_G = sub_tag_F

  # rename original to *.3x3
  filename_3x3 = filename_P + ".3x3"
  if not os.path.isfile( filename_3x3 ) :
    os.rename( filename_P, filename_3x3 )

  else :
    print( "Log: Couldn't create fresh", filename_3x3 )

  file_input = open( filename_3x3, 'r' ) 

  if len( optional_outputfilename_P ) > 0 :
    # make the optional_outputfilename_P
    file_output = open( optional_outputfilename_P, 'w' )
    print( "Log: Adding Facebook Pixel file to", filename_P, "and writing it to", optional_outputfilename_P )
 
  else :
    # make new one the old name
    file_output = open( filename_P, 'w' )
    print( "Log: Adding Facebook Pixel file to", filename_P )

  head_found = 0

  
  while True : 
    line = file_input.readline() 

    # if line is empty 
    # end of file has been reached 
    if not line: 
      if head_found == 0 :
        print( "Error: No", head_tag_G,"tag found to insert company.inf file before\n" )

      break

    if head_found == 0 :
      # check for the end of the <head> section to start inserting company.inf file
      if head_tag_G in line :
        index = line.find( head_tag_G )
        prefix = head_tag_G.find( '</' )

        if prefix != -1 :
          if index > 0 :
            line_head_tag_prefix = line[ 0 : index ]
            file_output.write( line_head_tag_prefix )
            line = line[ index : -1 ]
            line += '\n'

        else :
          index = index + len( head_tag_G )    # capture the text preceding the leading tag
          line_head_tag_prefix = line[ 0 : index ]
          file_output.write( line_head_tag_prefix )
          line = line[ index : -1 ]
          line += '\n'

        header_common = "<!-- Facebook Pixel Configuration inserted by " + program_name_G + " for " + fb_inf_F
        header_beg = "\n" + header_common + " { -->"
        header_end = header_common + " } -->\n"

        file_output.write( header_beg ) 
        file_inf = open( fb_inf_F, 'r' )

        while True :
          line_info = file_inf.readline()

          if not line_info :
            file_inf.close()
            break

          else :
            file_output.write( line_info )
            
        file_output.write( header_end ) 
        head_found = 1
                    
    if len( line ) > 0 :
      file_output.write( line )
  
  file_input.close() 
  file_output.close()

  if no_3x3_backups_F == 1 :
    os.remove( filename_3x3 )
    
def file_insert_dir_ext( file_ext_P ) :
  global no_dirs_F

  for file in glob.glob( file_ext_P ) :
    file_insert( file, "" )

def file_insert_dir_ext_html() :
  file_insert_dir_ext( "*.html" )
  file_insert_dir_ext( "*.htm" )

def file_insert_dir() :
  global html_only_F
  global php_only_F

  if html_only_F == 1 :
    file_insert_dir_ext_html()

  else:
    if php_only_F == 0 :
      file_insert_dir_ext_html()

    file_insert_dir_ext( "*.php" )

def print_log_cwd() :
  print( "Log: Processing files in", os.getcwd() )

def file_insert_dir_sub() :
  list_subfolders = [ f.name for f in os.scandir( os.getcwd() ) if f.is_dir() ]

  for dir_name in list_subfolders :
    os.chdir( dir_name )

    file_insert_dir_sub()
    print_log_cwd()
    file_insert_dir()

    os.chdir( ".." )

def main( argv ) :
  global html_only_F
  global php_only_F
  global no_3x3_backups_F
  global no_dirs_F
  global fb_inf_F
  global input_file_F
  global output_file_F
  global sub_tag_F
  global head_tag_G
  global program_name_G

  program_name_G = copy.deepcopy( sys.argv[ 0 ] )

  try :
    opts, args = getopt.getopt( argv, "?hpbf:i:o:s:", [ "fbinf=", "ifile=", "ofile=", "subtag=" ] )

  except getopt.GetoptError :
    print( program_name_G, '-? -h -p -b -f <fbinf> -i <inputfile> -o <outputfile> -s <substitute tag>' )
    sys.exit( 2 )

  for opt, arg in opts :
    if opt == '-?' :
      print( program_name_G, '\n\t-? help\n\t-f or --fbinf <company specific *.inf>\n\t-h html files only\n\t-p php files only\n\t-b no *.3x3 back up files\n\t-d don\'t descend into directories\n\t-i or --ifile <only inputfile> all html and php files are the default\n\t-o or --ofile <only outputfile> same name as input is the default\n\t-s or --subtag <substitute section tag> </head> is the default so the insertion happens at the end of the section' )
      sys.exit()

    elif opt == '-h' :
      html_only_F = 1

      if php_only_F == 1 :
        php_only_F = 0
        print( "Log: HTML only specified after PHP only.  Processing only HTML." )

    elif opt == '-p' :
      php_only_F = 1

      if html_only_F == 1 :
        html_only_F = 0
        print( "Log: PHP only specified after HTML only.  Processing only PHP." )

    elif opt == '-b' :
      no_3x3_backups_F = 1

    elif opt == '-d' :
      no_dirs_F = 1

    elif opt in ( "-f", "--fbinf" ) :
      fb_inf_F = arg

    elif opt in ( "-i", "--ifile" ) :
      input_file_F = arg

    elif opt in ( "-o", "--ofile" ) :
      output_file_F = arg

    elif opt in ( "-s", "--subtag" ) :
      sub_tag_F = arg

  print( "\n" )
  print( program_name_G )
  print( "Facebook Pixel Injection Tool" )
  print( "Copyright 3x3 (C) 2020, All Rights Reserved\n\n\t-? for directions.\n" )

  if len( fb_inf_F ) == 0 :
    print( "Error: Facebook Pixel file must be specified." )
    sys.exit( 2 )

  elif not os.path.isfile( fb_inf_F ) :
    print( "Error: Facebook Pixel file", fb_inf_F, "doesn't exist." )
    sys.exit( 2 )

  if len( input_file_F ) > 0 :
    if os.path.isfile( input_file_F ) :
      file_insert( input_file_F, output_file_F )

    else :
      print( "Error: Specified input file", input_file_F, "doesn't exist." )
      sys.exit( 2 )

  elif len( output_file_F ) > 0 :
    print( "Error: Can't specify custom output file name without custom input file name." )
    sys.exit( 2 )

  else :
    if no_dirs_F == 0 :
      fb_inf_F = os.getcwd() + "\\" + fb_inf_F
      file_insert_dir_sub()

    print_log_cwd()
    file_insert_dir()

  print( "\nComplete." )

if __name__ == "__main__" :
  global html_only_F
  global php_only_F
  global no_3x3_backups_F
  global no_dirs_F
  global fb_inf_F
  global input_file_F
  global output_file_F
  global sub_tag_F
  global head_tag_G

  html_only_F = 0
  php_only_F = 0
  no_3x3_backups_F = 0
  no_dirs_F = 0
  fb_inf_F = ''
  input_file_F = ''
  output_file_F = ''
  sub_tag_F = ''
  head_tag_G = '</head>'

  main( sys.argv[ 1 : ] )

