# External Methods for Plone websites

A random collection of external method scripts for Plone.

External Methods are python scripts that run within the Plone CMS and have full access to Python. They are considerably more powerful than 'Script (Python)' objects in Zope which run in restricted Python. The downside to external methods is that Buildout will delete everything in the Extensions folder where they live every time it's run. There's a solution for this in 'Installation' below.


## Installation

1. In the directory where `buildout.cfg` exists, create a directory called `Extensions`
2. Clone this repository into that `Extensions` directory
3. Edit your `buildout.cfg` file and under the `[client#]` or `[instance]` heading, add:

        zope-conf-additional = extensions ${buildout:directory}/Extensions

You can now run Buildout without worrying about it deleting everything in the Extensions directory.

**Note**: It's probably a good idea to test this before you put any one-of-a-kind files in there and they wind up getting deleted due to a typo or syntax error in your configuration.

**Thanks** to @tkimnguyen for this trick.


### Using a script in Zope/Plone

To use an External Method in Zope/Plone you need to first tell Zope that it exists.

1. Access the Zope Management Interface at `http://localhost:8080/Plone/manage_main`
2. Select `External Method` in the add box in the upper right corner
3. Fill in the values as follows:
    * **Id**: how you want to reference the script in a URL (no spaces)
    * **Title**: the name of the external method as it appears in the ZMI
    * **Module Name**: the name of the file on the file system without the `.py`
    * **Function Name**: the function name in the .py file that should be executed
4. Click Add
5. You can use the `Test` tab to run the external method or you can append the external method's `Id` value to the end of a url


## Requirements

* [Plone API](https://pypi.python.org/pypi/plone.api) which is a simplified way of doing 80% of the common things in Plone. [Read the docs](http://docs.plone.org/develop/index.html#plone-api) for details.


## The scripts

### setup_data_locker.py



## Resources

* [Zope docs on using external methods](http://old.zope.org/Documentation/How-To/ExternalMethods)
* [HTTP Request and Response objects in Plone](http://docs.plone.org/develop/plone/serving/http_request_and_response.html)
* [Using Python scripts with External Methods](https://plone.org/products/ploneformgen/documentation-obsolete/how-to/pass-form-elements-to-external-method)
