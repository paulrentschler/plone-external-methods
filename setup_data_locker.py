# External Method for adding a Web Services Adapter and a Mailer Adapter
# to an existing PloneFormGen Form Folder configured to send data to
# the Data Locker and send failures via the Mailer.
#
# Written by: Paul Rentschler <par117@psu.edu>
# Creation Date: 11 August 2015
#
# Targeted at: Plone 4.3.6
#


from plone import api

from Products.PloneFormGen.content.form import FormFolder
from Products.PloneFormGen.interfaces import \
    IPloneFormGenForm, IPloneFormGenActionAdapter

from collective.webservicespfgadapter.config import extra_data


def setup_data_locker(self):
    """
    Executed on a FormFolder (self) it reconfigures the form to send submissions
    to the Data Locker with an encrypted Mailer fallback option.
    """
    #
    # SETTINGS
    #
    try:
        from setup_data_locker_settings import *
    except:
        DATA_LOCKER_URL = ""
        DELETE_EXISTING_ACTION_ADAPTERS = False 
        FALLBACK_RECIPIENT_EMAIL = ""
        FALLBACK_RECIPIENT_NAME = ""
        FORM_CREATOR = ""
        NOTIFY_ON_FAILURE_EMAILS = ""
        OVERRIDE_EXISTING_SETUP_CHECK = False



    #
    # WHERE THE MAGIC HAPPENS
    # Warning, there be dragons beyond this point!
    #
    if not IPloneFormGenForm.providedBy(self):
        raise Exception("Must be executed on a PloneFormGen Form object")
    object_ids = [obj.id for obj in self.objectValues()]
    if 'data-locker' in object_ids and not OVERRIDE_EXISTING_SETUP_CHECK:
        print "Already setup for the Data Locker: %s" % self.absolute_url()
    else:
        if DELETE_EXISTING_ACTION_ADAPTERS:
            delete_action_adapters(self)
        elif OVERRIDE_EXISTING_SETUP_CHECK:
            delete_action_adapters(self, 'data-locker')
        create_data_locker_adapter(
            self, 
            DATA_LOCKER_URL, 
            NOTIFY_ON_FAILURE_EMAILS
            )
        create_fallback_adapter(
            self, 
            FALLBACK_RECIPIENT_EMAIL, 
            FALLBACK_RECIPIENT_NAME
            )
        if FORM_CREATOR:
            change_form_creator(self, FORM_CREATOR)


def change_form_creator(form, creator):
    """
    Update the form to prepend `creator` as the new first creator of the form
    """
    creators = form.Creators()
    if creator != creators[0]:
        form.setCreators((creator, ) + creators)
        print "First creator now: %s" % creator


def create_data_locker_adapter(form, url, notify):
    """
    Creates a Web Services Adapter in the form (self) and configures it to use
    the Data Locker located at `url`
    """
    data_locker = api.content.create(
        type='FormWebServiceAdapter',
        title='Data Locker',
        url=url,
        extraData=extra_data.keys(),
        failSilently=True,
        notifyOnFailure=notify,
        runDisabledAdapters=True,
        container=form
        )
    print "Data Locker created at: %s" % data_locker.absolute_url()


def create_fallback_adapter(form, recipient_email, recipient_name):
    """
    Creates a Mailer Adapter in the form (self) configured to send an encrypted
    email to the recipient (recipient_email, recipient_name).
    """
    template = \
"""Failed submission to the Data Locker

form_url: <tal:url tal:replace="python:context.aq_parent.absolute_url()" />
form_identifier: <tal:block tal:replace="python:context.aq_parent.id" />
name: <tal:block tal:replace="python:context.aq_parent.Title()" />
owner: <tal:block tal:replace="python:context.aq_parent.Creator()" />
timestamp: 
data: {
<tal:block repeat="field options/wrappedFields | nothing">"<tal:fieldset tal:condition="python:field.aq_parent.id != context.aq_parent.id"><tal:block tal:replace="python:field.aq_parent.Title()" /> / </tal:fieldset><tal:field tal:content="field/fgField/widget/label" />": "<tal:value tal:content="structure python:field.htmlValue(request)" />",</tal:block>
}
"""

    mailer = api.content.create(
        type='FormMailerAdapter',
        title='Failure Mailer',
        recipient_name=recipient_name,
        recipient_email=recipient_email,
        showAll=True,
        includeEmpties=True,
        body_pt=template,
        body_type='plain',
        gpg_keyid=recipient_email,
        container=form
        )
    mailer.msg_subject = 'Form Submission Failure'
    print "Fallback Mailer created at: %s" % mailer.absolute_url()
    active_adapters = set(list(form.actionAdapter))
    if mailer.id in active_adapters:
        active_adapters.remove(mailer.id)
    form.actionAdapter = list(active_adapters)
    print "Fallback Mailer deactivated"


def delete_action_adapters(form, id=None):
    """
    Removes all the action adapters for the form (self) or just the one
    specified by `id`
    """
    for obj in form.objectValues():
        if IPloneFormGenActionAdapter.providedBy(obj):
            if id == None or id == obj.id:
                api.content.delete(obj=obj)
                print "Deleting existing adapter at: %s" % obj.absolute_url()

