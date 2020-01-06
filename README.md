# ModifyEXIF
Modify your photos EXIF, if you hate the wrong date.

# General Idea
I often get pictures with wrong date when I transfer my data between my phones, which is so annoying. Therefore, I make this thing to satisfy my strange interest.  
Fortunately, we can get the correct date from picture file's name or its creation date. So I use this python script to read the origin date from picture itself (from filename or creation time, depends on which is earlier) and make it every date of the picture file.

# Requirements
+ pyexiv2  
+ os,re,time  
+ win32file  
+ pywintypes  

# How to use
1.Change `pic_dir` in `if __name__ == "__main__":`.  
2.Then just `python test.py`.

# Thanks To
`changeFileCreateTime()` is googled from the Internet, but I forget where and who I got this from.  
~~It's a bad habit. Remember to record everything next time.~~
