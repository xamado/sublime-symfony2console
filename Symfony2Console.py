import sublime, sublime_plugin
import os
import os.path
import subprocess
import threading

class SymfonyConsoleExecuteAsync(threading.Thread):
	def __init__(self, directory, command):
		self.directory = directory
		self.command = command
		self.result = ''

		threading.Thread.__init__(self)

	def run(self):
		os.chdir(self.directory)
		command = "php app/console --no-ansi -v" + " " + self.command

		child = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, cwd=self.directory)

		while True:
			out = child.stdout.read(1)
			if out == '' and child.poll() != None:
				break
			if out != '':
				self.result += out

		self.result = 'fdafd'


class SymfonyConsoleBase(sublime_plugin.WindowCommand):
	project_directory = ''

	def getProjectFolder(self):
		if self.window:
			folders = self.window.folders()
	    	for folder in folders:
	    		return folder

	def output(self, value):
		self.multi_line_output(value)

	def multi_line_output(self, value, panel_name='Symfony2Console'):
		# Create the output Panel
		panel = self.window.get_output_panel(panel_name)
		panel.set_read_only(False)
		panel.set_syntax_file('Packages/Text/Plain text.tmLanguage')
		edit = panel.begin_edit()
		panel.insert(edit, panel.size(), value)
		panel.end_edit(edit)
		panel.set_read_only(True)
		self.window.run_command("show_panel", {"panel": "output." + panel_name})



class SymfonyConsoleCommand(SymfonyConsoleBase):

	def executeCommand(self, command):
		directory = self.getProjectFolder()

		thread = SymfonyConsoleExecuteAsync(directory, command)
		thread.start()
		self.thread = thread

		self.waitForThread(0, 1)

	def waitForThread(self, i, dir):
		if len(self.thread.result) > 0:
			self.output(self.thread.result)

		if not self.thread.is_alive():
			self.window.active_view().erase_status('symfonyconsole')
			return

		# This animates a little activity indicator in the status area  
		before = i % 8  
		after = (7) - before  
		if not after:  
		    dir = -1  
		if not before:  
		    dir = 1  
		i += dir  
		self.window.active_view().set_status('symfonyconsole', self.thread.command + ' [%s=%s]' % \
			(' ' * before, ' ' * after))  

		# execute again in a while
		sublime.set_timeout(lambda: self.waitForThread(i, dir), 100)
			

 
class SymfonyConsoleSimpleCommand(SymfonyConsoleCommand):
	def run(self, command):
		self.executeCommand(command)



class SymfonyConsoleGenerateBundleCommand(SymfonyConsoleCommand):
	namespace = ''
	directory = ''
	format = ''

	def onNamespaceEntered(self, inputString):
		self.namespace = inputString
		self.askForParameters()

	def onDirectoryEntered(self, inputString):
		self.directory = inputString
		self.askForParameters()

	def onFormatEntered(self, inputString):
		self.format = inputString
		self.askForParameters()

	def askForParameters(self):
		if self.namespace == '':
			self.window.show_input_panel("Enter the bundle namespace", "Acme/BlogBundle", self.onNamespaceEntered, None, None)
		elif self.directory == '':
			self.window.show_input_panel("Enter the directory", self.getProjectFolder() + "/src", self.onDirectoryEntered, None, None)
		elif self.format == '':
			self.window.show_input_panel("Configuration format (yml, xml, php or annotation)", "yml", self.onFormatEntered, None, None)
		else:
			cmd = self.command
			cmd += ' --namespace=' + self.namespace
			cmd += ' --dir=' + self.directory
			cmd += ' --format=' + self.format
			self.executeCommand(cmd)

	def run(self, command):
		self.namespace = ''
		self.directory = ''
		self.format = ''
		self.command = command

		self.askForParameters()
