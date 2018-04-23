from fuse import FUSE

class FileSystem():
	def __init__(self):
		pass

if __name__ == '__main__':
	fuse = FUSE(FileSystem(), 'mnt', foreground=True)
