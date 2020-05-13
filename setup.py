# coding=utf-8

########################################################################################################################
### Do not forget to adjust the following variables to your own plugin.

# The plugin's identifier, has to be unique
plugin_identifier = "pushover"

# The plugin's python package, should be "octoprint_<plugin identifier>", has to be unique
plugin_package = "octoprint_%s" % plugin_identifier

# The plugin's human readable name. Can be overwritten within OctoPrint's internal data via __plugin_name__ in the
# plugin module
plugin_name = "OctoPrint-Pushover"

# The plugin's version. Can be overwritten within OctoPrint's internal data via __plugin_version__ in the plugin module
plugin_version = "0.3.5"

# The plugin's description. Can be overwritten within OctoPrint's internal data via __plugin_description__ in the plugin
# module
plugin_description = "Pushes notifications about finished print jobs trough Pushover."

# The plugin's author. Can be overwritten within OctoPrint's internal data via __plugin_author__ in the plugin module
plugin_author = "Thijs Bekke"

# The plugin's author's mail address.
plugin_author_email = "thijsbekke@gmail.com"

# The plugin's homepage URL. Can be overwritten within OctoPrint's internal data via __plugin_url__ in the plugin module
plugin_url = "https://github.com/thijsbekke/OctoPrint-Pushover"

# The plugin's license. Can be overwritten within OctoPrint's internal data via __plugin_license__ in the plugin module
plugin_license = "AGPLv3"

# Any additional requirements besides OctoPrint should be listed here
plugin_requires = ["pillow"]

### --------------------------------------------------------------------------------------------------------------------
### More advanced options that you usually shouldn't have to touch follow after this point
### --------------------------------------------------------------------------------------------------------------------

# Additional package data to install for this plugin. The subfolders "templates", "static" and "translations" will
# already be installed automatically if they exist.
plugin_additional_data = []

# Any additional python packages you need to install with your plugin that are not contains in <plugin_package>.*
plugin_addtional_packages = []

# Any python packages within <plugin_package>.* you do NOT want to install with your plugin
plugin_ignored_packages = []

# Additional parameters for the call to setuptools.setup. If your plugin wants to register additional entry points,
# define dependency links or other things like that, this is the place to go. Will be merged recursively with the
# default setup parameters as provided by octoprint_setuptools.create_plugin_setup_parameters using
# octoprint.util.dict_merge.
#
# Example:
#     plugin_requires = ["someDependency==dev"]
#     additional_setup_parameters = {"dependency_links": ["https://github.com/someUser/someRepo/archive/master.zip#egg=someDependency-dev"]}
additional_setup_parameters = {}

# README/long description file to use for PyPi uploads. Must be the full absolute path. If the filename ends on
# .md and pypandoc is installed a conversion from Markdown to ReStructured Text will be performed utilizing
# setuptools-markdown as additional setup requirement.
plugin_readme_file = "README.md"

########################################################################################################################

from setuptools import setup

try:
	import octoprint_setuptools
except:
	print("Could not import OctoPrint's setuptools, are you sure you are running that under "
	      "the same python installation that OctoPrint is installed under?")
	import sys
	sys.exit(-1)

setup_parameters = octoprint_setuptools.create_plugin_setup_parameters(
	identifier=plugin_identifier,
	package=plugin_package,
	name=plugin_name,
	version=plugin_version,
	description=plugin_description,
	author=plugin_author,
	mail=plugin_author_email,
	url=plugin_url,
	license=plugin_license,
	requires=plugin_requires,
	additional_packages=plugin_addtional_packages,
	ignored_packages=plugin_ignored_packages,
	additional_data=plugin_additional_data
)

if len(additional_setup_parameters):
	from octoprint.util import dict_merge
	setup_parameters = dict_merge(setup_parameters, additional_setup_parameters)

if plugin_readme_file:
	import os

	here = os.path.abspath(os.path.dirname(__file__))
	plugin_readme_file_path = os.path.join(here, plugin_readme_file)

	# make sure the file exists
	if os.path.isfile(plugin_readme_file_path):
		import codecs

		try:
			with codecs.open(plugin_readme_file_path, "rb", "utf-8") as f:
				plugin_readme_file_content = f.read()

		except Exception as e:
			print("Error reading {} ({}), ignoring long description...".format(plugin_readme_file_path, str(e)))

		else:
			# file exists, let's see if it's markdown or not
			if plugin_readme_file.endswith(".md"):
				print("File with long description apparently is in Markdown format, will convert to RST with pypandoc")
				try:
					import pypandoc
					setup_requires = setup_parameters.get("setup_requires", [])
					setup_parameters.update(dict(
						setup_requires=setup_requires+["setuptools-markdown"],
						long_description_markdown_filename=plugin_readme_file
					))
				except:
					print("No pypandoc installed, not using Markdown file as long description")
					pass
			else:
				print("Using long description from {}...".format(plugin_readme_file_path))
				setup_parameters.update(dict(
					long_description=plugin_readme_file_content
				))

setup(**setup_parameters)
